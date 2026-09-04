import json
from typing import Any


def parse_json_object(raw_response: str, source: str) -> dict[str, Any]:
    content = raw_response.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    start = content.find("{")
    end = content.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"{source} response does not contain a JSON object.")

    payload = json.loads(content[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError(f"{source} response must be a JSON object.")
    return payload
