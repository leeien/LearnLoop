import logging
import re
from datetime import date
from time import perf_counter

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.agents.quiz_agent import QuizAgent
from app.core.config import get_settings
from app.core.exceptions import (
    DependencyUnavailableError,
    RateLimitExceededError,
    ResourceNotFoundError,
)
from app.core.llm_client import call_llm
from app.models.enums import TaskStatus, TaskType
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.learning_task import LearningTask
from app.prompts.rag_prompts import build_rag_messages
from app.schemas.goals import DailyGoalCreate
from app.schemas.quiz import QuizAgentOutput
from app.schemas.rag import (
    DocumentIndexResult,
    KnowledgeChunkRead,
    KnowledgeDocumentCreate,
    KnowledgeDocumentDetail,
    KnowledgeDocumentRead,
    KnowledgeDocumentUpdate,
    RAGAnswer,
    RAGQuizQuestion,
    RAGQuizRequest,
    RAGQuizResult,
    RAGSearchResult,
    RAGSource,
)
from app.schemas.tasks import LearningTaskCreate
from app.services import (
    cache_service,
    goal_service,
    harness_service,
    quiz_service,
    task_service,
)

from .chunker import chunk_markdown
from .document_loader import load_markdown_sections, normalize_document
from .embedding_client import get_embedding_client
from .retriever import retrieve
from .vector_store import get_vector_store


logger = logging.getLogger(__name__)
quiz_agent = QuizAgent()
INSUFFICIENT_ANSWER = "知识库中没有足够依据。"


def list_documents(db: Session) -> list[KnowledgeDocumentRead]:
    documents = list(
        db.scalars(
            select(KnowledgeDocument)
            .options(selectinload(KnowledgeDocument.chunks))
            .order_by(KnowledgeDocument.updated_at.desc())
        )
    )
    return [_serialize_document(document) for document in documents]


def get_document_model(
    db: Session,
    document_id: int,
) -> KnowledgeDocument:
    document = db.scalar(
        select(KnowledgeDocument)
        .options(selectinload(KnowledgeDocument.chunks))
        .where(KnowledgeDocument.id == document_id)
    )
    if document is None:
        raise ResourceNotFoundError(
            f"Knowledge document {document_id} was not found."
        )
    return document


def get_document(
    db: Session,
    document_id: int,
) -> KnowledgeDocumentDetail:
    return _serialize_document_detail(get_document_model(db, document_id))


def create_document(
    db: Session,
    payload: KnowledgeDocumentCreate,
) -> KnowledgeDocumentDetail:
    started_at = perf_counter()
    document = KnowledgeDocument(
        **payload.model_dump(exclude={"content"}),
        content=normalize_document(payload.content),
    )
    db.add(document)
    db.commit()
    document = get_document_model(db, document.id)
    harness_service.log_event(
        event_type="document_created",
        entity_type="knowledge_document",
        entity_id=document.id,
        input_payload={
            "title": document.title,
            "source_type": document.source_type.value,
            "content_length": len(document.content),
            "tags": document.tags,
        },
        output_payload={"document_id": document.id},
        latency_ms=(perf_counter() - started_at) * 1000,
    )
    return _serialize_document_detail(document)


def update_document(
    db: Session,
    document_id: int,
    payload: KnowledgeDocumentUpdate,
) -> KnowledgeDocumentDetail:
    document = get_document_model(db, document_id)
    changes = payload.model_dump(exclude_unset=True)
    content_changed = "content" in changes
    if content_changed:
        changes["content"] = normalize_document(changes["content"])
    for field, value in changes.items():
        setattr(document, field, value)
    if content_changed:
        db.execute(
            delete(KnowledgeChunk).where(
                KnowledgeChunk.document_id == document_id
            )
        )
    db.commit()
    if content_changed:
        _best_effort_delete_vectors(document_id)
    return _serialize_document_detail(get_document_model(db, document_id))


def delete_document(db: Session, document_id: int) -> int:
    document = get_document_model(db, document_id)
    _best_effort_delete_vectors(document_id)
    db.delete(document)
    db.commit()
    return document_id


