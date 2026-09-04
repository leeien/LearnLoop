import hashlib
from datetime import date
from typing import Any

from app.core.exceptions import RateLimitExceededError
from app.core.redis_client import (
    delete,
    get_json,
    rate_limit_check,
    set_json,
)


DEFAULT_USER_ID = "default"
TODAY_STATUS_TTL = 300
QUIZ_SESSION_TTL = 3600
QUIZ_LLM_TTL = 86400
EVALUATION_LLM_TTL = 600
REMINDER_STATUS_TTL = 86400
LLM_RATE_LIMIT = 10
LLM_RATE_WINDOW = 60


def today_status_key(
    user_id: str = DEFAULT_USER_ID,
    target_date: date | None = None,
) -> str:
    return f"today_status:{user_id}:{(target_date or date.today()).isoformat()}"


def quiz_session_key(session_id: int) -> str:
    return f"quiz_session:{session_id}"


def quiz_llm_key(topic: str, difficulty: str) -> str:
    safe_topic = topic.strip().lower().replace(":", "-")
    return f"llm_cache:quiz:{safe_topic}:{difficulty}"


def evaluation_llm_key(
    topic: str,
    question: str,
    answer: str,
    reference_points: list[str],
) -> str:
    payload = "\n".join([topic, question, answer, *reference_points])
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"llm_cache:evaluation:{digest}"


def llm_rate_key(user_id: str = DEFAULT_USER_ID) -> str:
    return f"rate_limit:user:{user_id}:llm"


def reminder_status_key(
    user_id: str = DEFAULT_USER_ID,
    target_date: date | None = None,
) -> str:
    return (
        f"reminder_status:{user_id}:"
        f"{(target_date or date.today()).isoformat()}"
    )


def get_today_status(
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any] | None:
    value = get_json(today_status_key(user_id))
    return value if isinstance(value, dict) else None


def set_today_status(
    value: dict[str, Any],
    user_id: str = DEFAULT_USER_ID,
) -> bool:
    return set_json(
        today_status_key(user_id),
        value,
        TODAY_STATUS_TTL,
    )


def invalidate_today_status(user_id: str = DEFAULT_USER_ID) -> bool:
    return delete(today_status_key(user_id))


def get_quiz_session(session_id: int) -> dict[str, Any] | None:
    value = get_json(quiz_session_key(session_id))
    return value if isinstance(value, dict) else None


def set_quiz_session(session_id: int, value: dict[str, Any]) -> bool:
    return set_json(
        quiz_session_key(session_id),
        value,
        QUIZ_SESSION_TTL,
    )


def get_quiz_llm(topic: str, difficulty: str) -> dict[str, Any] | None:
    value = get_json(quiz_llm_key(topic, difficulty))
    return value if isinstance(value, dict) else None


def set_quiz_llm(
    topic: str,
    difficulty: str,
    value: dict[str, Any],
) -> bool:
    return set_json(
        quiz_llm_key(topic, difficulty),
        value,
        QUIZ_LLM_TTL,
    )


def get_evaluation_llm(
    topic: str,
    question: str,
    answer: str,
    reference_points: list[str],
) -> dict[str, Any] | None:
    value = get_json(
        evaluation_llm_key(
            topic,
            question,
            answer,
            reference_points,
        )
    )
    return value if isinstance(value, dict) else None


def set_evaluation_llm(
    topic: str,
    question: str,
    answer: str,
    reference_points: list[str],
    value: dict[str, Any],
) -> bool:
    return set_json(
        evaluation_llm_key(
            topic,
            question,
            answer,
            reference_points,
        ),
        value,
        EVALUATION_LLM_TTL,
    )


def ensure_llm_allowed(user_id: str = DEFAULT_USER_ID) -> None:
    result = rate_limit_check(
        llm_rate_key(user_id),
        LLM_RATE_LIMIT,
        LLM_RATE_WINDOW,
    )
    if not result.allowed:
        raise RateLimitExceededError(result.retry_after)


def get_reminder_status(
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any] | None:
    value = get_json(reminder_status_key(user_id))
    return value if isinstance(value, dict) else None


def set_reminder_status(
    value: dict[str, Any],
    user_id: str = DEFAULT_USER_ID,
) -> bool:
    return set_json(
        reminder_status_key(user_id),
        value,
        REMINDER_STATUS_TTL,
    )


def invalidate_reminder_status(user_id: str = DEFAULT_USER_ID) -> bool:
    return delete(reminder_status_key(user_id))

