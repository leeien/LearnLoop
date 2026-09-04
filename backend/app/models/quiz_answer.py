from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import QuizQuestionType

if TYPE_CHECKING:
    from app.models.quiz_session import QuizSession


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    __table_args__ = (
        CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 100)",
            name="ck_quiz_answer_score",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_session_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"),
        index=True,
    )
    question: Mapped[str] = mapped_column(Text)
    question_type: Mapped[QuizQuestionType] = mapped_column(
        Enum(
            QuizQuestionType,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    user_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    concept_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    key_points_coverage: Mapped[float | None] = mapped_column(Float, nullable=True)
    engineering_understanding: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    clarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    strengths: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_review_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    quiz_session: Mapped["QuizSession"] = relationship(back_populates="answers")
