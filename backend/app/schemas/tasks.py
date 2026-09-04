from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import TaskStatus, TaskType


class LearningTaskCreate(BaseModel):
    goal_id: int = Field(gt=0)
    task_type: TaskType
    title: str = Field(min_length=1, max_length=200)
    topic: str | None = Field(default=None, max_length=200)
    target_count: int = Field(default=1, ge=1)
    current_count: int = Field(default=0, ge=0)
    status: TaskStatus = TaskStatus.PENDING

    @model_validator(mode="after")
    def validate_counts(self) -> "LearningTaskCreate":
        if self.current_count > self.target_count:
            raise ValueError("current_count cannot exceed target_count")
        return self


class LearningTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_id: int
    task_type: TaskType
    title: str
    topic: str | None
    target_count: int
    current_count: int
    status: TaskStatus
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskCompletionResult(BaseModel):
    task: LearningTaskRead
    quiz_session_id: int | None
