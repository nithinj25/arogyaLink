"""
Conversation agent — drives the multi-turn emergency intake dialogue.

When a registered family calls, Gemini receives their full profile and can:
  • Greet them by name
  • Match mentioned family members to the stored profile
  • Reference known medical conditions
  • Skip asking for address (already stored)

For unregistered callers the standard emergency flow applies and location
is collected during the conversation.
"""

import json
import re
from services.gemini import chat
from firebase.client import update_call_field, get_call_record
from utils.logger import get_logger

logger = get_logger(__name__)

MAX_TURNS = 7
MIN_TURNS_BEFORE_DONE = 2   # code gate — overrides Gemini

# Polly.Aditi supports en-IN and hi-IN only.
_LANG_INSTRUCTION = {
    "kn-IN": (
        "You MUST reply in English only — Kannada TTS is unavailable on this system. "
        "You will still understand the patient even if they speak Kannada."
    ),
    "hi-IN": "Respond in Hindi (हिंदी में जवाब दें).",
    "te-IN": (
        "You MUST reply in English only — Telugu TTS is unavailable on this system. "
        "You will still understand the patient even if they speak Telugu."
    ),
    "en-IN": "Respond in English.",
}

# ── System prompt template ─────────────────────────────────────────────────────

_SYSTEM_TEMPLATE = """You are ArogyaLink — an emergency medical dispatcher for rural India. You are on a live phone call.

LANGUAGE: {lang_instruction}

━━━ CALLER CONTEXT ━━━
{caller_context}

━━━ RESPONSE FORMAT ━━━
Always reply with ONLY raw JSON — no markdown, no prose, nothing else:
{{
  "response": "<spoken reply — 1-2 SHORT sentences — read aloud on a phone>",
  "extracted": {{
    "patient_name":      "<name of patient if known, else null>",
    "patient_member_id": "<family member id from profile if matched, else null>",
    "symptom":           "<specific complaint or injury, else null>",
    "severity":          "<consciousness / breathing / bleeding / pain level, else null>",
    "patient_profile":   "<age group, gender, relationship, known conditions, else null>",
    "location":          "<address or village name if given or already known, else null>"
  }},
  "done": false,
  "phase": "identify|assess|done"
}}

━━━ DONE CONDITIONS ━━━
Set "done": true ONLY when:
  • symptom AND severity are both non-null
  • AND at least {min_turns} user turns have occurred in this conversation
FAST-TRACK EXCEPTION — set done=true after just 1 turn if ALL of these are true:
  • Situation is OBVIOUSLY life-threatening (not breathing / cardiac arrest /
    major trauma / uncontrolled bleeding / drowning / severe burns)
  • AND you have confirmed severity in that same turn

NEVER set done after: a greeting alone, a single vague word, or without knowing severity.

━━━ CONVERSATION PHASES ━━━
IDENTIFY (registered callers only):
  → Greet by first name, ask who needs help today (self or which family member)
  → When named, match to profile and load their known conditions into context

ASSESS:
  → ONE question per turn — most critical gap first
  → Symptom → Severity → (Location if unregistered) → done
  → NEVER ask for age as a standalone question — capture it only if volunteered
  → For registered callers: reference known conditions where relevant
  → {location_rule}

DONE → set done=true and the response is a brief reassurance ("Help is on the way")

━━━ EDGE CASES ━━━
• Greeting only ("hello", "hi", silence)
  → Ask what the emergency is. Never set done.

• Panic / distress (saying "please help", repeating words, frantic)
  → Lead with: "I understand, take a breath — I'm here." then ONE question

• Caller in shock / can't form sentences / very short answers
  → Switch to yes/no questions: "Is the person breathing? Just say yes or no."

• Child calling
  → "Can you get a grown-up? Or tell me quickly — what happened?"

• Multiple casualties
  → "How many people need help?" — capture count in patient_profile

• Caller IS the patient
  → Set patient_name to "caller", adjust questions accordingly

• Family member mentioned but not in registered profile
  → Use the name/relation given, don't force a match

• Non-emergency / wrong number / test call
  → "Is this a medical emergency? If not, please call back when you need help."

• Caller switches language mid-call
  → Continue in whatever language they're now using

• Chronic / known condition mentioned
  → For registered callers reference the profile condition; for unregistered ask for more detail

• Elderly patient (stated or inferred)
  → Flag as high risk; confirm severity urgently

• Caller gives very detailed answer covering multiple missing fields in one turn
  → Extract ALL fields from that single answer; move straight to done if sufficient

━━━ EXAMPLES ━━━
{examples}"""

