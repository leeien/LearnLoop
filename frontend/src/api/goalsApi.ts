import type {
  DailyGoal,
  GoalStatus,
  LearningTask,
} from "../types/models";
import { apiRequest } from "./client";

export interface CreateGoalInput {
  date?: string;
  title: string;
  description?: string;
}

export interface UpdateGoalInput {
  date?: string;
  title?: string;
  description?: string;
  status?: GoalStatus;
  completion_rate?: number;
}

export const goalsApi = {
  getToday: () => apiRequest<DailyGoal | null>("/api/goals/today"),

  create: (input: CreateGoalInput) =>
    apiRequest<DailyGoal>("/api/goals", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  planToday: () =>
    apiRequest<{ goal: DailyGoal; tasks: LearningTask[] }>(
      "/api/goals/plan",
      { method: "POST" },
    ),

  update: (goalId: number, input: UpdateGoalInput) =>
    apiRequest<DailyGoal>(`/api/goals/${goalId}`, {
      method: "PATCH",
      body: JSON.stringify(input),
    }),
};
