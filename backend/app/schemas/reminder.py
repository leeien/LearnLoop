from pydantic import BaseModel


class ReminderStatusRead(BaseModel):
    already_reminded: bool
    pending_quiz: bool
    pending_quiz_session_id: int | None
    needs_evening_review: bool


class ReminderStatusUpdate(BaseModel):
    already_reminded: bool | None = None
    pending_quiz: bool | None = None
    pending_quiz_session_id: int | None = None
    needs_evening_review: bool | None = None


class ReminderRead(BaseModel):
    id: str
    reminder_type: str
    content: str
    scheduled_at: str
    status: str
    related_entity_type: str | None = None
    related_entity_id: str | None = None


class ReminderActionResult(BaseModel):
    reminders: list[ReminderRead]
    status: ReminderStatusRead