def index_document(
    db: Session,
    document_id: int,
) -> DocumentIndexResult:
    started_at = perf_counter()
    document = get_document_model(db, document_id)
    chunks = chunk_markdown(
        document.content,
        document_id=document.id,
        title=document.title,
    )
    if not chunks:
        raise DependencyUnavailableError(
            "The document has no indexable Markdown or text content."
        )

    embedding_client = get_embedding_client()
    vector_store = get_vector_store()
    embeddings = embedding_client.embed_documents(
        [chunk.content for chunk in chunks]
    )
    if len(embeddings) != len(chunks):
        raise DependencyUnavailableError(
            "Embedding provider returned an unexpected vector count."
        )

    vector_store.delete_document(document.id)
    db.execute(
        delete(KnowledgeChunk).where(
            KnowledgeChunk.document_id == document.id
        )
    )
    db.commit()

    records = []
    for chunk in chunks:
        embedding_id = (
            f"document-{document.id}-chunk-{chunk.metadata['chunk_index']}"
        )
        record = KnowledgeChunk(
            document_id=document.id,
            chunk_index=chunk.metadata["chunk_index"],
            content=chunk.content,
            embedding_id=embedding_id,
            chunk_metadata=chunk.metadata,
        )
        db.add(record)
        records.append(record)
    db.flush()

    try:
        vector_store.upsert(
            ids=[record.embedding_id for record in records],
            embeddings=embeddings,
            documents=[record.content for record in records],
            metadatas=[
                {
                    **record.chunk_metadata,
                    "knowledge_chunk_id": record.id,
                }
                for record in records
            ],
        )
        db.commit()
    except Exception:
        db.rollback()
        vector_store.delete_document(document.id)
        raise

    result = DocumentIndexResult(
        document_id=document.id,
        chunk_count=len(records),
        embedding_provider=embedding_client.provider_name,
    )
    harness_service.log_event(
        event_type="document_indexed",
        entity_type="knowledge_document",
        entity_id=document.id,
        input_payload={
            "content_length": len(document.content),
            "chunking": {"min_size": 300, "max_size": 700, "overlap": 100},
        },
        output_payload=result.model_dump(mode="json"),
        latency_ms=(perf_counter() - started_at) * 1000,
    )
    return result


def search(
    db: Session,
    query: str,
    top_k: int,
) -> list[RAGSearchResult]:
    started_at = perf_counter()
    results = retrieve(db, query, top_k)
    harness_service.log_event(
        event_type="rag_searched",
        entity_type="rag_query",
        entity_id=_query_id(query),
        input_payload={"query": query, "top_k": top_k},
        output_payload={
            "result_count": len(results),
            "chunk_ids": [item.chunk_id for item in results],
        },
        latency_ms=(perf_counter() - started_at) * 1000,
    )
    return results


def ask(
    db: Session,
    question: str,
    top_k: int,
) -> RAGAnswer:
    started_at = perf_counter()
    results = search(db, question, top_k)
    sufficient = bool(
        results
        and results[0].similarity_score
        >= get_settings().rag_min_similarity
    )
    sources = [
        RAGSource(
            citation=f"[{index}]",
            chunk_id=result.chunk_id,
            document_id=result.document_id,
            document_title=result.document_title,
            heading=str(result.metadata.get("heading", "Document")),
            content=result.content,
            similarity_score=result.similarity_score,
        )
        for index, result in enumerate(results, start=1)
    ]

    if not sufficient:
        answer_text = INSUFFICIENT_ANSWER
    else:
        contexts = [
            (
                source.citation,
                (
                    f"Document: {source.document_title}\n"
                    f"Heading: {source.heading}\n{source.content}"
                ),
            )
            for source in sources
        ]
        try:
            cache_service.ensure_llm_allowed()
            answer_text = call_llm(
                build_rag_messages(question, contexts),
                temperature=0.1,
            ).strip()
            if not any(
                source.citation in answer_text for source in sources
            ):
                answer_text = INSUFFICIENT_ANSWER
                sufficient = False
        except RateLimitExceededError:
            raise
        except Exception as error:
            logger.warning(
                "RAG answer generation failed; using grounded fallback: %s",
                error,
            )
            excerpt = sources[0].content[:500]
            answer_text = f"根据知识库 {sources[0].citation}：{excerpt}"

    answer = RAGAnswer(
        answer=answer_text,
        has_sufficient_context=sufficient,
        sources=sources,
        retrieved_chunks=results,
    )
    harness_service.log_event(
        event_type="rag_answered",
        entity_type="rag_query",
        entity_id=_query_id(question),
        input_payload={"question": question, "top_k": top_k},
        output_payload={
            "has_sufficient_context": sufficient,
            "source_chunk_ids": [item.chunk_id for item in sources],
            "answer": answer_text,
        },
        latency_ms=(perf_counter() - started_at) * 1000,
    )
    return answer


