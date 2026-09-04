from functools import lru_cache
from typing import Any

from app.core.config import get_settings
from app.core.exceptions import DependencyUnavailableError


class ChromaVectorStore:
    collection_name = "learnloop_knowledge"

    def __init__(self, persist_directory: str) -> None:
        try:
            import chromadb
        except ImportError as error:
            raise DependencyUnavailableError(
                "Chroma is unavailable. Install 'chromadb' from "
                "backend/requirements.txt."
            ) from error
        try:
            client = chromadb.PersistentClient(path=persist_directory)
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as error:
            raise DependencyUnavailableError(
                f"Chroma could not initialize at '{persist_directory}': {error}"
            ) from error

    def upsert(
        self,
        *,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        try:
            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        except Exception as error:
            raise DependencyUnavailableError(
                f"Chroma upsert failed: {error}"
            ) from error

    def delete_document(self, document_id: int) -> None:
        try:
            self._collection.delete(where={"document_id": document_id})
        except Exception as error:
            raise DependencyUnavailableError(
                f"Chroma delete failed: {error}"
            ) from error

    def query(
        self,
        *,
        query_embedding: list[float],
        top_k: int,
    ) -> dict[str, Any]:
        try:
            return self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["distances", "metadatas", "documents"],
            )
        except Exception as error:
            raise DependencyUnavailableError(
                f"Chroma query failed: {error}"
            ) from error


@lru_cache
def get_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore(get_settings().chroma_persist_dir)
