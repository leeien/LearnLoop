from pydantic import BaseModel, Field, model_validator

from app.models.enums import TaskType
from app.schemas.goals import DailyGoalRead
from app.schemas.tasks import LearningTaskRead


class PlannedTask(BaseModel):
    task_type: TaskType
    title: str = Field(min_length=1, max_length=200)
    topic: str | None = Field(default=None, max_length=200)
    target_count: int = Field(default=1, ge=1, le=20)

    @model_validator(mode="after")
    def validate_topic(self) -> "PlannedTask":
        if self.task_type == TaskType.AGENT_KNOWLEDGE and not self.topic:
            raise ValueError("agent_knowledge tasks require a topic")
        return self


class GoalPlanOutput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str
    tasks: list[PlannedTask] = Field(min_length=1, max_length=6)


class DailyPlanResult(BaseModel):
    goal: DailyGoalRead
    tasks: list[LearningTaskRead]