# ── Examples ──────────────────────────────────────────────────────────────────

_EXAMPLES_REGISTERED = """\
[Registered caller: Ravi Kumar | Members: Ram (72M, heart disease, Warfarin) · Priya (42F)]

Turn 1 — Greeting:
User: "hello"
→ {{"response": "Hi Ravi! Who needs help today — is it for you or a family member?", "extracted": {{"patient_name": null, "patient_member_id": null, "symptom": null, "severity": null, "patient_profile": null, "location": null}}, "done": false, "phase": "identify"}}

Turn 2 — Member identified:
User: "my father"
→ {{"response": "Is that Ram? What's happening with him?", "extracted": {{"patient_name": "Ram", "patient_member_id": "RAM_ID", "symptom": null, "severity": null, "patient_profile": "72-year-old male, heart disease, on Warfarin, Blood O+", "location": "REGISTERED_ADDRESS"}}, "done": false, "phase": "assess"}}

Turn 3 — Symptom given with life-threatening detail:
User: "he has chest pain and is sweating a lot, he looks pale"
→ {{"response": "I understand. Since Ram has a heart condition, this is serious. Is he conscious and able to speak to you right now?", "extracted": {{"symptom": "chest pain, sweating, pallor — possible cardiac event", "severity": null, "patient_profile": "72-year-old male, heart disease, on Warfarin"}}, "done": false, "phase": "assess"}}

Turn 4 — Severity confirmed:
User: "yes he is conscious but in severe pain"
→ {{"response": "Help is being sent immediately. Keep Ram seated and calm. Do not give him anything to eat or drink.", "extracted": {{"symptom": "chest pain, sweating, pallor — likely cardiac", "severity": "conscious, severe pain, pallor", "patient_profile": "72-year-old male, heart disease, on Warfarin, O+"}}, "done": true, "phase": "done"}}

Panic example:
User: "please help please help he is dying"
→ {{"response": "I understand, take a breath — I'm here. Tell me: is he breathing right now?", "extracted": {{"symptom": null, "severity": null, "patient_profile": null}}, "done": false, "phase": "assess"}}"""

_EXAMPLES_UNREGISTERED = """\
[Unregistered caller — no prior profile]

Turn 1 — Greeting only:
User: "hello"
→ {{"response": "Hello, this is ArogyaLink. What is the emergency? Please describe what happened.", "extracted": {{"patient_name": null, "symptom": null, "severity": null, "patient_profile": null, "location": null}}, "done": false, "phase": "assess"}}

Turn 1 — Immediate emergency:
User: "my wife is having chest pain and can't breathe"
→ {{"response": "I understand. Is she conscious and able to speak right now?", "extracted": {{"symptom": "chest pain, difficulty breathing", "severity": null, "patient_profile": "adult female (wife)"}}, "done": false, "phase": "assess"}}

Turn 2 — Severity confirmed:
User: "yes she is conscious but very uncomfortable"
→ {{"response": "Okay. What is your village or address so we can send help?", "extracted": {{"symptom": "chest pain, breathing difficulty", "severity": "conscious, severe discomfort", "patient_profile": "adult female (wife)"}}, "done": false, "phase": "assess"}}

Turn 3 — Location given:
User: "Hosahalli village near Kolar"
→ {{"response": "Help is being sent to Hosahalli, Kolar. Keep her seated upright and calm.", "extracted": {{"symptom": "chest pain, difficulty breathing", "severity": "conscious, severe discomfort", "patient_profile": "adult female (wife)", "location": "Hosahalli village, Kolar"}}, "done": true, "phase": "done"}}

Child caller:
User: "my mummy fainted"
→ {{"response": "Okay. Can you get an adult to help? And is your mummy breathing?", "extracted": {{"symptom": "fainted / collapsed", "severity": null, "patient_profile": "adult female (mother)"}}, "done": false, "phase": "assess"}}

Yes/no mode (caller can't describe):
User: "I don't know I don't know"
→ {{"response": "That's okay. Just answer yes or no: is the person breathing right now?", "extracted": {{"symptom": null, "severity": null}}, "done": false, "phase": "assess"}}"""


# ── Context builder ────────────────────────────────────────────────────────────

