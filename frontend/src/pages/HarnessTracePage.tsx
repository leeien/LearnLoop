import { useEffect, useState } from "react";

import { harnessApi } from "../api/harnessApi";
import { TraceEventCard } from "../components/harness/TraceEventCard";
import type { LearningHarnessLog } from "../types/models";

export default function HarnessTracePage() {
  const [logs, setLogs] = useState<LearningHarnessLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadTrace() {
    setIsLoading(true);
    setError(null);
    try {
      setLogs(await harnessApi.recentTrace(100));
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Trace 加载失败",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadTrace();
  }, []);

  return (
    <main className="mx-auto max-w-6xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-medium text-cyan-700">Learning Harness</p>
          <h1 className="mt-2 text-3xl font-semibold">可审计学习 Trace</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-500">
            展示任务、Quiz、评分、Memory、Mastery 和复盘的动作与结果。
            不包含模型隐藏思维链、完整系统提示词或敏感环境变量。
          </p>
        </div>
        <button
          type="button"
          onClick={() => void loadTrace()}
          disabled={isLoading}
          className="rounded-xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
        >
          {isLoading ? "加载中…" : "刷新 Trace"}
        </button>
      </div>

      {error && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      {!isLoading && logs.length === 0 ? (
        <div className="mt-8 rounded-3xl border border-dashed border-slate-300 bg-white py-16 text-center">
          <h2 className="text-lg font-semibold">还没有学习事件</h2>
          <p className="mt-2 text-sm text-slate-500">
            完成一个任务或 Quiz 后，这里会显示完整可审计流程。
          </p>
        </div>
      ) : (
        <div className="relative mt-8 space-y-5 before:absolute before:bottom-6 before:left-[7px] before:top-6 before:w-px before:bg-slate-200">
          {logs.map((log) => (
            <TraceEventCard key={log.id} log={log} />
          ))}
        </div>
      )}
    </main>
  );
}
