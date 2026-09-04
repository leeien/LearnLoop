from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TopicMasteryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic: str
    category: str
    mastery_score: float
    completed_count: int
    quiz_count: int
    average_quiz_score: float
    review_count: int
    last_reviewed_at: datetime | None
    next_review_at: datetime | None
    created_at: datetime
    updated_at: datetime