def _build_caller_context(family: dict | None) -> tuple[str, str]:
    """Returns (caller_context_block, location_rule) for the system prompt."""
    if not family:
        return (
            "CALLER STATUS: Unregistered — no prior profile on file.",
            "Location is unknown. You MUST ask for village or address "
            "before setting done=true. Add to extracted.location.",
        )

    members = family.get("members", [])
    lines = []
    for m in members:
        conds = ", ".join(m.get("conditions") or []) or "none"
        allerg = ", ".join(m.get("allergies") or []) or "none"
        blood = m.get("blood_group") or "unknown"
        meds = ", ".join(m.get("medications") or []) or "none"
        g = "M" if m.get("gender") == "M" else ("F" if m.get("gender") == "F" else "")
        lines.append(
            f"  • {m['name']} ({m.get('relationship','')}, {m.get('age','')}{''+g}) "
            f"| Conditions: {conds} | Allergies: {allerg} | Blood: {blood} "
            f"| Meds: {meds} [id:{m.get('id','')}]"
        )

    name = family.get("primary_name", "the caller")
    first = name.split()[0]
    addr_parts = [family.get("address"), family.get("village"),
                  family.get("district"), family.get("state")]
    full_addr = ", ".join(p for p in addr_parts if p) or "not provided"
    members_text = "\n".join(lines) if lines else "  • (none registered)"

    context = (
        f"CALLER STATUS: Registered ✓\n"
        f"Name: {name} | Phone: {family.get('phone','')}\n"
        f"Address on file: {full_addr}\n"
        f"Language preference: {family.get('language','en-IN')}\n\n"
        f"Family members:\n{members_text}\n\n"
        f"GREETING: Start with 'Hi {first}!' — then ask who needs help today.\n"
        f"MATCHING: When a family member is mentioned by name or relation, "
        f"match them to the list above and use their profile.\n"
        f"CONDITIONS: Proactively reference known conditions when relevant."
    )
    location_rule = (
        f"Address is already registered: '{full_addr}'. "
        f"Do NOT ask for address — set extracted.location to this address automatically. "
        f"Only ask if caller explicitly says they are away from home."
    )
    return context, location_rule


def _get_system_prompt(lang_code: str, family: dict | None) -> str:
    lang_instr = _LANG_INSTRUCTION.get(lang_code, _LANG_INSTRUCTION["en-IN"])
    caller_ctx, location_rule = _build_caller_context(family)
    examples = _EXAMPLES_REGISTERED if family else _EXAMPLES_UNREGISTERED
    return _SYSTEM_TEMPLATE.format(
        lang_instruction=lang_instr,
        caller_context=caller_ctx,
        location_rule=location_rule,
        min_turns=MIN_TURNS_BEFORE_DONE,
        examples=examples,
    )


# ── JSON parser ────────────────────────────────────────────────────────────────

def _parse_response(raw: str) -> dict:
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

    logger.warning(f"Non-JSON from Gemini: {text[:120]}")
    return {
        "response": text if 5 < len(text) < 400 else None,
        "extracted": {},
        "done": False,
        "phase": "assess",
    }


# ── Fallbacks ──────────────────────────────────────────────────────────────────

_FALLBACKS = {
    0: {
        "en-IN": "I'm here to help. What is the emergency? Please describe what happened.",
        "hi-IN": "मैं मदद के लिए हूँ। कृपया बताएं क्या हुआ।",
        "kn-IN": "I'm here to help. What is the emergency? Please describe what happened.",
        "te-IN": "I'm here to help. What is the emergency? Please describe what happened.",
    },
    1: {
        "en-IN": "I understand. Is the patient conscious and breathing normally?",
        "hi-IN": "क्या मरीज़ होश में है और सांस ले रहे हैं?",
        "kn-IN": "Is the patient conscious and breathing normally?",
        "te-IN": "Is the patient conscious and breathing normally?",
    },
    2: {
        "en-IN": "What is your village or nearest town so we can send help?",
        "hi-IN": "आपका गाँव या नज़दीकी शहर कौनसा है ताकि हम मदद भेज सकें?",
        "kn-IN": "What is your village or nearest town so we can send help?",
        "te-IN": "What is your village or nearest town so we can send help?",
    },
}

