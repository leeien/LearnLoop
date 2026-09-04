import type { QuizSession } from "../types/models";
import { apiRequest } from "./client";

export interface QuizAnswerInput {
  answer_id: number;
  user_answer: string;
}

export const quizApi = {
  generate: (taskId: number) =>
    apiRequest<QuizSession>("/api/quiz/generate", {
      method: "POST",
      body: JSON.stringify({ task_id: taskId }),
    }),

  get: (sessionId: number) =>
    apiRequest<QuizSession>(`/api/quiz/${sessionId}`),

  submitAnswers: (sessionId: number, answers: QuizAnswerInput[]) =>
    apiRequest<QuizSession>(`/api/quiz/${sessionId}/answer`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    }),

  evaluate: (sessionId: number) =>
    apiRequest<QuizSession>(`/api/quiz/${sessionId}/evaluate`, {
      method: "POST",
    }),
};
