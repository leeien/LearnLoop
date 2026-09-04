import { apiRequest } from "./client";

export interface ToolDefinition {
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
}

export const toolsApi = {
  list: () => apiRequest<ToolDefinition[]>("/api/tools/list"),

  call: <T>(toolName: string, argumentsPayload: Record<string, unknown>) =>
    apiRequest<{ tool_name: string; result: T }>("/api/tools/call", {
      method: "POST",
      body: JSON.stringify({
        tool_name: toolName,
        arguments: argumentsPayload,
      }),
    }).then((response) => response.result),
};
