from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.rag import (
    DocumentIndexResult,
    KnowledgeDocumentCreate,
    KnowledgeDocumentDetail,
    KnowledgeDocumentRead,
    KnowledgeDocumentUpdate,
    RAGAnswer,
    RAGAskRequest,
    RAGDeleteResult,
    RAGQuizRequest,
    RAGQuizResult,
    RAGSearchRequest,
    RAGSearchResult,
)
from app.rag import rag_service


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post(
    "/documents",
    response_model=ApiResponse[KnowledgeDocumentDetail],
    status_code=201,
)
def create_document(
    payload: KnowledgeDocumentCreate,
    db: Session = Depends(get_db),
) -> ApiResponse[KnowledgeDocumentDetail]:
    document = rag_service.create_document(db, payload)
    return ApiResponse(data=document, message="Knowledge document was created.")


@router.get(
    "/documents",
    response_model=ApiResponse[list[KnowledgeDocumentRead]],
)
def list_documents(
    db: Session = Depends(get_db),
) -> ApiResponse[list[KnowledgeDocumentRead]]:
    return ApiResponse(
        data=rag_service.list_documents(db),
        message="Knowledge documents were retrieved.",
    )


@router.get(
    "/documents/{document_id}",
    response_model=ApiResponse[KnowledgeDocumentDetail],
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[KnowledgeDocumentDetail]:
    return ApiResponse(
        data=rag_service.get_document(db, document_id),
        message="Knowledge document was retrieved.",
    )


@router.patch(
    "/documents/{document_id}",
    response_model=ApiResponse[KnowledgeDocumentDetail],
)
def update_document(
    document_id: int,
    payload: KnowledgeDocumentUpdate,
    db: Session = Depends(get_db),
) -> ApiResponse[KnowledgeDocumentDetail]:
    document = rag_service.update_document(db, document_id, payload)
    return ApiResponse(data=document, message="Knowledge document was updated.")


@router.delete(
    "/documents/{document_id}",
    response_model=ApiResponse[RAGDeleteResult],
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[RAGDeleteResult]:
    deleted_id = rag_service.delete_document(db, document_id)
    return ApiResponse(
        data=RAGDeleteResult(id=deleted_id),
        message="Knowledge document was deleted.",
    )


@router.post(
    "/documents/{document_id}/index",
    response_model=ApiResponse[DocumentIndexResult],
)
def index_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[DocumentIndexResult]:
    result = rag_service.index_document(db, document_id)
    return ApiResponse(data=result, message="Knowledge document was indexed.")


@router.post(
    "/search",
    response_model=ApiResponse[list[RAGSearchResult]],
)
def search(
    payload: RAGSearchRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[list[RAGSearchResult]]:
    return ApiResponse(
        data=rag_service.search(db, payload.query, payload.top_k),
        message="Knowledge-base search was completed.",
    )


@router.post("/ask", response_model=ApiResponse[RAGAnswer])
def ask(
    payload: RAGAskRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[RAGAnswer]:
    return ApiResponse(
        data=rag_service.ask(db, payload.question, payload.top_k),
        message="Knowledge-base answer was generated.",
    )


@router.post(
    "/generate-quiz",
    response_model=ApiResponse[RAGQuizResult],
    status_code=201,
)
def generate_quiz(
    payload: RAGQuizRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[RAGQuizResult]:
    result = rag_service.generate_quiz(db, payload)
    return ApiResponse(
        data=result,
        message="Knowledge-base quiz was generated.",
    )
