import { Link } from "react-router-dom";

import { useStudyData } from "../../stores/StudyDataContext";

export function DailyReviewSummary() {
  const { dailyReviews } = useStudyData();
  const today = new Date().toLocaleDateString("sv-SE");
  const report = dailyReviews.find((item) => item.date === today);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <h2 className="font-semibold">今日复盘</h2>
        <Link to="/review" className="text-sm font-medium text-cyan-700">
          {report ? "查看详情" : "生成复盘"}
        </Link>
      </div>
      {report ? (
        <>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            {report.summary}
          </p>
          <div className="mt-4 flex gap-4 text-xs text-slate-500">
            <span>完成 {report.completed_tasks.length}</span>
            <span>未完成 {report.unfinished_tasks.length}</span>
            <span>薄弱点 {report.weaknesses.length}</span>
          </div>
        </>
      ) : (
        <p className="mt-3 text-sm leading-6 text-slate-400">
          今天还没有复盘报告。完成学习后可生成基础复盘。
        </p>
      )}
    </section>
  );
}

