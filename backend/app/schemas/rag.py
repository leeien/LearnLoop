from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import KnowledgeSourceType, QuizQuestionType


class KnowledgeDocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    source_type: KnowledgeSourceType = KnowledgeSourceType.MARKDOWN
    content: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list, max_length=50)


class KnowledgeDocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    source_type: KnowledgeSourceType | None = None
    content: str | None = Field(default=None, min_length=1)
    tags: list[str] | None = Field(default=None, max_length=50)


class KnowledgeChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    chunk_index: int
    content: str
    embedding_id: str
    metadata: dict[str, Any] = Field(validation_alias="chunk_metadata")
    created_at: datetime


class KnowledgeDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source_type: KnowledgeSourceType
    content: str
    tags: list[str]
    chunk_count: int = 0
    is_indexed: bool = False
    created_at: datetime
    updated_at: datetime


class KnowledgeDocumentDetail(KnowledgeDocumentRead):
    chunks: list[KnowledgeChunkRead] = Field(default_factory=list)


class DocumentIndexResult(BaseModel):
    document_id: int
    chunk_count: int
    embedding_provider: str


class RAGSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class RAGSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    content: str
    similarity_score: float = Field(ge=0, le=1)
    metadata: dict[str, Any]


class RAGAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class RAGSource(BaseModel):
    citation: str
    chunk_id: int
    document_id: int
    document_title: str
    heading: str
    content: str
    similarity_score: float


class RAGAnswer(BaseModel):
    answer: str
    has_sufficient_context: bool
    sources: list[RAGSource]
    retrieved_chunks: list[RAGSearchResult]


class RAGQuizRequest(BaseModel):
    document_id: int = Field(gt=0)
    topic: str = Field(min_length=1, max_length=200)
    question_count: int = Field(default=5, ge=3, le=5)


class RAGQuizQuestion(BaseModel):
    id: int
    question: str
    question_type: QuizQuestionType


class RAGQuizResult(BaseModel):
    quiz_session_id: int
    task_id: int
    topic: str
    questions: list[RAGQuizQuestion]


class RAGDeleteResult(BaseModel):
    id: int
    deleted: bool = True
