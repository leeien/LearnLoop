from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, Enum, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import ReviewReportType


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReviewReport(Base):
    __tablename__ = "review_reports"
    __table_args__ = (
        UniqueConstraint(
            "report_type",
            "date",
            name="uq_review_report_type_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    report_type: Mapped[ReviewReportType] = mapped_column(
        Enum(
            ReviewReportType,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, index=True)
    summary: Mapped[str] = mapped_column(Text)
    completed_tasks: Mapped[list[str]] = mapped_column(JSON, default=list)
    unfinished_tasks: Mapped[list[str]] = mapped_column(JSON, default=list)
    weaknesses: Mapped[list[str]] = mapped_column(JSON, default=list)
    insights: Mapped[list[str]] = mapped_column(JSON, default=list)
    next_actions: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

