from pydantic import BaseModel

from app.schemas.goals import DailyGoalRead


class TaskSummary(BaseModel):
    total: int
    pending: int
    completed: int
    skipped: int


class KnowledgeSummary(BaseModel):
    total_topics: int
    average_mastery: float


class LeetCodeSummary(BaseModel):
    total_records: int
    solved_records: int
    need_review: int


class DashboardSummary(BaseModel):
    today_goal: DailyGoalRead | None
    tasks: TaskSummary
    knowledge: KnowledgeSummary
    leetcode: LeetCodeSummary

