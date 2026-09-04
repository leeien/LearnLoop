from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ReviewReportType


class ReflectionOutput(BaseModel):
    summary: str = Field(min_length=1)
    weaknesses: list[str] = Field(default_factory=list, max_length=10)
    insights: list[str] = Field(default_factory=list, max_length=10)
    next_actions: list[str] = Field(default_factory=list, max_length=10)


class ReviewReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_type: ReviewReportType
    date: Date
    summary: str
    completed_tasks: list[str]
    unfinished_tasks: list[str]
    weaknesses: list[str]
    insights: list[str]
    next_actions: list[str]
    created_at: datetime

