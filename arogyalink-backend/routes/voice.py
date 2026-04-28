from fastapi import APIRouter, Request, Form, BackgroundTasks, HTTPException
from fastapi.responses import Response
from twilio.rest import Client

from services.twilio_voice import (
    build_welcome_twiml,
    build_conversation_twiml,
    build_farewell_twiml,
    build_simple_farewell_twiml,
    LANG_CONFIG,
)
from agents.conversation import run_conversation_turn, build_summary
from agents.registration import run_registration_turn
from agents.orchestrator import run_orchestrator
from firebase.client import (
    create_call_record, update_call_field, get_call_record,
    get_family_by_phone, increment_family_call_count,
)
from utils.id_gen import generate_case_id
from utils.phone import to_e164
from config.settings import get_settings
from utils.logger import get_logger

router = APIRouter(prefix="/voice", tags=["voice-ivr"])
logger = get_logger(__name__)
settings = get_settings()

# ── Opening questions ──────────────────────────────────────────────────────────
# For registered callers this is replaced by a personalised greeting built inline.
_OPENING_QUESTIONS = {
    "kn-IN": "Hello, this is ArogyaLink. Please describe your emergency. You can speak in Kannada.",
    "hi-IN": "नमस्ते, यह ArogyaLink है। कृपया अपनी आपात स्थिति बताएं।",
    "te-IN": "Hello, this is ArogyaLink. Please describe your emergency. You can speak in Telugu.",
    "en-IN": "Hello, this is ArogyaLink. What is your emergency? Please describe what happened.",
}

_REGISTERED_OPENINGS = {
    "kn-IN": "Hello {first_name}! We have your family registered. Who needs help today?",
    "hi-IN": "नमस्ते {first_name}! आपका परिवार हमारे पास पंजीकृत है। आज किसे मदद चाहिए?",
    "te-IN": "Hello {first_name}! We have your family registered. Who needs help today?",
    "en-IN": "Hello {first_name}! We have your family registered. Who needs help today?",
}

# Retry prompts — 3 variants so consecutive retries don't sound identical
_RETRY_PROMPTS = {
    "en-IN": [
        "Sorry, I didn't catch that. Please describe your emergency.",
        "I'm having trouble hearing you. Please speak a little louder.",
        "I still couldn't hear clearly. Please tell me what the emergency is.",
    ],
    "hi-IN": [
        "माफ करें, सुनाई नहीं दिया। कृपया अपनी समस्या बताएं।",
        "आपकी आवाज़ ठीक से नहीं आ रही। ज़रा ज़ोर से बोलिए।",
        "फिर से सुनाई नहीं दिया। कृपया बताएं क्या हुआ।",
    ],
    "kn-IN": [
        "Sorry, I couldn't hear you. Please describe your emergency.",
        "I'm having trouble hearing. Please speak louder.",
        "I still couldn't hear. Please tell me what the emergency is.",
    ],
    "te-IN": [
        "Sorry, I couldn't hear you. Please describe your emergency.",
        "I'm having trouble hearing. Please speak louder.",
        "I still couldn't hear. Please tell me what the emergency is.",
    ],
}

_TRANSFER_MESSAGES = {
    "en-IN": "We are registering your emergency based on what we have. Help will be sent shortly. Please stay calm.",
    "hi-IN": "हम आपकी आपात स्थिति दर्ज कर रहे हैं। मदद भेजी जा रही है। शांत रहें।",
    "kn-IN": "We are registering your emergency. Help will be sent. Please stay calm.",
    "te-IN": "We are registering your emergency. Help will be sent. Please stay calm.",
}

# Offer registration after a successful emergency for unregistered callers
_REGISTRATION_OFFER = {
    "en-IN": "To get faster help next time, you can register your family. Press 1 to register now, or hang up.",
    "hi-IN": "अगली बार तेज़ मदद के लिए अपना परिवार पंजीकृत करें। अभी पंजीकरण के लिए 1 दबाएं।",
    "kn-IN": "To get faster help next time, press 1 to register your family now, or hang up.",
    "te-IN": "To get faster help next time, press 1 to register your family now, or hang up.",
}

MAX_EMPTY_RETRIES = 2


# ── Step 1: Incoming call ──────────────────────────────────────────────────────

@router.post("/incoming")
async def handle_incoming_call(
    request: Request,
    From: str = Form(...),
    CallSid: str = Form(...),
):
    phone = to_e164(From)
    logger.info(f"Incoming call from {phone} | SID={CallSid}")
    twiml = build_welcome_twiml(settings.app_base_url)
    return Response(content=twiml, media_type="application/xml")


# ── Step 2: Language chosen ────────────────────────────────────────────────────

