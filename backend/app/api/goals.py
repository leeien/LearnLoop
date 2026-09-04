from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.goals import DailyGoalCreate, DailyGoalRead, DailyGoalUpdate
from app.schemas.planning import DailyPlanResult
from app.services import goal_service, planning_service


router = APIRouter(prefix="/goals", tags=["goals"])


@router.post(
    "/plan",
    response_model=ApiResponse[DailyPlanResult],
    status_code=201,
)
def generate_today_plan(
    db: Session = Depends(get_db),
) -> ApiResponse[DailyPlanResult]:
    plan = planning_service.generate_today_plan(db)
    return ApiResponse(data=plan, message="Today's learning plan was created.")


@router.get("/today", response_model=ApiResponse[DailyGoalRead | None])
def get_today_goal(
    db: Session = Depends(get_db),
) -> ApiResponse[DailyGoalRead | None]:
    goal = goal_service.get_today_goal(db)
    return ApiResponse(
        data=goal,
        message="Today's daily goal was retrieved.",
    )


@router.post("", response_model=ApiResponse[DailyGoalRead], status_code=201)
def create_goal(
    payload: DailyGoalCreate,
    db: Session = Depends(get_db),
) -> ApiResponse[DailyGoalRead]:
    goal = goal_service.create_goal(db, payload)
    return ApiResponse(data=goal, message="Daily goal was created.")


@router.patch("/{goal_id}", response_model=ApiResponse[DailyGoalRead])
def update_goal(
    goal_id: int,
    payload: DailyGoalUpdate,
    db: Session = Depends(get_db),
) -> ApiResponse[DailyGoalRead]:
    goal = goal_service.update_goal(db, goal_id, payload)
    return ApiResponse(data=goal, message="Daily goal was updated.")
