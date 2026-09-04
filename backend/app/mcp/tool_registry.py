from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from pydantic import ValidationError

from app.core.exceptions import ServiceError
from app.services import harness_service


ToolHandler = Callable[[dict[str, Any]], Any]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler

    def public_definition(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            tool.public_definition()
            for tool in sorted(
                self._tools.values(),
                key=lambda item: item.name,
            )
        ]

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        started_at = perf_counter()
        tool = self._tools.get(tool_name)
        if tool is None:
            available = ", ".join(sorted(self._tools))
            error = ServiceError(
                f"Unknown tool '{tool_name}'. Available tools: {available}.",
                status_code=404,
            )
            self._log_failure(tool_name, arguments, error, started_at)
            raise error

        try:
            result = tool.handler(arguments)
        except ValidationError as error:
            message = _validation_message(error)
            harness_service.log_event(
                event_type="tool_called",
                entity_type="tool",
                entity_id=tool_name,
                input_payload={"arguments": arguments},
                output_payload={"error": message},
                status="failed",
                latency_ms=(perf_counter() - started_at) * 1000,
            )
            raise ServiceError(
                f"Invalid arguments for '{tool_name}': {message}",
                status_code=422,
            ) from error
        except ServiceError as error:
            self._log_failure(tool_name, arguments, error, started_at)
            raise
        except Exception as error:
            self._log_failure(tool_name, arguments, error, started_at)
            raise ServiceError(
                f"Tool '{tool_name}' failed: {error}",
                status_code=500,
            ) from error

        harness_service.log_event(
            event_type="tool_called",
            entity_type="tool",
            entity_id=tool_name,
            input_payload={"arguments": arguments},
            output_payload={"result": result},
            status="success",
            latency_ms=(perf_counter() - started_at) * 1000,
        )
        return result

    @staticmethod
    def _log_failure(
        tool_name: str,
        arguments: dict[str, Any],
        error: Exception,
        started_at: float,
    ) -> None:
        harness_service.log_event(
            event_type="tool_called",
            entity_type="tool",
            entity_id=tool_name,
            input_payload={"arguments": arguments},
            output_payload={
                "error_type": type(error).__name__,
                "error": str(error),
            },
            status="failed",
            latency_ms=(perf_counter() - started_at) * 1000,
        )


def _validation_message(error: ValidationError) -> str:
    messages = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"])
        messages.append(f"{location}: {item['msg']}")
    return "; ".join(messages)
