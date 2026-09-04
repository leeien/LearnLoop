from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.knowledge import KnowledgeSeedResult, KnowledgeTopicRead
from app.services import knowledge_service


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get(
    "/topics",
    response_model=ApiResponse[list[KnowledgeTopicRead]],
)
def list_topics(
    db: Session = Depends(get_db),
) -> ApiResponse[list[KnowledgeTopicRead]]:
    topics = knowledge_service.list_topics(db)
    return ApiResponse(data=topics, message="Knowledge topics were retrieved.")


@router.get(
    "/topics/{topic_id}",
    response_model=ApiResponse[KnowledgeTopicRead],
)
def get_topic(
    topic_id: str,
    db: Session = Depends(get_db),
) -> ApiResponse[KnowledgeTopicRead]:
    topic = knowledge_service.get_topic(db, topic_id)
    return ApiResponse(data=topic, message="Knowledge topic was retrieved.")


@router.post(
    "/topics/seed",
    response_model=ApiResponse[KnowledgeSeedResult],
)
def seed_topics(
    db: Session = Depends(get_db),
) -> ApiResponse[KnowledgeSeedResult]:
    created, total = knowledge_service.seed_topics(db)
    return ApiResponse(
        data=KnowledgeSeedResult(created=created, total=total),
        message="Knowledge topic seed completed.",
    )

