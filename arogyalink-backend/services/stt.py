import httpx
import base64
from config.settings import get_settings
from utils.logger import get_logger
from services.audio_processing import preprocess_audio

settings = get_settings()
logger = get_logger(__name__)

STT_URL = "https://speech.googleapis.com/v1/speech:recognize"


async def transcribe_recording_url(recording_url: str, lang_code: str) -> str:
    """
    Download Twilio recording, denoise + bandpass filter, then transcribe via Google STT.
    NOTE: Requires Speech-to-Text API enabled on the same key as google_maps_api_key,
    or replace with a dedicated GOOGLE_STT_API_KEY env var in production.
    """
    async with httpx.AsyncClient(
        auth=(settings.twilio_account_sid, settings.twilio_auth_token),
        timeout=30.0
    ) as client:
        audio_response = await client.get(recording_url + ".wav")
        raw_bytes = audio_response.content

    logger.info(f"Audio downloaded: {len(raw_bytes)} bytes — applying noise reduction + bandpass filter")
    audio_bytes = preprocess_audio(raw_bytes)
    logger.info(f"Audio preprocessed: {len(audio_bytes)} bytes")

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    payload = {
        "config": {
            "encoding": "LINEAR16",
            "sampleRateHertz": 8000,
            "languageCode": lang_code,
            "alternativeLanguageCodes": ["en-IN", "kn-IN", "hi-IN", "te-IN"],
            "enableAutomaticPunctuation": True,
            "model": "phone_call",
        },
        "audio": {"content": audio_b64},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            STT_URL,
            params={"key": settings.google_maps_api_key},
            json=payload,
        )
        data = r.json()

    try:
        return data["results"][0]["alternatives"][0]["transcript"]
    except (KeyError, IndexError):
        logger.warning(f"STT returned no transcript: {data}")
        return ""
