from typing import Any

from pydantic import BaseModel, Field


class ToolDefinitionRead(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]


class ToolCallRequest(BaseModel):
    tool_name: str = Field(min_length=1, max_length=100)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolCallResult(BaseModel):
    tool_name: str
    result: Any
