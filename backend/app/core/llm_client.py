from collections.abc import Sequence
from typing import Any

from openai import OpenAI

from app.core.config import get_settings


Message = dict[str, Any]


def _get_client() -> OpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. Add it to backend/.env."
        )
    return OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


def call_llm(
    messages: Sequence[Message],
    temperature: float = 0.2,
    model: str | None = None,
    json_mode: bool = False,
) -> str:
    settings = get_settings()
    request: dict[str, Any] = {
        "model": model or settings.model_name,
        "messages": list(messages),
        "temperature": temperature,
    }
    if json_mode:
        request["response_format"] = {"type": "json_object"}

    response = _get_client().chat.completions.create(**request)
    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("The LLM returned an empty response.")
    return content


def call_eval_llm(
    messages: Sequence[Message],
    temperature: float = 0.1,
    json_mode: bool = True,
) -> str:
    return call_llm(
        messages=messages,
        temperature=temperature,
        model=get_settings().eval_model_name,
        json_mode=json_mode,
    )


def call_advanced_llm(
    messages: Sequence[Message],
    temperature: float = 0.2,
    json_mode: bool = False,
) -> str:
    return call_llm(
        messages=messages,
        temperature=temperature,
        model=get_settings().advanced_model_name,
        json_mode=json_mode,
    )

