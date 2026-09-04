from dataclasses import dataclass
from typing import Any

from .document_loader import load_markdown_sections


@dataclass(frozen=True)
class DocumentChunk:
    content: str
    metadata: dict[str, Any]


def chunk_markdown(
    content: str,
    *,
    document_id: int,
    title: str,
    min_size: int = 300,
    max_size: int = 700,
    overlap: int = 100,
) -> list[DocumentChunk]:
    if not 0 <= overlap < max_size:
        raise ValueError("Chunk overlap must be non-negative and below max size.")
    if min_size <= 0 or min_size > max_size:
        raise ValueError("Chunk min size must be between 1 and max size.")

    chunks: list[DocumentChunk] = []
    for section in load_markdown_sections(content):
        start = 0
        text = section.content
        while start < len(text):
            end = min(start + max_size, len(text))
            if end < len(text):
                boundary = text.rfind("\n", start + min_size, end)
                if boundary > start:
                    end = boundary
            piece = text[start:end].strip()
            if piece:
                chunks.append(
                    DocumentChunk(
                        content=piece,
                        metadata={
                            "document_id": document_id,
                            "title": title,
                            "heading": section.heading,
                            "chunk_index": len(chunks),
                        },
                    )
                )
            if end >= len(text):
                break
            next_start = max(start + 1, end - overlap)
            start = next_start
    return chunks
