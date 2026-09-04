import { useState } from "react";
import { Link } from "react-router-dom";

import { useStudyData } from "../../stores/StudyDataContext";
import { taskTypeLabels } from "../../utils/format";

export function FloatingStudyWidget() {
  const [isExpanded, setIsExpanded] = useState(true);
  const {
    todayGoal,
    tasks,
    isLoading,
    mutatingTaskId,
    pendingQuiz,
    reminderStatus,
    completeTask,
    skipTask,
  } = useStudyData();

  const completedCount = tasks.filter(
    (task) => task.status === "completed",
  ).length;
  const pendingTasks = tasks.filter((task) => task.status === "pending");
  const pendingQuizSessionId =
    pendingQuiz?.sessionId ?? reminderStatus?.pending_quiz_session_id;

  if (!isExpanded) {
    return (
      <button
        type="button"
        onClick={() => setIsExpanded(true)}
        className="fixed bottom-5 right-5 z-50 flex items-center gap-3 rounded-2xl bg-slate-950 px-4 py-3 text-left text-white shadow-2xl shadow-slate-900/30 transition hover:-translate-y-0.5 hover:bg-slate-900"
        aria-label="展开今日学习任务"
      >
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-cyan-400 font-bold text-slate-950">
          {completedCount}/{tasks.length}
        </span>
        <span>
          <span className="block text-sm font-semibold">今日学习</span>
          <span className="block text-xs text-slate-400">
            {pendingQuizSessionId
              ? "有检测待完成"
              : `${pendingTasks.length} 项待处理`}
          </span>
        </span>
      </button>
    );
  }

  return (
    <aside className="fixed bottom-4 right-4 z-50 w-[calc(100vw-2rem)] overflow-hidden rounded-2xl border border-slate-700 bg-slate-950 text-white shadow-2xl shadow-slate-950/30 sm:bottom-5 sm:right-5 sm:w-96">
      <div className="flex items-start justify-between border-b border-slate-800 px-5 py-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-cyan-400">
            Today
          </p>
          <h2 className="mt-1 font-semibold">学习任务</h2>
        </div>
        <button
          type="button"
          onClick={() => setIsExpanded(false)}
          className="rounded-lg px-2 py-1 text-lg text-slate-400 transition hover:bg-slate-800 hover:text-white"
          aria-label="收起学习任务"
        >
          −
        </button>
      </div>

      <div className="grid grid-cols-2 border-b border-slate-800">
        <div className="px-5 py-3">
          <p className="text-xs text-slate-500">今日任务</p>
          <p className="mt-1 text-xl font-semibold">{tasks.length}</p>
        </div>
        <div className="border-l border-slate-800 px-5 py-3">
          <p className="text-xs text-slate-500">已完成</p>
          <p className="mt-1 text-xl font-semibold text-emerald-400">
            {completedCount}
          </p>
        </div>
      </div>

      <div className="max-h-72 overflow-y-auto px-3 py-3">
        {isLoading ? (
          <p className="px-2 py-6 text-center text-sm text-slate-400">
            正在加载今日任务…
          </p>
        ) : !todayGoal ? (
          <p className="px-2 py-6 text-center text-sm text-slate-400">
            今日还没有学习目标
          </p>
        ) : pendingTasks.length === 0 ? (
          <p className="px-2 py-6 text-center text-sm text-emerald-400">
            今日待处理任务已清空
          </p>
        ) : (
          <ul className="space-y-2">
            {pendingTasks.map((task) => {
              const isMutating = mutatingTaskId === task.id;
              return (
                <li
                  key={task.id}
                  className="rounded-xl border border-slate-800 bg-slate-900 p-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{task.title}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {taskTypeLabels[task.task_type]}
                        {task.task_type === "agent_knowledge" && " · 待检测"}
                      </p>
                    </div>
                    <span className="shrink-0 text-xs text-slate-500">
                      {task.current_count}/{task.target_count}
                    </span>
                  </div>
                  <div className="mt-3 flex gap-2">
                    <button
                      type="button"
                      disabled={isMutating}
                      onClick={() => void completeTask(task.id)}
                      className="flex-1 rounded-lg bg-cyan-400 px-3 py-2 text-xs font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-wait disabled:opacity-60"
                    >
                      {isMutating ? "处理中…" : "完成"}
                    </button>
                    <button
                      type="button"
                      disabled={isMutating}
                      onClick={() => void skipTask(task.id)}
                      className="rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-300 transition hover:border-slate-500 hover:text-white disabled:cursor-wait disabled:opacity-60"
                    >
                      跳过
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <div className="border-t border-slate-800 bg-slate-900/70 px-5 py-3">
        {pendingQuizSessionId ? (
          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0">
              <p className="text-xs font-medium text-cyan-400">检测已生成</p>
              <p className="mt-1 truncate text-xs text-slate-400">
                {pendingQuiz?.taskTitle ?? "未完成的知识检测"}
              </p>
            </div>
            <Link
              to={`/quiz/${pendingQuizSessionId}`}
              className="shrink-0 rounded-lg bg-cyan-400 px-3 py-2 text-xs font-semibold text-slate-950 hover:bg-cyan-300"
            >
              开始检测
            </Link>
          </div>
        ) : (
          <div className="text-xs text-slate-500">
            <p>完成 Agent 知识任务后将自动生成检测</p>
            {reminderStatus?.needs_evening_review && (
              <p className="mt-1 text-amber-300">今晚需要生成每日复盘</p>
            )}
          </div>
        )}
      </div>
    </aside>
  );
}
