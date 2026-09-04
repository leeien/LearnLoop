from fastapi import APIRouter

from app.mcp.memory_mcp_server import memory_mcp_server
from app.schemas.common import ApiResponse
from app.schemas.tools import (
    ToolCallRequest,
    ToolCallResult,
    ToolDefinitionRead,
)


router = APIRouter(prefix="/tools", tags=["tools"])


@router.get(
    "/list",
    response_model=ApiResponse[list[ToolDefinitionRead]],
)
def list_tools() -> ApiResponse[list[ToolDefinitionRead]]:
    return ApiResponse(
        data=memory_mcp_server.list_tools(),
        message="Registered Memory MCP tools were retrieved.",
    )


@router.post(
    "/call",
    response_model=ApiResponse[ToolCallResult],
)
def call_tool(
    payload: ToolCallRequest,
) -> ApiResponse[ToolCallResult]:
    result = memory_mcp_server.call_tool(
        payload.tool_name,
        payload.arguments,
    )
    return ApiResponse(
        data=ToolCallResult(
            tool_name=payload.tool_name,
            result=result,
        ),
        message=f"Tool '{payload.tool_name}' completed.",
    )
