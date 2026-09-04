from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import LeetCodeDifficulty


class LeetCodeRecordCreate(BaseModel):
    task_id: int = Field(gt=0)
    problem_number: int = Field(gt=0)
    problem_title: str = Field(min_length=1, max_length=200)
    difficulty: LeetCodeDifficulty
    tags: list[str] = Field(default_factory=list)
    is_solved: bool = False
    mistake_reason: str | None = None
    insight: str | None = None
    need_review: bool = False
    next_review_at: datetime | None = None


class LeetCodeRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    problem_number: int
    problem_title: str
    difficulty: LeetCodeDifficulty
    tags: list[str]
    is_solved: bool
    mistake_reason: str | None
    insight: str | None
    need_review: bool
    next_review_at: datetime | None
    created_at: datetime
    updated_at: datetime

