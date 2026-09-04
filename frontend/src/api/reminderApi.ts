import type { ReminderStatus } from "../types/models";
import { apiRequest } from "./client";

export const reminderApi = {
  getStatus: () =>
    apiRequest<ReminderStatus>("/api/reminder/status"),
  markReminded: () =>
    apiRequest<ReminderStatus>("/api/reminder/status", {
      method: "PATCH",
      body: JSON.stringify({ already_reminded: true }),
    }),
};
