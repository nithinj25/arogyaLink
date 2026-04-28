from twilio.twiml.voice_response import VoiceResponse, Gather
from config.settings import get_settings

settings = get_settings()

LANG_CONFIG = {
    "1": {"code": "hi-IN", "name": "Hindi",
          "greeting": "नमस्ते, कृपया अपनी स्वास्थ्य समस्या बताएं"},
    "2": {"code": "en-IN", "name": "English",
          "greeting": "Hello, please describe your health emergency"},
    "3": {"code": "te-IN", "name": "Telugu",
          "greeting": "నమస్కారం, మీ ఆరోగ్య సమస్య చెప్పండి"},
}

# Polly.Aditi only supports en-IN and hi-IN for TTS.
# Kannada/Telugu callers get English TTS but their regional language for STT.
TTS_LANG = {
    "kn-IN": "en-IN",
    "hi-IN": "hi-IN",
    "te-IN": "en-IN",
    "en-IN": "en-IN",
}

_FAREWELL_MESSAGES = {
    "en-IN": "Emergency registered. Help is on the way. You will receive an SMS shortly. Please stay calm.",
    "hi-IN": "आपातकाल दर्ज हो गया। मदद भेजी जा रही है। आपको SMS मिलेगा। शांत रहें।",
    "te-IN": "Emergency registered. Help is on the way. You will receive an SMS. Please stay calm.",
}

_FAREWELL_REGISTERED = {
    "en-IN": (
        "Emergency registered. The nearest ASHA worker is being dispatched to {address}. "
        "Help is on the way. Please stay calm and keep your phone on."
    ),
    "hi-IN": (
        "आपातकाल दर्ज हो गया। नज़दीकी आशा कार्यकर्ता {address} पर भेजी जा रही हैं। "
        "मदद आ रही है। शांत रहें और फ़ोन खुला रखें।"
    ),
    "te-IN": (
        "Emergency registered. The nearest ASHA worker is being dispatched to {address}. "
        "Help is on the way. Please stay calm and keep your phone on."
    ),
}


def build_welcome_twiml(base_url: str) -> str:
    response = VoiceResponse()
    gather = Gather(
        num_digits=1,
        action=f"{base_url}/voice/language",
        timeout=10,
        method="POST",
    )
    gather.say(
        "Welcome to ArogyaLink emergency line. "
        "Hindi ke liye, 1 dabaiye. "
        "For English, press 2. "
        "Telugu kosam, 3 napatandi.",
        voice="Polly.Aditi",
        language="en-IN",
    )
    response.append(gather)
    response.redirect(f"{base_url}/voice/incoming")
    return str(response)


def build_conversation_twiml(question: str, lang_code: str, action_url: str) -> str:
    """Speak a question and wait for the patient's spoken response."""
    tts_lang = TTS_LANG.get(lang_code, "en-IN")
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action=action_url,
        method="POST",
        speech_timeout="auto",
        timeout=12,                  # seconds of initial silence before timing out
        language=lang_code,          # STT in the patient's language
        action_on_empty_result=True,
    )
    gather.say(question, language=tts_lang, voice="Polly.Aditi")
    response.append(gather)
    # Fallback redirect if Gather completes with no speech
    response.redirect(action_url + "&empty=true", method="POST")
    return str(response)


def build_farewell_twiml(lang_code: str, family: dict | None = None) -> str:
    """Final message after triage is triggered — spoken before hanging up."""
    tts_lang = TTS_LANG.get(lang_code, "en-IN")

    if family:
        addr_parts = [
            family.get("address"), family.get("village"),
            family.get("district"), family.get("state"),
        ]
        address = ", ".join(p for p in addr_parts if p) or "your registered address"
        template = _FAREWELL_REGISTERED.get(lang_code, _FAREWELL_REGISTERED["en-IN"])
        message = template.format(address=address)
    else:
        message = _FAREWELL_MESSAGES.get(lang_code, _FAREWELL_MESSAGES["en-IN"])

    response = VoiceResponse()
    response.say(message, language=tts_lang, voice="Polly.Aditi")
    response.pause(length=1)
    response.hangup()
    return str(response)


def build_simple_farewell_twiml(message: str, lang_code: str) -> str:
    """Speak an arbitrary message and hang up — used for the force-triage path."""
    tts_lang = TTS_LANG.get(lang_code, "en-IN")
    response = VoiceResponse()
    response.say(message, language=tts_lang, voice="Polly.Aditi")
    response.pause(length=1)
    response.hangup()
    return str(response)


def build_record_twiml(lang_code: str, greeting: str, base_url: str) -> str:
    response = VoiceResponse()
    response.say(greeting, language=lang_code, voice="Polly.Aditi")
    response.record(
        action=f"{base_url}/voice/recording",
        max_length=60,
        transcribe=False,
        play_beep=True,
        timeout=5,
    )
    return str(response)


def build_processing_twiml(lang_code: str) -> str:
    messages = {
        "kn-IN": "Processing your emergency. Please hold.",
        "hi-IN": "आपकी जानकारी प्रोसेस हो रही है। कृपया प्रतीक्षा करें।",
        "te-IN": "Processing your emergency. Please hold.",
        "en-IN": "Processing your emergency. Please hold.",
    }
    tts_lang = TTS_LANG.get(lang_code, "en-IN")
    response = VoiceResponse()
    response.say(messages.get(lang_code, messages["en-IN"]), language=tts_lang, voice="Polly.Aditi")
    response.pause(length=3)
    return str(response)


def build_result_twiml(lang_code: str, action_summary: str, eta: int) -> str:
    prefix = {
        "kn-IN": f"Emergency registered. {action_summary} Ambulance arriving in approximately {eta} minutes.",
        "hi-IN": f"आपकी इमरजेंसी रजिस्टर हुई। {action_summary} एम्बुलेंस लगभग {eta} मिनट में आएगी।",
        "te-IN": f"Emergency registered. {action_summary} Ambulance arriving in approximately {eta} minutes.",
        "en-IN": f"Emergency registered. {action_summary} Ambulance arriving in approximately {eta} minutes.",
    }
    tts_lang = TTS_LANG.get(lang_code, "en-IN")
    response = VoiceResponse()
    response.say(prefix.get(lang_code, prefix["en-IN"]), language=tts_lang, voice="Polly.Aditi")
    response.hangup()
    return str(response)
