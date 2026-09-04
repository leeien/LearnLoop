import logging
import re
from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.learning_harness_log import LearningHarnessLog


logger = logging.getLogger(__name__)

_SENSITIVE_KEY = re.compile(
    r"(api.?key|authorization|password|secret|access.?token|"
    r"refresh.?token|system.?prompt|environment|env)",
    re.IGNORECASE,
)
_MAX_STRING_LENGTH = 2000
_MAX_COLLECTION_ITEMS = 50


def log_event(
    *,
    event_type: str,
    entity_type: str,
    entity_id: int | str,
    input_payload: Mapping[str, Any] | None = None,
    output_payload: Mapping[str, Any] | None = None,
    status: str = "success",
    latency_ms: int | float = 0,
) -> LearningHarnessLog | None:
    """Persist an audit event independently; never break the main workflow."""
    db = None
    try:
        db = SessionLocal()
        log = LearningHarnessLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
            input_payload=_sanitize(dict(input_payload or {})),
            output_payload=_sanitize(dict(output_payload or {})),
            status=status,
            latency_ms=max(0, round(latency_ms)),
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception as error:
        if db is not None:
            try:
                db.rollback()
            except Exception:
                pass
        logger.warning("Harness logging failed without blocking workflow: %s", error)
        return None
    finally:
        if db is not None:
            try:
                db.close()
            except Exception:
                pass


def list_logs(
    *,
    event_type: str | None = None,
    entity_type: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> list[LearningHarnessLog]:
    db = SessionLocal()
    try:
        statement = select(LearningHarnessLog)
        if event_type:
            statement = statement.where(
                LearningHarnessLog.event_type == event_type
            )
        if entity_type:
            statement = statement.where(
                LearningHarnessLog.entity_type == entity_type
            )
        if status:
            statement = statement.where(
                LearningHarnessLog.status == status
            )
        statement = statement.order_by(
            LearningHarnessLog.created_at.desc(),
            LearningHarnessLog.id.desc(),
        ).limit(min(max(limit, 1), 500))
        return list(db.scalars(statement))
    finally:
        db.close()


def list_logs_by_entity(
    entity_type: str,
    entity_id: int | str,
    *,
    limit: int = 100,
) -> list[LearningHarnessLog]:
    db = SessionLocal()
    try:
        statement = (
            select(LearningHarnessLog)
            .where(
                LearningHarnessLog.entity_type == entity_type,
                LearningHarnessLog.entity_id == str(entity_id),
            )
            .order_by(
                LearningHarnessLog.created_at.asc(),
                LearningHarnessLog.id.asc(),
            )
            .limit(min(max(limit, 1), 500))
        )
        return list(db.scalars(statement))
    finally:
        db.close()


def list_recent_trace(limit: int = 50) -> list[LearningHarnessLog]:
    return list_logs(limit=min(max(limit, 1), 200))


def _sanitize(value: Any, key: str | None = None) -> Any:
    if key and _SENSITIVE_KEY.search(key):
        return "[REDACTED]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        if len(value) <= _MAX_STRING_LENGTH:
            return value
        return f"{value[:_MAX_STRING_LENGTH]}…[truncated]"
    if isinstance(value, Mapping):
        return {
            str(item_key): _sanitize(item_value, str(item_key))
            for item_key, item_value in list(value.items())[
                :_MAX_COLLECTION_ITEMS
            ]
        }
    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        return [
            _sanitize(item)
            for item in list(value)[:_MAX_COLLECTION_ITEMS]
        ]
    return _sanitize(str(value), key)
