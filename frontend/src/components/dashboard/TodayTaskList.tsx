import { useStudyData } from "../../stores/StudyDataContext";
import type { LearningTask } from "../../types/models";
import { TaskStatusBadge, TaskTypeBadge } from "../StatusBadge";

function TaskRow({ task }: { task: LearningTask }) {
  const { completeTask, skipTask, mutatingTaskId } = useStudyData();
  const isMutating = mutatingTaskId === task.id;

  return (
    <li className="flex flex-col gap-4 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="font-medium text-slate-900">{task.title}</h3>
          <TaskTypeBadge type={task.task_type} />
          <TaskStatusBadge status={task.status} />
        </div>
        <p className="mt-2 text-sm text-slate-500">
          {task.topic ? `主题：${task.topic}` : "通用学习任务"} · 进度{" "}
          {task.current_count}/{task.target_count}
        </p>
      </div>

      {task.status === "pending" && (
        <div className="flex shrink-0 gap-2">
          <button
            type="button"
            disabled={isMutating}
            onClick={() => void completeTask(task.id)}
            className="rounded-lg bg-slate-950 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60"
          >
            完成
          </button>
          <button
            type="button"
            disabled={isMutating}
            onClick={() => void skipTask(task.id)}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:border-slate-300 hover:bg-slate-50 disabled:opacity-60"
          >
            跳过
          </button>
        </div>
      )}
    </li>
  );
}

export function TodayTaskList() {
  const { tasks } = useStudyData();

  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
        <div>
          <h2 className="font-semibold">今日任务</h2>
          <p className="mt-1 text-xs text-slate-500">
            完成状态会同步到右下角悬浮框
          </p>
        </div>
        <span className="text-sm text-slate-400">{tasks.length} 项</span>
      </div>
      {tasks.length === 0 ? (
        <p className="px-5 py-10 text-center text-sm text-slate-400">
          当前目标还没有任务
        </p>
      ) : (
        <ul className="divide-y divide-slate-100">
          {tasks.map((task) => (
            <TaskRow key={task.id} task={task} />
          ))}
        </ul>
      )}
    </section>
  );
}

