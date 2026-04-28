import httpx
import json
from config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Uses same Google AI Studio key as Gemma, but hits Gemini Flash (better for conversation)
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GEMINI_MODEL = "gemini-2.0-flash"


async def chat(messages: list[dict], system_prompt: str, temperature: float = 0.3, max_tokens: int = 512) -> str:
    """
    Multi-turn conversation with Gemini Flash.
    messages: list of {"role": "user"/"assistant", "content": "..."}
    Returns assistant's next response as plain text.
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

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(GEMINI_URL, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except httpx.TimeoutException:
        logger.error("Gemini API timeout")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API error {e.response.status_code}: {e.response.text}")
        raise
