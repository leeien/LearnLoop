from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.schemas.rag import RAGSearchResult

from .embedding_client import get_embedding_client
from .vector_store import get_vector_store


def retrieve(
    db: Session,
    query: str,
    top_k: int,
) -> list[RAGSearchResult]:
    chunk_count = db.scalar(
        select(func.count()).select_from(KnowledgeChunk)
    )
    if not chunk_count:
        return []
    embedding = get_embedding_client().embed_query(query)
    raw = get_vector_store().query(
        query_embedding=embedding,
        top_k=min(max(top_k * 2, top_k), 40),
    )
    ids = (raw.get("ids") or [[]])[0]
    distances = (raw.get("distances") or [[]])[0]
    distance_by_id = dict(zip(ids, distances, strict=False))
    if not ids:
        return []

    chunks = list(
        db.scalars(
            select(KnowledgeChunk)
            .where(KnowledgeChunk.embedding_id.in_(ids))
        )
    )
    chunk_by_embedding = {chunk.embedding_id: chunk for chunk in chunks}
    document_ids = {chunk.document_id for chunk in chunks}
    documents = list(
        db.scalars(
            select(KnowledgeDocument).where(
                KnowledgeDocument.id.in_(document_ids)
            )
        )
    )
    title_by_id = {document.id: document.title for document in documents}

    results: list[RAGSearchResult] = []
    for embedding_id in ids:
        chunk = chunk_by_embedding.get(embedding_id)
        if chunk is None:
            continue
        distance = float(distance_by_id.get(embedding_id, 1.0))
        similarity = round(max(0.0, min(1.0, 1.0 - distance)), 4)
        results.append(
            RAGSearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_title=title_by_id.get(
                    chunk.document_id,
                    "Unknown document",
                ),
                content=chunk.content,
                similarity_score=similarity,
                metadata=chunk.chunk_metadata,
            )
        )
        if len(results) >= top_k:
            break
    return results
