from datetime import date
from time import perf_counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import QuizStatus, ReviewReportType
from app.models.quiz_session import QuizSession
from app.models.review_report import ReviewReport
from app.schemas.reminder import (
    ReminderActionResult,
    ReminderRead,
    ReminderStatusRead,
    ReminderStatusUpdate,
)
from app.services import cache_service, harness_service


def get_status(
    db: Session,
    user_id: str = cache_service.DEFAULT_USER_ID,
) -> tuple[ReminderStatusRead, bool]:
    cached = cache_service.get_reminder_status(user_id)
    if cached is not None:
        try:
            return ReminderStatusRead.model_validate(cached), True
        except Exception:
            pass

    pending_session = db.scalar(
        select(QuizSession)
        .where(QuizSession.status != QuizStatus.EVALUATED)
        .order_by(QuizSession.created_at.desc())
    )
    daily_report = db.scalar(
        select(ReviewReport).where(
            ReviewReport.report_type == ReviewReportType.DAILY,
            ReviewReport.date == date.today(),
        )
    )
    status = ReminderStatusRead(
        already_reminded=False,
        pending_quiz=pending_session is not None,
        pending_quiz_session_id=(
            pending_session.id if pending_session is not None else None
        ),
        needs_evening_review=daily_report is None,
    )
    cache_service.set_reminder_status(
        status.model_dump(mode="json"),
        user_id,
    )
    return status, False


def update_status(
    db: Session,
    payload: ReminderStatusUpdate,
    user_id: str = cache_service.DEFAULT_USER_ID,
) -> ReminderStatusRead:
    started_at = perf_counter()
    current, _ = get_status(db, user_id)
    values = current.model_dump()
    values.update(payload.model_dump(exclude_unset=True))
    if values["pending_quiz"] is False:
        values["pending_quiz_session_id"] = None
    status = ReminderStatusRead.model_validate(values)
    cache_service.set_reminder_status(
        status.model_dump(mode="json"),
        user_id,
    )
    if status != current:
        harness_service.log_event(
            event_type="reminder_triggered",
            entity_type="reminder",
            entity_id=date.today().isoformat(),
            input_payload=current.model_dump(mode="json"),
            output_payload=status.model_dump(mode="json"),
            latency_ms=(perf_counter() - started_at) * 1000,
        )
    return status


def refresh_status(
    db: Session,
    user_id: str = cache_service.DEFAULT_USER_ID,
) -> ReminderStatusRead:
    started_at = perf_counter()
    cached = cache_service.get_reminder_status(user_id)
    already_reminded = bool(
        cached and cached.get("already_reminded", False)
    )
    cache_service.invalidate_reminder_status(user_id)
    status, _ = get_status(db, user_id)
    if already_reminded:
        status = status.model_copy(update={"already_reminded": True})
        cache_service.set_reminder_status(
            status.model_dump(mode="json"),
            user_id,
        )
    if cached is not None:
        previous = ReminderStatusRead.model_validate(cached)
        if status != previous:
            harness_service.log_event(
                event_type="reminder_triggered",
                entity_type="reminder",
                entity_id=date.today().isoformat(),
                input_payload=previous.model_dump(mode="json"),
                output_payload=status.model_dump(mode="json"),
                latency_ms=(perf_counter() - started_at) * 1000,
            )
    else:
        harness_service.log_event(
            event_type="reminder_triggered",
            entity_type="reminder",
            entity_id=date.today().isoformat(),
            input_payload={"previous_status": "cache_unavailable_or_empty"},
            output_payload=status.model_dump(mode="json"),
            latency_ms=(perf_counter() - started_at) * 1000,
        )
    return status


def list_today_reminders(
    db: Session,
    user_id: str = cache_service.DEFAULT_USER_ID,
) -> tuple[list[ReminderRead], ReminderStatusRead, bool]:
    status, cache_hit = get_status(db, user_id)
    return _build_reminders(status), status, cache_hit


def mark_shown(
    db: Session,
    user_id: str = cache_service.DEFAULT_USER_ID,
) -> ReminderActionResult:
    status = update_status(
        db,
        ReminderStatusUpdate(already_reminded=True),
        user_id,
    )
    return ReminderActionResult(
        reminders=_build_reminders(status),
        status=status,
    )


def snooze(
    db: Session,
    user_id: str = cache_service.DEFAULT_USER_ID,
) -> ReminderActionResult:
    status = update_status(
        db,
        ReminderStatusUpdate(already_reminded=True),
        user_id,
    )
    return ReminderActionResult(
        reminders=_build_reminders(status, snoozed=True),
        status=status,
    )


def _build_reminders(
    status: ReminderStatusRead,
    snoozed: bool = False,
) -> list[ReminderRead]:
    today = date.today().isoformat()
    base_status = "snoozed" if snoozed else "pending"
    reminders: list[ReminderRead] = []

    if not status.already_reminded or snoozed:
        reminders.append(
            ReminderRead(
                id=f"daily-checkin:{today}",
                reminder_type="daily_checkin",
                content="查看今日学习任务并完成打卡。",
                scheduled_at=f"{today}T09:00:00",
                status=base_status,
                related_entity_type="dashboard",
                related_entity_id=today,
            )
        )

    if status.pending_quiz and status.pending_quiz_session_id is not None:
        reminders.append(
            ReminderRead(
                id=f"pending-quiz:{status.pending_quiz_session_id}",
                reminder_type="pending_quiz",
                content="有待检测 Quiz 需要完成。",
                scheduled_at=f"{today}T12:00:00",
                status=base_status,
                related_entity_type="quiz_session",
                related_entity_id=str(status.pending_quiz_session_id),
            )
        )

    if status.needs_evening_review:
        reminders.append(
            ReminderRead(
                id=f"evening-review:{today}",
                reminder_type="evening_review",
                content="今晚还没有生成每日复盘。",
                scheduled_at=f"{today}T21:00:00",
                status=base_status,
                related_entity_type="review",
                related_entity_id=today,
            )
        )

    return reminders
