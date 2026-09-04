from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import QuizStatus

if TYPE_CHECKING:
    from app.models.learning_task import LearningTask
    from app.models.quiz_answer import QuizAnswer


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("learning_tasks.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    topic: Mapped[str] = mapped_column(String(200), index=True)
    status: Mapped[QuizStatus] = mapped_column(
        Enum(
            QuizStatus,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=QuizStatus.PENDING,
        index=True,
    )
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    evaluated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    task: Mapped["LearningTask"] = relationship(back_populates="quiz_session")
    answers: Mapped[list["QuizAnswer"]] = relationship(
        back_populates="quiz_session",
        cascade="all, delete-orphan",
        order_by="QuizAnswer.id",
    )

