import httpx
from app.config import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"

def is_quota_error(error: Exception) -> bool:
    error_message = str(error)
    return (
        "429" in error_message
        or "RESOURCE_EXHAUSTED" in error_message
        or "quota" in error_message.lower()
    )

def generate_text(prompt: str) -> str:
    response = httpx.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        },
        timeout=60.0,
    )
    response.raise_for_status()
    response_data = response.json()

    return response_data["choices"][0]["message"]["content"]

    