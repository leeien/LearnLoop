from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import TaskStatus, TaskType

if TYPE_CHECKING:
    from app.models.daily_goal import DailyGoal
    from app.models.leetcode_record import LeetCodeRecord
    from app.models.quiz_session import QuizSession


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LearningTask(Base):
    __tablename__ = "learning_tasks"
    __table_args__ = (
        CheckConstraint("target_count >= 1", name="ck_task_target_count"),
        CheckConstraint("current_count >= 0", name="ck_task_current_count_min"),
        CheckConstraint(
            "current_count <= target_count",
            name="ck_task_current_count_max",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    goal_id: Mapped[int] = mapped_column(
        ForeignKey("daily_goals.id", ondelete="CASCADE"),
        index=True,
    )
    task_type: Mapped[TaskType] = mapped_column(
        Enum(
            TaskType,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200))
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True)
    target_count: Mapped[int] = mapped_column(Integer, default=1)
    current_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=TaskStatus.PENDING,
        index=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    goal: Mapped["DailyGoal"] = relationship(back_populates="tasks")
    leetcode_records: Mapped[list["LeetCodeRecord"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    quiz_session: Mapped[Optional["QuizSession"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        uselist=False,
    )