_NEXT_Q = {
    "symptom": {
        "en-IN": "What is the main problem — please describe the symptom or injury.",
        "hi-IN": "मुख्य समस्या क्या है — लक्षण या चोट बताएं।",
        "kn-IN": "What is the main problem? Please describe what happened.",
        "te-IN": "What is the main problem? Please describe what happened.",
    },
    "severity": {
        "en-IN": "Is the patient conscious and breathing normally right now?",
        "hi-IN": "क्या मरीज़ अभी होश में है और सांस ठीक से ले रहे हैं?",
        "kn-IN": "Is the patient conscious and breathing right now?",
        "te-IN": "Is the patient conscious and breathing right now?",
    },
    "location": {
        "en-IN": "What is your village or address so we can send help?",
        "hi-IN": "आपका गाँव या पता क्या है ताकि हम मदद भेज सकें?",
        "kn-IN": "What is your village or address so we can send help?",
        "te-IN": "What is your village or address so we can send help?",
    },
}

_LIFE_THREATENING = [
    "not breathing", "no breathing", "stopped breathing", "can't breathe",
    "cardiac arrest", "heart attack", "no pulse", "unconscious", "not waking",
    "not responding", "severe bleeding", "heavy bleeding", "drowning",
    "choking", "major trauma", "severe burns",
    "सांस नहीं", "बेहोश", "दिल का दौरा",
    "ಉಸಿರಾಡುತ್ತಿಲ್ಲ", "ಪ್ರಜ್ಞೆ ಇಲ್ಲ",
]


def _is_life_threatening(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in _LIFE_THREATENING)


_SYMPTOM_KW = [
    "pain", "chest", "heart", "breath", "breathing", "fever", "accident",
    "fall", "fell", "vomit", "headache", "seizure", "faint", "unconscious",
    "bleed", "burn", "injury", "hurt", "dard", "bukhaar", "chot", "dil",
    "dard", "takleef", "bimaar", "emergency", "help", "problem",
]
_SEVERITY_KW = [
    "yes", "no", "conscious", "breathing", "severe", "critical", "mild",
    "okay", "fine", "bad", "worse", "awake", "haan", "nahi", "theek",
    "nahi", "ho", "hai",
]


def _rule_extract(user_input: str, extracted: dict, turn: int) -> dict:
    """Keyword-based extraction used as fallback when Gemini is unavailable."""
    text = user_input.lower().strip()
    if not text:
        return extracted

    # Turn 1: anything said is the symptom description
    if turn == 0 and not extracted.get("symptom"):
        extracted["symptom"] = user_input
        return extracted

    # If symptom set but no severity — treat this turn as severity answer
    if extracted.get("symptom") and not extracted.get("severity"):
        extracted["severity"] = user_input
        return extracted

    # If symptom + severity set but no location — treat this turn as location
    if extracted.get("symptom") and extracted.get("severity") and not extracted.get("location"):
        if len(text) > 1:
            extracted["location"] = user_input
        return extracted

    # First turn with symptom keywords
    if not extracted.get("symptom"):
        for kw in _SYMPTOM_KW:
            if kw in text:
                extracted["symptom"] = user_input
                break

    return extracted


_ALL_COLLECTED = {
    "en-IN": "Thank you. Help is being arranged for you right now. Please stay calm.",
    "hi-IN": "धन्यवाद। आपके लिए अभी मदद भेजी जा रही है। शांत रहें।",
    "te-IN": "Thank you. Help is being arranged for you right now. Please stay calm.",
}


def _next_question(extracted: dict, lang_code: str, family: dict | None, turn: int) -> str:
    if not extracted.get("symptom"):
        return _NEXT_Q["symptom"].get(lang_code, _NEXT_Q["symptom"]["en-IN"])
    if not extracted.get("severity"):
        return _NEXT_Q["severity"].get(lang_code, _NEXT_Q["severity"]["en-IN"])
    if not extracted.get("location") and not family:
        return _NEXT_Q["location"].get(lang_code, _NEXT_Q["location"]["en-IN"])
    # All fields collected — should not normally reach here due to force_done
    return _ALL_COLLECTED.get(lang_code, _ALL_COLLECTED["en-IN"])


# ── Public API ─────────────────────────────────────────────────────────────────

def build_summary(history: list, extracted: dict) -> str:
    symptom = extracted.get("symptom") or "not specified"
    severity = extracted.get("severity") or "unknown"
    patient = (
        extracted.get("patient_profile")
        or extracted.get("patient_name")
        or "unknown"
    )
    location = extracted.get("location") or "unknown"
    turns = [m["content"] for m in history if m["role"] == "user"]
    transcript = " | ".join(turns)
    return (
        f"Patient: {patient}. "
        f"Complaint: {symptom}. "
        f"Severity: {severity}. "
        f"Location: {location}. "
        f"Transcript: {transcript}"
    )


