from datetime import date, datetime, timezone

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import GoalStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DailyGoal(Base):
    __tablename__ = "daily_goals"
    __table_args__ = (
        CheckConstraint(
            "completion_rate >= 0 AND completion_rate <= 100",
            name="ck_daily_goal_completion_rate",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[GoalStatus] = mapped_column(
        Enum(
            GoalStatus,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=GoalStatus.PENDING,
        index=True,
    )
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    tasks: Mapped[list["LearningTask"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )
