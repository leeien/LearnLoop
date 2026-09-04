import { Link } from "react-router-dom";

import { useStudyData } from "../../stores/StudyDataContext";

const memoryLabels: Record<string, string> = {
  weakness_memory: "薄弱点",
  mistake_memory: "错因",
  insight_memory: "收获",
  review_memory: "复习",
  goal_memory: "目标",
  completion_memory: "完成记录",
};

export function RecentMemory() {
  const { memories } = useStudyData();
  const recent = [...memories]
    .sort((left, right) => right.created_at.localeCompare(left.created_at))
    .slice(0, 4);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
        <div>
          <h2 className="font-semibold">最近 Memory</h2>
          <p className="mt-1 text-xs text-slate-500">长期价值学习信息</p>
        </div>
        <Link to="/memory" className="text-sm font-medium text-cyan-700">
          查看全部
        </Link>
      </div>
      {recent.length === 0 ? (
        <p className="px-5 py-9 text-center text-sm text-slate-400">
          完成 Quiz 评估后会自动提取薄弱点
        </p>
      ) : (
        <ul className="divide-y divide-slate-100">
          {recent.map((memory) => (
            <li key={memory.id} className="px-5 py-4">
              <div className="flex items-center justify-between gap-3">
                <span className="rounded-full bg-violet-50 px-2.5 py-1 text-xs font-medium text-violet-700">
                  {memoryLabels[memory.memory_type]}
                </span>
                <span className="text-xs text-slate-400">{memory.topic}</span>
              </div>
              <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-600">
                {memory.content}
              </p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

