# LearnLoop Memory MCP-style Server

This directory implements a small, project-internal MCP-style boundary for
long-term learning memories. It is deliberately not a general MCP platform and
does not implement Prompt Engineering MCP.

## Scope

The server exposes exactly five registered tools:

- `memory.search`
- `memory.write`
- `memory.update`
- `memory.list_due_reviews`
- `memory.delete`

Every handler validates structured input and calls `memory_service`. Tool code
does not duplicate Memory SQL or lifecycle rules. SQLite remains the durable
data store.

`memory_mcp_server.py` owns one fixed `ToolRegistry`. The HTTP adapter exposes
the registry through:

```text
GET /api/tools/list
POST /api/tools/call
```

This is an internal MCP-style implementation, not yet an official MCP protocol
transport. It gives agents stable tool names, descriptions, JSON schemas and
audited calls while keeping the current deployment simple.

## Security boundary

- There is no API for dynamic tool registration.
- Tool names never map to dynamic imports, shell commands or filesystem paths.
- Tools only call approved `memory_service` methods.
- The server does not load or hold an LLM API key.
- It cannot read arbitrary files or access arbitrary system resources.
- Prompt resources and Prompt MCP are intentionally absent.
- Every success and failure is recorded as `tool_called` in Learning Harness.
- Harness sanitization redacts API keys, tokens, authorization values, secrets,
  passwords, system prompts and environment fields.

## Migration to an official MCP SDK

Keep `memory_tools.py` as the domain adapter and replace the current HTTP
transport with an official MCP server transport:

1. Register each existing tool definition with the SDK.
2. Reuse the same Pydantic input models and JSON schemas.
3. Keep handlers calling `memory_service`; do not move SQL into the transport.
4. Map `ServiceError` to MCP structured tool errors.
5. Preserve Harness logging around every tool invocation.
6. Add authentication and user/tenant context before exposing a remote
   transport.
7. Add protocol-level conformance tests for initialize, tools/list and
   tools/call.

Do not add shell, filesystem or Prompt MCP capabilities during this migration.
