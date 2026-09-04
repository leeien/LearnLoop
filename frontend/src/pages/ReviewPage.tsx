import { useState } from "react";

import { reviewApi } from "../api/reviewApi";
import { useStudyData } from "../stores/StudyDataContext";

function ListSection({
  title,
  items,
  emptyText,
}: {
  title: string;
  items: string[];
  emptyText: string;
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="font-semibold">{title}</h2>
      {items.length ? (
        <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-600">
          {items.map((item) => (
            <li key={item} className="flex gap-2">
              <span className="text-cyan-600">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-slate-400">{emptyText}</p>
      )}
    </section>
  );
}

export default function ReviewPage() {
  const { dailyReviews, refresh, error } = useStudyData();
  const [isGenerating, setIsGenerating] = useState(false);
  const report = dailyReviews[0] ?? null;

  async function generateReview() {
    setIsGenerating(true);
    try {
      await reviewApi.generateDaily();
      await refresh();
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-medium text-cyan-700">Reflection</p>
          <h1 className="mt-2 text-3xl font-semibold">每日复盘</h1>
          <p className="mt-3 text-sm text-slate-500">
            汇总任务、Quiz、Memory、LeetCode 和 Mastery 数据。
          </p>
        </div>
        <button
          type="button"
          onClick={() => void generateReview()}
          disabled={isGenerating || report !== null}
          className="rounded-xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isGenerating
            ? "正在生成…"
            : report
              ? "今日复盘已生成"
              : "生成今日复盘"}
        </button>
      </div>

      {error && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      {!report ? (
        <div className="mt-8 rounded-3xl border border-dashed border-slate-300 bg-white py-16 text-center">
          <h2 className="text-lg font-semibold">今天还没有复盘报告</h2>
          <p className="mt-2 text-sm text-slate-500">
            完成学习任务和检测后生成，数据不足时也会提供模板复盘。
          </p>
        </div>
      ) : (
        <>
          <section className="mt-8 rounded-3xl bg-slate-950 p-7 text-white sm:p-9">
            <p className="text-sm text-cyan-400">{report.date}</p>
            <h2 className="mt-3 text-2xl font-semibold">今日总结</h2>
            <p className="mt-4 leading-7 text-slate-300">{report.summary}</p>
          </section>
          <div className="mt-6 grid gap-5 md:grid-cols-2">
            <ListSection
              title="今日完成任务"
              items={report.completed_tasks}
              emptyText="今天没有已完成任务"
            />
            <ListSection
              title="未完成任务"
              items={report.unfinished_tasks}
              emptyText="没有未完成任务"
            />
            <ListSection
              title="今日薄弱点"
              items={report.weaknesses}
              emptyText="尚未识别薄弱点"
            />
            <ListSection
              title="今日收获"
              items={report.insights}
              emptyText="尚未记录学习收获"
            />
          </div>
          <div className="mt-5">
            <ListSection
              title="明日建议"
              items={report.next_actions}
              emptyText="暂无下一步建议"
            />
          </div>
        </>
      )}
    </main>
  );
}

