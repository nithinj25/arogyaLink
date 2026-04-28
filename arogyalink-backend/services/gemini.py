import httpx
from config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GEMINI_MODEL = "gemini-2.0-flash"


async def chat(messages: list[dict], system_prompt: str, temperature: float = 0.3, max_tokens: int = 512) -> str:
    """
    Single-attempt Gemini call with a tight 8s timeout.
    Fails fast so Twilio never hits its 15s webhook timeout.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.gemma_api_key}",
    }
    payload = {
        "model": GEMINI_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=8.0) as client:
        r = await client.post(GEMINI_URL, headers=headers, json=payload)
        if r.status_code == 429:
            logger.warning("Gemini 429 — falling back to rule-based extraction")
            raise httpx.HTTPStatusError("429", request=r.request, response=r)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
