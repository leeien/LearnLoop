from enum import Enum


class GoalStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskType(str, Enum):
    AGENT_KNOWLEDGE = "agent_knowledge"
    LEETCODE = "leetcode"
    REVIEW = "review"
    REFLECTION = "reflection"


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class KnowledgeDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LeetCodeDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizStatus(str, Enum):
    PENDING = "pending"
    ANSWERED = "answered"
    EVALUATED = "evaluated"


class QuizQuestionType(str, Enum):
    CONCEPT = "concept"
    COMPARISON = "comparison"
    SCENARIO = "scenario"
    PROS_CONS = "pros_cons"
    INTERVIEW = "interview"


class MemoryType(str, Enum):
    GOAL = "goal_memory"
    COMPLETION = "completion_memory"
    WEAKNESS = "weakness_memory"
    MISTAKE = "mistake_memory"
    INSIGHT = "insight_memory"
    REVIEW = "review_memory"


class ReviewReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class KnowledgeSourceType(str, Enum):
    MARKDOWN = "markdown"
    TEXT = "text"
    UPLOAD = "upload"
