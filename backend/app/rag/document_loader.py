import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MarkdownSection:
    heading: str
    content: str


def normalize_document(content: str) -> str:
    normalized = content.lstrip("\ufeff").replace("\r\n", "\n")
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def load_markdown_sections(content: str) -> list[MarkdownSection]:
    text = normalize_document(content)
    if not text:
        return []

    sections: list[MarkdownSection] = []
    heading = "Document"
    body: list[str] = []

    def flush() -> None:
        section_content = "\n".join(body).strip()
        if section_content:
            sections.append(
                MarkdownSection(
                    heading=heading,
                    content=section_content,
                )
            )

    for line in text.splitlines():
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
        if match:
            flush()
            heading = match.group(1).strip()
            body = []
        else:
            body.append(line)
    flush()

    if not sections:
        sections.append(MarkdownSection(heading="Document", content=text))
    return sections
