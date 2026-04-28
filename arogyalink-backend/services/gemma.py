import httpx
import json
from config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

GEMMA_URL = f"{settings.gemma_base_url}/chat/completions"


async def call_gemma(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.2,
    max_tokens: int = 1024,
    json_mode: bool = False,
) -> str:
    """
    Call Gemma 4 via Google AI Studio OpenAI-compatible endpoint.
    Returns the assistant's text response.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.gemma_api_key}",
    }

    payload = {
        "model": settings.gemma_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GEMMA_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except httpx.TimeoutException:
        logger.error("Gemma API timeout")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemma API error: {e.response.status_code} — {e.response.text}")
        raise


async def call_gemma_json(system_prompt: str, user_message: str) -> dict:
    """Call Gemma and parse JSON response. Strips markdown fences if present."""
    raw = await call_gemma(system_prompt, user_message, json_mode=True)
    clean = raw.strip()
    if clean.startswith("```"):
        clean = "\n".join(clean.split("\n")[1:])
    if clean.endswith("```"):
        clean = "\n".join(clean.split("\n")[:-1])
    return json.loads(clean.strip())