@router.post("/language")
async def handle_language_selection(
    Digits: str = Form(...),
    From: str = Form(...),
    CallSid: str = Form(...),
):
    phone = to_e164(From)
    lang_info = LANG_CONFIG.get(Digits, LANG_CONFIG["4"])
    lang_code = lang_info["code"]

    # Look up registered family
    family = get_family_by_phone(phone)

    case_id = generate_case_id()
    create_call_record(case_id=case_id, phone=phone, source="voice", lang=lang_code)
    update_call_field(case_id, "call_sid", CallSid)

    if family:
        # Store family reference so every /converse turn can use it
        update_call_field(case_id, "family_phone", phone)
        update_call_field(case_id, "family_name", family.get("primary_name"))
        increment_family_call_count(phone)

        first_name = (family.get("primary_name") or "there").split()[0]
        opening = _REGISTERED_OPENINGS.get(lang_code, _REGISTERED_OPENINGS["en-IN"]).format(
            first_name=first_name
        )
        logger.info(f"[{case_id}] Registered caller: {family.get('primary_name')}")
    else:
        opening = _OPENING_QUESTIONS.get(lang_code, _OPENING_QUESTIONS["en-IN"])
        logger.info(f"[{case_id}] Unregistered caller")

    update_call_field(case_id, "conversation_history", [
        {"role": "assistant", "content": opening}
    ])

    action_url = f"{settings.app_base_url}/voice/converse?case_id={case_id}&lang={lang_code}"
    twiml = build_conversation_twiml(opening, lang_code, action_url)

    logger.info(f"[{case_id}] Conversation started | lang={lang_code}")
    return Response(content=twiml, media_type="application/xml")


# ── Step 3+: Conversation turns ────────────────────────────────────────────────

@router.post("/converse")
async def handle_conversation(
    request: Request,
    background_tasks: BackgroundTasks,
    case_id: str,
    lang: str,
    empty: str = "false",
    retries: int = 0,
    From: str = Form(default=""),
    SpeechResult: str = Form(default=""),
    Confidence: str = Form(default="0"),
):
    phone = to_e164(From) if From else ""
    confidence = float(Confidence) if Confidence else 0.0

    logger.info(
        f"[{case_id}] Speech='{SpeechResult[:60]}' | "
        f"conf={confidence:.2f} | empty={empty} | retries={retries}"
    )

    # ── Empty / unclear speech ─────────────────────────────────────────────────
    speech_missing = not SpeechResult or empty == "true"
    speech_unclear = bool(SpeechResult) and confidence < 0.35

    if speech_missing or speech_unclear:
        if retries >= MAX_EMPTY_RETRIES:
            logger.warning(f"[{case_id}] Force-triaging after {retries} empty retries")
            record = get_call_record(case_id) or {}
            extracted = record.get("extracted_info", {})
            history = record.get("conversation_history", [])
            summary = (
                build_summary(history, extracted)
                if history
                else f"Emergency call from {phone} — unable to gather details"
            )
            background_tasks.add_task(
                run_orchestrator, case_id=case_id, phone=phone,
                lang=lang, transcript=summary, source="voice",
            )
            msg = _TRANSFER_MESSAGES.get(lang, _TRANSFER_MESSAGES["en-IN"])
            return Response(
                content=build_simple_farewell_twiml(msg, lang),
                media_type="application/xml",
            )

        prompts = _RETRY_PROMPTS.get(lang, _RETRY_PROMPTS["en-IN"])
        retry_msg = prompts[min(retries, len(prompts) - 1)]
        action_url = (
            f"{settings.app_base_url}/voice/converse"
            f"?case_id={case_id}&lang={lang}&retries={retries + 1}"
        )
        return Response(
            content=build_conversation_twiml(retry_msg, lang, action_url),
            media_type="application/xml",
        )

    # ── Good speech — run a Gemini turn ────────────────────────────────────────
    # Fetch family (if registered) for this case
    record = get_call_record(case_id) or {}
    family_phone = record.get("family_phone")
    family = get_family_by_phone(family_phone) if family_phone else None

    result = await run_conversation_turn(
        case_id=case_id,
        lang_code=lang,
        user_input=SpeechResult,
        family=family,
    )

    # Retries reset to 0 on successful speech (no retries param → defaults to 0)
    action_url = f"{settings.app_base_url}/voice/converse?case_id={case_id}&lang={lang}"

    if result["done"]:
        logger.info(f"[{case_id}] Conversation complete — triggering orchestrator")
        background_tasks.add_task(
            run_orchestrator, case_id=case_id, phone=phone,
            lang=lang, transcript=result["summary"], source="voice",
        )

        # For unregistered callers — offer registration after farewell
        if not family:
            background_tasks.add_task(
                _maybe_offer_registration, case_id, phone, lang
            )

        return Response(
            content=build_farewell_twiml(lang),
            media_type="application/xml",
        )

    return Response(
        content=build_conversation_twiml(result["response"], lang, action_url),
        media_type="application/xml",
    )


