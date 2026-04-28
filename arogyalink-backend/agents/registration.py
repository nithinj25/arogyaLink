"""
IVR registration agent — collects family details over a voice call.

Flow:
  1. Collect primary contact name
  2. Collect village + district
  3. Collect family members (iterative — Gemini decides when list is complete)
  4. Confirm summary, save to Firestore

Gemini drives the conversation and returns structured JSON at each turn.
When registration is complete it returns {"done": true, "family": {...}}.
"""

import json
import re
import uuid
from services.gemini import chat
from firebase.client import update_call_field, get_call_record, create_family
from utils.phone import to_e164
from utils.logger import get_logger

logger = get_logger(__name__)

MAX_REG_TURNS = 12

_LANG_INSTRUCTION = {
    "kn-IN": "Respond in English (Kannada TTS unavailable).",
    "hi-IN": "Respond in Hindi (हिंदी में जवाब दें).",
    "te-IN": "Respond in English (Telugu TTS unavailable).",
    "en-IN": "Respond in English.",
}

_SYSTEM_PROMPT_TEMPLATE = """You are ArogyaLink's registration assistant. You are on a phone call helping someone register their family for emergency services.

{lang_instruction}

Your job is to collect:
1. Primary contact's full name
2. Village name and district (their home address)
3. Family members — for EACH member: name, age, gender (M/F), relationship to caller, any medical conditions

RESPONSE FORMAT — Always reply with ONLY raw JSON:
{{
  "response": "<spoken reply — 1-2 short sentences — read aloud>",
  "collected": {{
    "primary_name": "<name or null>",
    "village": "<village or null>",
    "district": "<district or null>",
    "state": "<state or null>",
    "members": [
      {{
        "name": "<name>",
        "age": <number>,
        "gender": "M|F",
        "relationship": "<self|spouse|father|mother|son|daughter|sibling|other>",
        "conditions": ["<condition1>", ...]
      }}
    ]
  }},
  "done": false
}}

Set "done": true ONLY when you have: primary_name, village, district, AND at least one family member.

RULES:
- Ask ONE question at a time
- After getting the first member, ask "Is there anyone else in your family I should add? Or say no to finish."
- Keep responses short — this is spoken aloud
- Be warm and reassuring
- If they say "no more members" or "that's all", set done=true with what you have

EXAMPLES:
User: "hello" / start of registration
→ {{"response": "Welcome! I'll register your family for faster emergency help. What is your full name?", "collected": {{"primary_name": null, "village": null, "district": null, "state": null, "members": []}}, "done": false}}

User: "My name is Suresh Kumar"
→ {{"response": "Hello Suresh! What is your village name and district?", "collected": {{"primary_name": "Suresh Kumar", "village": null, "district": null, "state": null, "members": []}}, "done": false}}

User: "Hosahalli village, Kolar district, Karnataka"
→ {{"response": "Great. Now let's add your family members. Starting with yourself — how old are you?", "collected": {{"primary_name": "Suresh Kumar", "village": "Hosahalli", "district": "Kolar", "state": "Karnataka", "members": []}}, "done": false}}

User: "I am 45"
→ {{"response": "Do you have any medical conditions like diabetes or blood pressure?", "collected": {{"primary_name": "Suresh Kumar", "village": "Hosahalli", "district": "Kolar", "state": "Karnataka", "members": [{{"name": "Suresh Kumar", "age": 45, "gender": "M", "relationship": "self", "conditions": []}}]}}, "done": false}}

User: "yes I have diabetes"
→ {{"response": "Noted. Is there anyone else in your family I should add? Or say no to finish.", "collected": {{"members": [{{"name": "Suresh Kumar", "age": 45, "gender": "M", "relationship": "self", "conditions": ["diabetes"]}}]}}, "done": false}}

User: "no that's all"
→ {{"response": "Your family has been registered. You will receive faster, personalised help when you call next time.", "collected": {{}}, "done": true}}"""


def _parse_reg_response(raw: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip(), flags=re.MULTILINE)
    text = re.sub(r"\n?```\s*$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return {"response": text if len(text) < 400 else None, "collected": {}, "done": False}


def _merge_collected(existing: dict, new: dict) -> dict:
    """Deep-merge collected fields — never overwrite a good value with null."""
    merged = dict(existing)
    for k, v in new.items():
        if k == "members" and isinstance(v, list) and v:
            # Assign stable IDs to any member that doesn't have one
            for member in v:
                if not member.get("id"):
                    member["id"] = str(uuid.uuid4())[:8]
            merged["members"] = v
        elif v not in (None, "", []):
            merged[k] = v
    return merged


async def run_registration_turn(
    case_id: str,
    phone: str,
    lang_code: str,
    user_input: str,
) -> dict:
    """
    Process one registration conversation turn.
    Returns:
        {"done": False, "response": "next question"}
        {"done": True,  "response": "farewell", "family": {...saved family dict...}}
    """
    record = get_call_record(case_id) or {}
    history: list[dict] = record.get("reg_history", [])
    collected: dict = record.get("reg_collected", {})
    if "members" not in collected:
        collected["members"] = []
    turn_count = len([m for m in history if m["role"] == "user"])

    history.append({"role": "user", "content": user_input})
    logger.info(f"[{case_id}/reg] Turn {turn_count + 1} | '{user_input[:60]}'")

    if turn_count >= MAX_REG_TURNS:
        # Save whatever we have
        return await _save_and_finish(case_id, phone, lang_code, history, collected)

    lang_instr = _LANG_INSTRUCTION.get(lang_code, _LANG_INSTRUCTION["en-IN"])
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(lang_instruction=lang_instr)

    try:
        raw = await chat(history, system_prompt, max_tokens=512)
        logger.info(f"[{case_id}/reg] Gemini: {raw[:120]}")

        parsed = _parse_reg_response(raw)
        collected = _merge_collected(collected, parsed.get("collected", {}))

        update_call_field(case_id, "reg_history", history)
        update_call_field(case_id, "reg_collected", collected)

        response_text = parsed.get("response") or "Could you repeat that?"
        history.append({"role": "assistant", "content": response_text})
        update_call_field(case_id, "reg_history", history)

        if parsed.get("done") is True and collected.get("primary_name"):
            return await _save_and_finish(case_id, phone, lang_code, history, collected,
                                          farewell=response_text)

        return {"done": False, "response": response_text}

    except Exception as e:
        logger.error(f"[{case_id}/reg] Error: {e}", exc_info=True)
        fallback = "Can you please repeat that?"
        history.append({"role": "assistant", "content": fallback})
        update_call_field(case_id, "reg_history", history)
        return {"done": False, "response": fallback}


async def _save_and_finish(
    case_id: str,
    phone: str,
    lang_code: str,
    history: list,
    collected: dict,
    farewell: str | None = None,
) -> dict:
    family_data = {
        "phone": phone,
        "primary_name": collected.get("primary_name") or "Unknown",
        "address": collected.get("address") or "",
        "village": collected.get("village") or "",
        "district": collected.get("district") or "",
        "state": collected.get("state") or "",
        "language": lang_code,
        "members": collected.get("members") or [],
    }
    try:
        saved = create_family(family_data)
        logger.info(f"[{case_id}/reg] Family saved for {phone}")
    except Exception as e:
        logger.error(f"[{case_id}/reg] Failed to save family: {e}")
        saved = family_data

    if not farewell:
        farewell = "Your family has been registered. Thank you for using ArogyaLink."

    return {"done": True, "response": farewell, "family": saved}
