import type {
  KnowledgeDifficulty,
  LeetCodeDifficulty,
  TaskStatus,
  TaskType,
} from "../types/models";

export const taskTypeLabels: Record<TaskType, string> = {
  agent_knowledge: "Agent 知识",
  leetcode: "LeetCode",
  review: "复习",
  reflection: "复盘",
};

export const taskStatusLabels: Record<TaskStatus, string> = {
  pending: "待完成",
  completed: "已完成",
  skipped: "已跳过",
};

export const difficultyLabels: Record<KnowledgeDifficulty, string> = {
  beginner: "入门",
  intermediate: "进阶",
  advanced: "高级",
};

export const leetcodeDifficultyLabels: Record<LeetCodeDifficulty, string> = {
  easy: "简单",
  medium: "中等",
  hard: "困难",
};

export const categoryLabels: Record<string, string> = {
  foundations: "基础能力",
  tools: "工具调用",
  reasoning: "推理模式",
  memory: "记忆系统",
  retrieval: "检索增强",
  protocols: "Agent 协议",
  agents: "多智能体",
  learning: "学习复盘",
  observability: "可观测性",
  evaluation: "评估体系",
  governance: "治理与协作",
};

export function formatPercent(value: number): string {
  return `${Math.round(value)}%`;
}

export function isToday(isoDate: string): boolean {
  const value = new Date(isoDate);
  const today = new Date();
  return (
    value.getFullYear() === today.getFullYear() &&
    value.getMonth() === today.getMonth() &&
    value.getDate() === today.getDate()
  );
}

export function formatTime(isoDate: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(isoDate));
}

