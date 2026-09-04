import type { LearningHarnessLog } from "../types/models";
import { apiRequest } from "./client";

export const harnessApi = {
  list: (filters?: {
    eventType?: string;
    entityType?: string;
    status?: string;
    limit?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.eventType) params.set("event_type", filters.eventType);
    if (filters?.entityType) {
      params.set("entity_type", filters.entityType);
    }
    if (filters?.status) params.set("status", filters.status);
    if (filters?.limit) params.set("limit", String(filters.limit));
    const query = params.toString();
    return apiRequest<LearningHarnessLog[]>(
      `/api/harness/logs${query ? `?${query}` : ""}`,
    );
  },

  listByEntity: (entityType: string, entityId: string, limit = 100) =>
    apiRequest<LearningHarnessLog[]>(
      `/api/harness/logs/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}?limit=${limit}`,
    ),

  recentTrace: (limit = 50) =>
    apiRequest<LearningHarnessLog[]>(
      `/api/harness/recent-trace?limit=${limit}`,
    ),
};
