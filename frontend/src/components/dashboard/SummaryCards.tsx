import type { DailyGoal, DashboardSummary } from "../../types/models";
import { formatPercent } from "../../utils/format";

interface SummaryCardsProps {
  goal: DailyGoal;
  summary: DashboardSummary | null;
  todayLeetCodeCount: number;
}

export function SummaryCards({
  goal,
  summary,
  todayLeetCodeCount,
}: SummaryCardsProps) {
  const cards = [
    {
      label: "今日完成率",
      value: formatPercent(goal.completion_rate),
      detail: goal.status === "completed" ? "今日目标已完成" : "继续保持节奏",
      tone: "from-cyan-500 to-blue-600",
    },
    {
      label: "任务进度",
      value: `${summary?.tasks.completed ?? 0}/${summary?.tasks.total ?? 0}`,
      detail: `${summary?.tasks.pending ?? 0} 项待完成`,
      tone: "from-violet-500 to-indigo-600",
    },
    {
      label: "知识掌握度",
      value: formatPercent(summary?.knowledge.average_mastery ?? 0),
      detail: `${summary?.knowledge.total_topics ?? 0} 个知识主题`,
      tone: "from-emerald-500 to-teal-600",
    },
    {
      label: "今日 LeetCode",
      value: String(todayLeetCodeCount),
      detail: `${summary?.leetcode.need_review ?? 0} 条记录待复习`,
      tone: "from-orange-500 to-rose-500",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <article
          key={card.label}
          className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
        >
          <div className={`h-1 bg-gradient-to-r ${card.tone}`} />
          <div className="p-5">
            <p className="text-sm text-slate-500">{card.label}</p>
            <p className="mt-3 text-3xl font-semibold tracking-tight">
              {card.value}
            </p>
            <p className="mt-2 text-xs text-slate-400">{card.detail}</p>
          </div>
        </article>
      ))}
    </div>
  );
}

