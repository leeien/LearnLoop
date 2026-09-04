import type {
  KnowledgeDifficulty,
  TaskStatus,
  TaskType,
} from "../types/models";
import {
  difficultyLabels,
  taskStatusLabels,
  taskTypeLabels,
} from "../utils/format";

const statusStyles: Record<TaskStatus, string> = {
  pending: "bg-amber-50 text-amber-700 ring-amber-600/20",
  completed: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  skipped: "bg-slate-100 text-slate-600 ring-slate-500/20",
};

const difficultyStyles: Record<KnowledgeDifficulty, string> = {
  beginner: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  intermediate: "bg-blue-50 text-blue-700 ring-blue-600/20",
  advanced: "bg-violet-50 text-violet-700 ring-violet-600/20",
};

const baseClass =
  "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset";

export function TaskStatusBadge({ status }: { status: TaskStatus }) {
  return (
    <span className={`${baseClass} ${statusStyles[status]}`}>
      {taskStatusLabels[status]}
    </span>
  );
}

export function TaskTypeBadge({ type }: { type: TaskType }) {
  return (
    <span className={`${baseClass} bg-cyan-50 text-cyan-700 ring-cyan-600/20`}>
      {taskTypeLabels[type]}
    </span>
  );
}

export function DifficultyBadge({
  difficulty,
}: {
  difficulty: KnowledgeDifficulty;
}) {
  return (
    <span className={`${baseClass} ${difficultyStyles[difficulty]}`}>
      {difficultyLabels[difficulty]}
    </span>
  );
}

