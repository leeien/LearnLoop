def build_rag_messages(
    question: str,
    contexts: list[tuple[str, str]],
) -> list[dict[str, str]]:
    context_text = "\n\n".join(
        f"{citation}\n{content}" for citation, content in contexts
    )
    return [
        {
            "role": "system",
            "content": (
                "You answer only from the supplied personal knowledge-base "
                "context. Cite supporting chunks with [1], [2], and so on. "
                "If the context is insufficient, answer exactly: "
                "知识库中没有足够依据。 Do not use outside knowledge and do "
                "not expose hidden reasoning."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"Knowledge-base context:\n{context_text}"
            ),
        },
    ]