async def run_conversation_turn(
    case_id: str,
    lang_code: str,
    user_input: str,
    family: dict | None = None,
) -> dict:
    record = get_call_record(case_id) or {}
    history: list[dict] = record.get("conversation_history", [])
    extracted: dict = record.get("extracted_info", {})
    turn_count = len([m for m in history if m["role"] == "user"])

    # Auto-fill location for registered callers
    if family and not extracted.get("location"):
        parts = [family.get("address"), family.get("village"),
                 family.get("district"), family.get("state")]
        addr = ", ".join(p for p in parts if p)
        if addr:
            extracted["location"] = addr

    history.append({"role": "user", "content": user_input})
    logger.info(f"[{case_id}] Turn {turn_count + 1} | '{user_input[:80]}'")

    # Hard cap
    if turn_count >= MAX_TURNS:
        summary = build_summary(history, extracted)
        update_call_field(case_id, "conversation_history", history)
        logger.info(f"[{case_id}] Max turns — forcing triage")
        return {"done": True, "summary": summary}

    system_prompt = _get_system_prompt(lang_code, family)

    try:
        raw = await chat(history, system_prompt, max_tokens=600)
        logger.info(f"[{case_id}] Gemini: {raw[:160]}")

        parsed = _parse_response(raw)

        # Merge extracted fields — never overwrite a good value with null
        for k, v in parsed.get("extracted", {}).items():
            if v:
                extracted[k] = v
        # Always keep auto-filled location for registered callers
        if family and not extracted.get("location"):
            parts = [family.get("address"), family.get("village"),
                     family.get("district"), family.get("state")]
            addr = ", ".join(p for p in parts if p)
            if addr:
                extracted["location"] = addr

        update_call_field(case_id, "extracted_info", extracted)

        response_text = parsed.get("response") or ""
        if len(response_text.strip()) < 5:
            response_text = _next_question(extracted, lang_code, family, turn_count)

        history.append({"role": "assistant", "content": response_text})
        update_call_field(case_id, "conversation_history", history)

        # ── Done evaluation ────────────────────────────────────────────────
        gemini_done = parsed.get("done") is True
        has_symptom_severity = extracted.get("symptom") and extracted.get("severity")
        has_location = bool(extracted.get("location"))
        turns_done = (turn_count + 1) >= MIN_TURNS_BEFORE_DONE
        fast_track = _is_life_threatening(user_input) and turn_count >= 1

        # For unregistered callers, also need location
        location_ok = family is not None or has_location

        can_finish = has_symptom_severity and location_ok and (turns_done or fast_track)

        # Force done if all required fields collected — don't wait on Gemini
        if can_finish:
            summary = build_summary(history, extracted)
            logger.info(f"[{case_id}] Conversation complete (force={not gemini_done})")
            return {"done": True, "summary": summary}

        # Gemini tried to finish too early — inject the right follow-up
        if gemini_done and not can_finish:
            override = _next_question(extracted, lang_code, family, turn_count)
            logger.info(f"[{case_id}] Premature done overridden → '{override[:60]}'")
            history[-1]["content"] = override
            update_call_field(case_id, "conversation_history", history)
            return {"done": False, "response": override}

        return {"done": False, "response": response_text}

    except Exception as e:
        logger.error(f"[{case_id}] Gemini error: {e}", exc_info=True)
        # Use rule-based extraction so conversation still progresses
        extracted = _rule_extract(user_input, extracted, turn_count)
        update_call_field(case_id, "extracted_info", extracted)

        has_symptom_severity = extracted.get("symptom") and extracted.get("severity")
        location_ok = family is not None or bool(extracted.get("location"))

        if has_symptom_severity and location_ok:
            summary = build_summary(history, extracted)
            logger.info(f"[{case_id}] Force-done via rule-extract after Gemini error")
            return {"done": True, "summary": summary}

        # Ask the next missing field
        fallback = _next_question(extracted, lang_code, family, turn_count)
        history.append({"role": "assistant", "content": fallback})
        update_call_field(case_id, "conversation_history", history)
        return {"done": False, "response": fallback}
