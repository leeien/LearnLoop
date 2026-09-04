from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.reminder import ReminderActionResult, ReminderRead
from app.services import reminder_service


router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/today", response_model=ApiResponse[list[ReminderRead]])
def list_today_reminders(
    db: Session = Depends(get_db),
) -> ApiResponse[list[ReminderRead]]:
    reminders, _, cache_hit = reminder_service.list_today_reminders(db)
    return ApiResponse(
        data=reminders,
        message="Today's reminders were retrieved.",
        cache_hit=cache_hit,
    )


@router.post(
    "/snooze",
    response_model=ApiResponse[ReminderActionResult],
)
def snooze_reminders(
    db: Session = Depends(get_db),
) -> ApiResponse[ReminderActionResult]:
    result = reminder_service.snooze(db)
    return ApiResponse(
        data=result,
        message="Today's reminders were snoozed.",
    )


@router.post(
    "/mark-shown",
    response_model=ApiResponse[ReminderActionResult],
)
def mark_reminders_shown(
    db: Session = Depends(get_db),
) -> ApiResponse[ReminderActionResult]:
    result = reminder_service.mark_shown(db)
    return ApiResponse(
        data=result,
        message="Today's reminders were marked as shown.",
    )
