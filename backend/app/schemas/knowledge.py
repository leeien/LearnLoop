from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import KnowledgeDifficulty


class KnowledgeTopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: str
    title: str
    category: str
    difficulty: KnowledgeDifficulty
    description: str
    learning_content: str
    key_points: list[str]
    common_questions: list[str]
    mastery_score: float
    next_review_at: datetime | None
    created_at: datetime
    updated_at: datetime


class KnowledgeSeedResult(BaseModel):
    created: int
    total: int

