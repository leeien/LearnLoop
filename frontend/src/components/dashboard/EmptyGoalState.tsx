import { useState } from "react";

import { useStudyData } from "../../stores/StudyDataContext";

export function EmptyGoalState() {
  const { createTodayPlan } = useStudyData();
  const [isCreating, setIsCreating] = useState(false);

  async function handleCreate() {
    setIsCreating(true);
    try {
      await createTodayPlan();
    } catch {
      // The shared store exposes the API error on the page.
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <section className="rounded-3xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center">
      <span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-cyan-50 text-2xl">
        ◎
      </span>
      <h2 className="mt-5 text-xl font-semibold">今天还没有学习目标</h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
        Goal Planner 会结合到期 Memory 和当前掌握度生成今日任务；模型不可用时
        使用确定性计划回退。
      </p>
      <button
        type="button"
        onClick={() => void handleCreate()}
        disabled={isCreating}
        className="mt-6 rounded-xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-wait disabled:opacity-60"
      >
        {isCreating ? "正在生成…" : "生成今日学习计划"}
      </button>
    </section>
  );
}
