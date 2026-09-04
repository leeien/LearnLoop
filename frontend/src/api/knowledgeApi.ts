import type { KnowledgeTopic } from "../types/models";
import { apiRequest } from "./client";

export interface KnowledgeSeedResult {
  created: number;
  total: number;
}

export const knowledgeApi = {
  list: () => apiRequest<KnowledgeTopic[]>("/api/knowledge/topics"),

  get: (topicId: string) =>
    apiRequest<KnowledgeTopic>(`/api/knowledge/topics/${topicId}`),

  seed: () =>
    apiRequest<KnowledgeSeedResult>("/api/knowledge/topics/seed", {
      method: "POST",
    }),
};

