from datetime import datetime, timezone
from sqlalchemy import JSON, CheckConstraint, DateTime, Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import KnowledgeDifficulty


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeTopic(Base):
    __tablename__ = "knowledge_topics"
    __table_args__ = (
        CheckConstraint(
            "mastery_score >= 0 AND mastery_score <= 100",
            name="ck_knowledge_mastery_score",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), unique=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    difficulty: Mapped[KnowledgeDifficulty] = mapped_column(
        Enum(
            KnowledgeDifficulty,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, default="")
    learning_content: Mapped[str] = mapped_column(Text, default="")
    key_points: Mapped[list[str]] = mapped_column(JSON, default=list)
    common_questions: Mapped[list[str]] = mapped_column(JSON, default=list)
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)
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
