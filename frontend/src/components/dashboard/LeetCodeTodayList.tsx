import type { LeetCodeRecord } from "../../types/models";
import {
  formatTime,
  leetcodeDifficultyLabels,
} from "../../utils/format";

export function LeetCodeTodayList({
  records,
}: {
  records: LeetCodeRecord[];
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <h2 className="font-semibold">LeetCode 今日记录</h2>
        <p className="mt-1 text-xs text-slate-500">
          今日手动记录的刷题情况
        </p>
      </div>

      {records.length === 0 ? (
        <p className="px-5 py-10 text-center text-sm text-slate-400">
          今天还没有 LeetCode 学习记录
        </p>
      ) : (
        <ul className="divide-y divide-slate-100">
          {records.map((record) => (
            <li
              key={record.id}
              className="flex items-center justify-between gap-4 px-5 py-4"
            >
              <div>
                <p className="text-sm font-medium">
                  #{record.problem_number} {record.problem_title}
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  {leetcodeDifficultyLabels[record.difficulty]} ·{" "}
                  {record.tags.join(" / ") || "暂无标签"}
                </p>
              </div>
              <div className="text-right">
                <p
                  className={`text-xs font-medium ${
                    record.is_solved ? "text-emerald-600" : "text-amber-600"
                  }`}
                >
                  {record.is_solved ? "已解决" : "未解决"}
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  {formatTime(record.created_at)}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

