"""
LLM client wrapper. Uses Anthropic Claude API.
"""
import json
import anthropic
from lib.config import ANTHROPIC_API_KEY


def call_llm(system_prompt: str, user_message: str, model: str, max_tokens: int = 4096) -> str:
    """Call Anthropic Claude API and return the text response."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    return response.content[0].text


def call_llm_json(system_prompt: str, user_message: str, model: str, max_tokens: int = 4096) -> dict:
    """Call LLM and parse JSON from response. Handles markdown code blocks."""
    raw = call_llm(system_prompt, user_message, model, max_tokens)

    # Strip markdown code block if present
    text = raw.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return {"_raw": raw, "_parse_error": True}
