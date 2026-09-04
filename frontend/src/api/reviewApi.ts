import type { ReviewReport } from "../types/models";
import { apiRequest } from "./client";

export const reviewApi = {
  generateDaily: () =>
    apiRequest<ReviewReport>("/api/review/daily/generate", {
      method: "POST",
    }),

  listDaily: () => apiRequest<ReviewReport[]>("/api/review/daily"),

  listWeekly: () => apiRequest<ReviewReport[]>("/api/review/weekly"),
};

