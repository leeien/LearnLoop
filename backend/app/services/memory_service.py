import re
from datetime import date, datetime, time, timedelta, timezone
from difflib import SequenceMatcher
from time import perf_counter

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.agents.memory_curator_agent import MemoryCuratorAgent
from app.core.exceptions import ResourceNotFoundError
from app.models.enums import MemoryType
from app.models.memory import Memory
from app.models.quiz_session import QuizSession
from app.schemas.memory import (
    MemoryCreate,
    MemoryCuratorOutput,
    MemoryUpdate,
)
from app.services import cache_service, harness_service


memory_curator = MemoryCuratorAgent()


def list_memories(
    db: Session,
    memory_type: MemoryType | None = None,
    topic: str | None = None,
) -> list[Memory]:
    statement = select(Memory)
    if memory_type is not None:
        statement = statement.where(Memory.memory_type == memory_type)
    if topic:
        statement = statement.where(Memory.topic == topic)
    return list(
        db.scalars(
            statement.order_by(
                Memory.importance.desc(),
                Memory.created_at.desc(),
            )
        )
    )


def search_memories(
    db: Session,
    query: str,
    topic: str | None = None,
    memory_type: MemoryType | None = None,
    limit: int = 5,
) -> list[Memory]:
    tokens = query.strip().lower().split()[:10]
    statement = select(Memory)
    for token in tokens:
        search_term = f"%{token}%"
        statement = statement.where(
            or_(
                func.lower(Memory.content).like(search_term),
                func.lower(Memory.topic).like(search_term),
                func.lower(cast(Memory.tags, String)).like(search_term),
            )
        )
    if topic:
        statement = statement.where(
            func.lower(Memory.topic) == topic.strip().lower()
        )
    if memory_type is not None:
        statement = statement.where(Memory.memory_type == memory_type)
    statement = statement.order_by(
        Memory.importance.desc(),
        Memory.confidence.desc(),
        Memory.created_at.desc(),
    ).limit(min(max(limit, 1), 100))
    return list(db.scalars(statement))


def list_due_reviews(
    db: Session,
    target_date: date,
    limit: int = 20,
) -> list[Memory]:
    end_of_day = datetime.combine(
        target_date,
        time.max,
        tzinfo=timezone.utc,
    )
    statement = (
        select(Memory)
        .where(
            Memory.next_review_at.is_not(None),
            Memory.next_review_at <= end_of_day,
        )
        .order_by(
            Memory.next_review_at.asc(),
            Memory.importance.desc(),
        )
        .limit(min(max(limit, 1), 100))
    )
    return list(db.scalars(statement))


def get_memory(db: Session, memory_id: int) -> Memory:
    memory = db.get(Memory, memory_id)
    if memory is None:
        raise ResourceNotFoundError(f"Memory {memory_id} was not found.")
    return memory


def create_memory(db: Session, payload: MemoryCreate) -> Memory:
    memory = Memory(**payload.model_dump())
    db.add(memory)
    db.commit()
    db.refresh(memory)
    cache_service.invalidate_today_status()
    return memory


def update_memory(
    db: Session,
    memory_id: int,
    payload: MemoryUpdate,
) -> Memory:
    memory = get_memory(db, memory_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(memory, field, value)
    db.commit()
    db.refresh(memory)
    cache_service.invalidate_today_status()
    return memory


def delete_memory(db: Session, memory_id: int) -> int:
    memory = get_memory(db, memory_id)
    db.delete(memory)
    db.commit()
    cache_service.invalidate_today_status()
    return memory_id


def curate_quiz_weaknesses(
    db: Session,
    quiz_session: QuizSession,
    topic: str,
) -> list[Memory]:
    weaknesses = list(
        dict.fromkeys(
            weakness
            for answer in quiz_session.answers
            for weakness in (answer.weaknesses or [])
        )
    )
    if not weaknesses:
        return []
    curated = memory_curator.curate_quiz_weaknesses(
        topic=topic,
        weaknesses=weaknesses,
        score=quiz_session.total_score or 0.0,
    )
    return store_curated(
        db=db,
        memory_type=MemoryType.WEAKNESS,
        topic=topic,
        source=f"quiz_session:{quiz_session.id}",
        curated=curated,
    )


def curate_leetcode_mistake(
    db: Session,
    topic: str,
    mistake_reason: str,
    source: str,
) -> list[Memory]:
    curated = memory_curator.curate_leetcode_mistake(
        topic,
        mistake_reason,
    )
    return store_curated(
        db,
        MemoryType.MISTAKE,
        topic,
        source,
        curated,
    )


def curate_insights(
    db: Session,
    topic: str,
    insights: list[str],
    source: str,
    source_kind: str,
) -> list[Memory]:
    if not insights:
        return []
    curated = memory_curator.curate_insights(
        topic,
        insights,
        source_kind,
    )
    return store_curated(
        db,
        MemoryType.INSIGHT,
        topic,
        source,
        curated,
    )


def store_curated(
    db: Session,
    memory_type: MemoryType,
    topic: str,
    source: str,
    curated: MemoryCuratorOutput,
) -> list[Memory]:
    started_at = perf_counter()
    existing = list(
        db.scalars(
            select(Memory).where(
                Memory.memory_type == memory_type,
                Memory.topic == topic,
            )
        )
    )
    stored: list[Memory] = []
    now = datetime.now(timezone.utc)

    for candidate in curated.memories:
        duplicate = next(
            (
                memory
                for memory in existing
                if _similarity(memory.content, candidate.content) >= 0.72
            ),
            None,
        )
        review_at = now + timedelta(days=candidate.next_review_days)
        if duplicate is not None:
            if len(candidate.content) > len(duplicate.content):
                duplicate.content = candidate.content
            duplicate.importance = max(
                duplicate.importance,
                candidate.importance,
            )
            duplicate.confidence = max(
                duplicate.confidence,
                candidate.confidence,
            )
            if (
                duplicate.next_review_at is None
                or review_at < duplicate.next_review_at
            ):
                duplicate.next_review_at = review_at
            duplicate.tags = list(
                dict.fromkeys([*duplicate.tags, *candidate.tags])
            )
            sources = duplicate.source.split("|")
            if source not in sources:
                duplicate.source = "|".join([*sources, source])[:200]
            stored.append(duplicate)
            continue

        memory = Memory(
            memory_type=memory_type,
            topic=topic,
            content=candidate.content,
            source=source,
            importance=candidate.importance,
            confidence=candidate.confidence,
            next_review_at=review_at,
            tags=candidate.tags,
        )
        db.add(memory)
        existing.append(memory)
        stored.append(memory)

    db.commit()
    for memory in stored:
        db.refresh(memory)
        harness_service.log_event(
            event_type="memory_created",
            entity_type="memory",
            entity_id=memory.id,
            input_payload={
                "source": source,
                "topic": topic,
                "memory_type": memory_type.value,
            },
            output_payload={
                "content": memory.content,
                "importance": memory.importance,
                "confidence": memory.confidence,
                "next_review_at": memory.next_review_at,
                "action": "created_or_merged",
            },
            latency_ms=(perf_counter() - started_at) * 1000,
        )
    if stored:
        cache_service.invalidate_today_status()
    return stored


def _similarity(left: str, right: str) -> float:
    normalize = lambda value: re.sub(r"\s+", "", value).lower()
    return SequenceMatcher(None, normalize(left), normalize(right)).ratio()
