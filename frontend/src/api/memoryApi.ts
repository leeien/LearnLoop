import type { Memory, MemoryType } from "../types/models";
import { apiRequest } from "./client";

export interface MemoryCreateInput {
  memory_type: MemoryType;
  topic: string;
  content: string;
  source?: string;
  importance?: number;
  confidence?: number;
  next_review_at?: string | null;
  tags?: string[];
}

export type MemoryUpdateInput = Partial<MemoryCreateInput>;

export const memoryApi = {
  list: (filters?: { memoryType?: MemoryType; topic?: string }) => {
    const params = new URLSearchParams();
    if (filters?.memoryType) {
      params.set("memory_type", filters.memoryType);
    }
    if (filters?.topic) {
      params.set("topic", filters.topic);
    }
    const query = params.toString();
    return apiRequest<Memory[]>(`/api/memory${query ? `?${query}` : ""}`);
  },

  create: (input: MemoryCreateInput) =>
    apiRequest<Memory>("/api/memory", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  update: (memoryId: number, input: MemoryUpdateInput) =>
    apiRequest<Memory>(`/api/memory/${memoryId}`, {
      method: "PATCH",
      body: JSON.stringify(input),
    }),

  delete: (memoryId: number) =>
    apiRequest<{ id: number }>(`/api/memory/${memoryId}`, {
      method: "DELETE",
    }),
};

