import type {
  LearningTask,
  TaskStatus,
  TaskType,
} from "../types/models";
import { apiRequest } from "./client";

export interface CreateTaskInput {
  goal_id: number;
  task_type: TaskType;
  title: string;
  topic?: string;
  target_count?: number;
  current_count?: number;
  status?: TaskStatus;
}

export interface TaskCompletionResult {
  task: LearningTask;
  quiz_session_id: number | null;
}

export const tasksApi = {
  getToday: () => apiRequest<LearningTask[]>("/api/tasks/today"),

  create: (input: CreateTaskInput) =>
    apiRequest<LearningTask>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  complete: (taskId: number) =>
    apiRequest<TaskCompletionResult>(`/api/tasks/${taskId}/complete`, {
      method: "PATCH",
    }),

  skip: (taskId: number) =>
    apiRequest<LearningTask>(`/api/tasks/${taskId}/skip`, {
      method: "PATCH",
    }),
};
