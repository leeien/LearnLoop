import type { TopicMastery } from "../types/models";
import { apiRequest } from "./client";

export const masteryApi = {
  list: () => apiRequest<TopicMastery[]>("/api/mastery"),

  get: (topic: string) =>
    apiRequest<TopicMastery>(`/api/mastery/${topic}`),
};

