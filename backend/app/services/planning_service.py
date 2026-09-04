from datetime import date
from time import perf_counter

from sqlalchemy.orm import Session

from app.agents.goal_planner_agent import GoalPlannerAgent
from app.core.exceptions import ResourceConflictError
from app.mcp.memory_mcp_server import memory_mcp_server
from app.schemas.goals import DailyGoalCreate
from app.schemas.planning import DailyPlanResult
from app.schemas.tasks import LearningTaskCreate
from app.services import (
    goal_service,
    harness_service,
    mastery_service,
    task_service,
)


goal_planner = GoalPlannerAgent()


def generate_today_plan(db: Session) -> DailyPlanResult:
    if goal_service.get_today_goal(db) is not None:
        raise ResourceConflictError("Today's daily goal already exists.")

    started_at = perf_counter()
    due_memories = memory_mcp_server.call_tool(
        "memory.list_due_reviews",
        {"date": date.today().isoformat(), "limit": 5},
    )
    weakest_topics = sorted(
        mastery_service.list_masteries(db),
        key=lambda item: item.mastery_score,
    )[:5]
    context = {
        "date": date.today().isoformat(),
        "due_memories": due_memories,
        "weakest_topics": [
            {"topic": item.topic, "mastery_score": item.mastery_score}
            for item in weakest_topics
        ],
    }
    plan = goal_planner.generate(context)
    goal = goal_service.create_goal(
        db,
        DailyGoalCreate(
            title=plan.title,
            description=plan.description,
        ),
    )
    tasks = [
        task_service.create_task(
            db,
            LearningTaskCreate(
                goal_id=goal.id,
                task_type=item.task_type,
                title=item.title,
                topic=item.topic,
                target_count=item.target_count,
            ),
        )
        for item in plan.tasks
    ]
    harness_service.log_event(
        event_type="goal_planned",
        entity_type="goal",
        entity_id=goal.id,
        input_payload={
            "due_memory_count": len(due_memories),
            "mastery_topic_count": len(weakest_topics),
        },
        output_payload={
            "title": goal.title,
            "task_count": len(tasks),
            "tasks": [item.title for item in tasks],
        },
        latency_ms=(perf_counter() - started_at) * 1000,
    )
    return DailyPlanResult(goal=goal, tasks=tasks)
