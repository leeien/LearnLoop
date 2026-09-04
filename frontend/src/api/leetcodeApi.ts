import type { LeetCodeRecord } from "../types/models";
import { apiRequest } from "./client";

export const leetcodeApi = {
  list: () => apiRequest<LeetCodeRecord[]>("/api/leetcode/records"),
};

