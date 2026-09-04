import type { DashboardSummary } from "../types/models";
import { apiRequest } from "./client";

export const dashboardApi = {
  getSummary: () =>
    apiRequest<DashboardSummary>("/api/dashboard/summary"),
};