async def _maybe_offer_registration(case_id: str, phone: str, lang: str):
    """No-op placeholder — registration offer is handled via /voice/offer-register."""
    pass


# ── Registration offer (digit press after emergency) ──────────────────────────

@router.post("/offer-register")
async def offer_registration(
    From: str = Form(default=""),
    lang: str = "en-IN",
):
    """Called after farewell if we want to offer registration to unregistered callers."""
    from services.twilio_voice import TTS_LANG
    from twilio.twiml.voice_response import VoiceResponse, Gather

    phone = to_e164(From) if From else ""
    tts_lang = TTS_LANG.get(lang, "en-IN")
    offer_msg = _REGISTRATION_OFFER.get(lang, _REGISTRATION_OFFER["en-IN"])

    response = VoiceResponse()
    gather = Gather(
        num_digits=1,
        action=f"{settings.app_base_url}/voice/register-start?lang={lang}&phone={phone}",
        timeout=8,
        method="POST",
    )
    gather.say(offer_msg, language=tts_lang, voice="Polly.Aditi")
    response.append(gather)
    response.hangup()
    return Response(content=str(response), media_type="application/xml")


# ── IVR Registration flow ──────────────────────────────────────────────────────

@router.post("/register-start")
async def registration_start(
    Digits: str = Form(default=""),
    phone: str = "",
    lang: str = "en-IN",
):
    """User pressed 1 to register — create a registration case and start the flow."""
    if Digits != "1":
        from twilio.twiml.voice_response import VoiceResponse
        r = VoiceResponse()
        r.hangup()
        return Response(content=str(r), media_type="application/xml")

    case_id = generate_case_id()
    create_call_record(case_id=case_id, phone=phone, source="voice_reg", lang=lang)

    welcome = {
        "en-IN": "Great! I will register your family. This takes about 2 minutes. What is your full name?",
        "hi-IN": "बढ़िया! मैं आपका परिवार पंजीकृत करूँगा। आपका पूरा नाम क्या है?",
        "kn-IN": "Great! I will register your family. This takes about 2 minutes. What is your full name?",
        "te-IN": "Great! I will register your family. This takes about 2 minutes. What is your full name?",
    }.get(lang, "Great! What is your full name?")

    update_call_field(case_id, "reg_history", [{"role": "assistant", "content": welcome}])
    action_url = f"{settings.app_base_url}/voice/register-converse?case_id={case_id}&lang={lang}&phone={phone}"
    twiml = build_conversation_twiml(welcome, lang, action_url)
    return Response(content=twiml, media_type="application/xml")


@router.post("/register-converse")
async def registration_converse(
    case_id: str,
    lang: str,
    phone: str = "",
    empty: str = "false",
    retries: int = 0,
    SpeechResult: str = Form(default=""),
    Confidence: str = Form(default="0"),
):
    """Multi-turn registration conversation."""
    confidence = float(Confidence) if Confidence else 0.0

    if not SpeechResult or empty == "true" or confidence < 0.3:
        if retries >= 3:
            msg = "We could not complete your registration. Please call back or visit our website."
            return Response(
                content=build_simple_farewell_twiml(msg, lang),
                media_type="application/xml",
            )
        retry_msg = "Sorry, I didn't catch that. Please repeat."
        action_url = (
            f"{settings.app_base_url}/voice/register-converse"
            f"?case_id={case_id}&lang={lang}&phone={phone}&retries={retries + 1}"
        )
        return Response(
            content=build_conversation_twiml(retry_msg, lang, action_url),
            media_type="application/xml",
        )

    result = await run_registration_turn(
        case_id=case_id,
        phone=phone,
        lang_code=lang,
        user_input=SpeechResult,
    )

    if result["done"]:
        logger.info(f"[{case_id}] Registration complete for {phone}")
        return Response(
            content=build_simple_farewell_twiml(result["response"], lang),
            media_type="application/xml",
        )

    action_url = (
        f"{settings.app_base_url}/voice/register-converse"
        f"?case_id={case_id}&lang={lang}&phone={phone}"
    )
    return Response(
        content=build_conversation_twiml(result["response"], lang, action_url),
        media_type="application/xml",
    )


# ── Outbound call trigger ──────────────────────────────────────────────────────

@router.post("/call-me")
async def trigger_outbound_call(phone: str = "+919902740794"):
    """Trigger an outbound Twilio call. When answered, the emergency IVR starts."""
    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        call = client.calls.create(
            to=to_e164(phone),
            from_=settings.twilio_phone_number,
            url=f"{settings.app_base_url}/voice/incoming",
        )
        logger.info(f"Outbound call triggered to {phone} | SID={call.sid}")
        return {
            "status": "calling",
            "message": f"Twilio is calling {phone}. Pick up — the conversation will start.",
            "call_sid": call.sid,
        }
    except Exception as e:
        logger.error(f"Outbound call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
