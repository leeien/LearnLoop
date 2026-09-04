from typing import Any

from .memory_tools import register_memory_tools
from .tool_registry import ToolRegistry


class MemoryMCPServer:
    """Small internal MCP-style boundary for LearnLoop Memory tools."""

    def __init__(self) -> None:
        self.registry = ToolRegistry()
        register_memory_tools(self.registry)

    def list_tools(self) -> list[dict[str, Any]]:
        return self.registry.list_tools()

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        return self.registry.call_tool(tool_name, arguments)


memory_mcp_server = MemoryMCPServer()