def generate_quiz(
    db: Session,
    payload: RAGQuizRequest,
) -> RAGQuizResult:
    started_at = perf_counter()
    document = get_document_model(db, payload.document_id)
    headings = [
        section.heading
        for section in load_markdown_sections(document.content)
    ]
    generated = quiz_agent.generate(
        topic=payload.topic,
        learning_content=document.content,
        key_points=headings[:10],
        difficulty=(
            f"rag-{document.id}-{int(document.updated_at.timestamp())}"
        ),
    )
    questions = list(generated.questions[: payload.question_count])
    if len(questions) < payload.question_count:
        for question in quiz_agent.fallback(payload.topic).questions:
            if question.question not in {
                existing.question for existing in questions
            }:
                questions.append(question)
            if len(questions) == payload.question_count:
                break
    generated = QuizAgentOutput(
        topic=payload.topic,
        questions=questions,
    )

    goal = goal_service.get_today_goal(db)
    if goal is None:
        goal = goal_service.create_goal(
            db,
            DailyGoalCreate(
                title="完成个人知识库学习",
                description="基于个人 Agent 笔记完成知识检测。",
            ),
        )
    task = task_service.create_task(
        db,
        LearningTaskCreate(
            goal_id=goal.id,
            task_type=TaskType.AGENT_KNOWLEDGE,
            title=f"知识库检测：{payload.topic}",
            topic=f"rag-document:{document.id}",
            status=TaskStatus.COMPLETED,
        ),
    )
    session = quiz_service.create_generated_session(
        db,
        task=task,
        generated=generated,
        input_payload={
            "source": "rag_document",
            "document_id": document.id,
            "topic": payload.topic,
            "question_count": payload.question_count,
        },
        started_at=started_at,
    )
    result = RAGQuizResult(
        quiz_session_id=session.id,
        task_id=task.id,
        topic=session.topic,
        questions=[
            RAGQuizQuestion(
                id=answer.id,
                question=answer.question,
                question_type=answer.question_type,
            )
            for answer in session.answers
        ],
    )
    harness_service.log_event(
        event_type="rag_quiz_generated",
        entity_type="knowledge_document",
        entity_id=document.id,
        input_payload=payload.model_dump(mode="json"),
        output_payload={
            "quiz_session_id": session.id,
            "task_id": task.id,
            "question_count": len(result.questions),
        },
        latency_ms=(perf_counter() - started_at) * 1000,
    )
    return result


def _serialize_document(
    document: KnowledgeDocument,
) -> KnowledgeDocumentRead:
    return KnowledgeDocumentRead.model_validate(document).model_copy(
        update={
            "chunk_count": len(document.chunks),
            "is_indexed": bool(document.chunks),
        }
    )


def _serialize_document_detail(
    document: KnowledgeDocument,
) -> KnowledgeDocumentDetail:
    base = _serialize_document(document)
    return KnowledgeDocumentDetail(
        **base.model_dump(),
        chunks=[
            KnowledgeChunkRead.model_validate(chunk)
            for chunk in document.chunks
        ],
    )


def _best_effort_delete_vectors(document_id: int) -> None:
    try:
        get_vector_store().delete_document(document_id)
    except DependencyUnavailableError:
        return
    except Exception as error:
        logger.warning(
            "Could not remove stale Chroma vectors for document %s: %s",
            document_id,
            error,
        )


def _query_id(query: str) -> str:
    normalized = re.sub(r"\s+", "-", query.strip().lower())
    return normalized[:80] or "empty"
