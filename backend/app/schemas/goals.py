from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import GoalStatus


class DailyGoalCreate(BaseModel):
    date: Date = Field(default_factory=Date.today)
    title: str = Field(min_length=1, max_length=200)
    description: str = ""


class DailyGoalUpdate(BaseModel):
    date: Date | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: GoalStatus | None = None
    completion_rate: float | None = Field(default=None, ge=0, le=100)


class DailyGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: Date
    title: str
    description: str
    status: GoalStatus
    completion_rate: float
    created_at: datetime
    updated_at: datetime
