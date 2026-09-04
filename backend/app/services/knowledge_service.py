from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.enums import KnowledgeDifficulty
from app.models.knowledge_topic import KnowledgeTopic
from app.services import cache_service


TOPIC_SEEDS = [
    ("prompt-engineering", "Prompt Engineering", "foundations", KnowledgeDifficulty.BEGINNER, "Design clear instructions, context, constraints, and output formats for language models.", ["Instruction structure", "Context and constraints"]),
    ("function-calling", "Function Calling", "tools", KnowledgeDifficulty.INTERMEDIATE, "Let a model select structured application functions and provide validated arguments.", ["Tool schemas", "Argument validation"]),
    ("tool-use", "Tool Use", "tools", KnowledgeDifficulty.INTERMEDIATE, "Connect agent decisions to controlled external capabilities and observable results.", ["Tool selection", "Permission boundaries"]),
    ("react", "ReAct", "reasoning", KnowledgeDifficulty.INTERMEDIATE, "Interleave auditable action selection with observations without exposing hidden chain-of-thought.", ["Action-observation loop", "Trace safety"]),
    ("short-term-memory", "Short-term Memory", "memory", KnowledgeDifficulty.BEGINNER, "Maintain task-local context needed during an active interaction or workflow.", ["Context window", "Working state"]),
    ("long-term-memory", "Long-term Memory", "memory", KnowledgeDifficulty.INTERMEDIATE, "Persist useful information across sessions with lifecycle and provenance controls.", ["Persistence", "Memory lifecycle"]),
    ("episodic-memory", "Episodic Memory", "memory", KnowledgeDifficulty.INTERMEDIATE, "Represent specific past events, attempts, and outcomes.", ["Event context", "Temporal retrieval"]),
    ("semantic-memory", "Semantic Memory", "memory", KnowledgeDifficulty.INTERMEDIATE, "Store stable facts, concepts, and learned relationships independent of one event.", ["Fact consolidation", "Knowledge relations"]),
    ("skill-memory", "Skill Memory", "memory", KnowledgeDifficulty.ADVANCED, "Represent reusable procedures and strategies learned from prior work.", ["Procedural knowledge", "Skill reuse"]),
    ("memory-retrieval", "Memory Retrieval", "memory", KnowledgeDifficulty.INTERMEDIATE, "Select relevant memories using filters, ranking, recency, and importance.", ["Retrieval policy", "Relevance ranking"]),
    ("memory-compression", "Memory Compression", "memory", KnowledgeDifficulty.ADVANCED, "Reduce memory volume while retaining important facts, evidence, and uncertainty.", ["Summarization", "Information retention"]),
    ("rag", "RAG", "retrieval", KnowledgeDifficulty.INTERMEDIATE, "Ground model responses in retrieved external knowledge.", ["Retrieval pipeline", "Grounded generation"]),
    ("chunking", "Chunking", "retrieval", KnowledgeDifficulty.BEGINNER, "Split source material into retrievable units while preserving useful context.", ["Chunk boundaries", "Overlap strategy"]),
    ("embedding", "Embedding", "retrieval", KnowledgeDifficulty.INTERMEDIATE, "Map content into vectors used for semantic similarity and retrieval.", ["Vector representation", "Similarity metrics"]),
    ("vector-database", "Vector Database", "retrieval", KnowledgeDifficulty.INTERMEDIATE, "Store and query embeddings with metadata filters and indexes.", ["Vector indexes", "Metadata filtering"]),
    ("rerank", "Rerank", "retrieval", KnowledgeDifficulty.ADVANCED, "Reorder retrieved candidates with a stronger relevance model.", ["Candidate scoring", "Recall versus precision"]),
    ("mcp", "MCP", "protocols", KnowledgeDifficulty.INTERMEDIATE, "Use a standard protocol to expose tools, resources, and prompts to AI clients.", ["Protocol roles", "Capability discovery"]),
    ("mcp-server", "MCP Server", "protocols", KnowledgeDifficulty.INTERMEDIATE, "Implement a bounded server that exposes validated MCP capabilities.", ["Tool contracts", "Access control"]),
    ("multi-agent", "Multi-Agent", "agents", KnowledgeDifficulty.INTERMEDIATE, "Coordinate specialized agents with explicit responsibilities and shared workflow state.", ["Role boundaries", "Coordination"]),
    ("orchestrator", "Orchestrator", "agents", KnowledgeDifficulty.ADVANCED, "Control workflow transitions, retries, state, and agent invocation policies.", ["Workflow state", "Failure handling"]),
    ("reflection", "Reflection", "learning", KnowledgeDifficulty.INTERMEDIATE, "Review outcomes and evidence to produce actionable future adjustments.", ["Outcome analysis", "Actionable revision"]),
    ("agent-harness", "Agent Harness", "observability", KnowledgeDifficulty.ADVANCED, "Capture reproducible agent runs, inputs, outputs, versions, and metrics.", ["Run records", "Evaluation reproducibility"]),
    ("trace-logging", "Trace Logging", "observability", KnowledgeDifficulty.INTERMEDIATE, "Record auditable workflow actions and observations without hidden reasoning.", ["Structured events", "Sensitive-data controls"]),
    ("llm-as-judge", "LLM-as-Judge", "evaluation", KnowledgeDifficulty.ADVANCED, "Apply versioned rubrics to model outputs while tracking confidence and calibration.", ["Rubric design", "Judge calibration"]),
    ("human-in-the-loop", "Human-in-the-loop", "governance", KnowledgeDifficulty.INTERMEDIATE, "Insert human review or approval where automation confidence or impact requires it.", ["Escalation policy", "Human override"]),
]


def list_topics(db: Session) -> list[KnowledgeTopic]:
    return list(
        db.scalars(
            select(KnowledgeTopic).order_by(
                KnowledgeTopic.category,
                KnowledgeTopic.id,
            )
        )
    )


def get_topic(db: Session, topic_id: str) -> KnowledgeTopic:
    topic = db.scalar(
        select(KnowledgeTopic).where(KnowledgeTopic.topic_id == topic_id)
    )
    if topic is None:
        raise ResourceNotFoundError(
            f"Knowledge topic '{topic_id}' was not found."
        )
    return topic


def seed_topics(db: Session) -> tuple[int, int]:
    existing_ids = set(db.scalars(select(KnowledgeTopic.topic_id)))
    created = 0

    for topic_id, title, category, difficulty, description, key_points in TOPIC_SEEDS:
        if topic_id in existing_ids:
            continue
        db.add(
            KnowledgeTopic(
                topic_id=topic_id,
                title=title,
                category=category,
                difficulty=difficulty,
                description=description,
                learning_content=(
                    f"Study {title} by understanding its purpose, core design "
                    "trade-offs, boundaries, and one practical application."
                ),
                key_points=key_points,
                common_questions=[
                    f"What problem does {title} solve?",
                    f"What are the main risks or trade-offs of {title}?",
                ],
            )
        )
        created += 1

    db.commit()
    if created:
        cache_service.invalidate_today_status()
    total = db.scalar(select(func.count()).select_from(KnowledgeTopic)) or 0
    return created, total
