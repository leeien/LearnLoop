from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import LeetCodeDifficulty

if TYPE_CHECKING:
    from app.models.learning_task import LearningTask


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LeetCodeRecord(Base):
    __tablename__ = "leetcode_records"
    __table_args__ = (
        CheckConstraint("problem_number > 0", name="ck_leetcode_problem_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("learning_tasks.id", ondelete="CASCADE"),
        index=True,
    )
    problem_number: Mapped[int] = mapped_column(Integer, index=True)
    problem_title: Mapped[str] = mapped_column(String(200))
    difficulty: Mapped[LeetCodeDifficulty] = mapped_column(
        Enum(
            LeetCodeDifficulty,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    is_solved: Mapped[bool] = mapped_column(Boolean, default=False)
    mistake_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    insight: Mapped[str | None] = mapped_column(Text, nullable=True)
    need_review: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    task: Mapped["LearningTask"] = relationship(back_populates="leetcode_records")
