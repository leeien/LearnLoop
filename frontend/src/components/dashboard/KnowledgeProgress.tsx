import { Link } from "react-router-dom";

import { useStudyData } from "../../stores/StudyDataContext";
import { categoryLabels, formatPercent } from "../../utils/format";
import { ProgressBar } from "../ProgressBar";

export function KnowledgeProgress() {
  const { knowledgeTopics, masteries, seedKnowledge } = useStudyData();
  const masteryByTopic = new Map(
    masteries.map((mastery) => [mastery.topic, mastery]),
  );
  const displayTopics = [...knowledgeTopics]
    .sort(
      (left, right) =>
        (masteryByTopic.get(right.topic_id)?.mastery_score ??
          right.mastery_score) -
        (masteryByTopic.get(left.topic_id)?.mastery_score ??
          left.mastery_score),
    )
    .slice(0, 6);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
        <div>
          <h2 className="font-semibold">Agent 知识进度</h2>
          <p className="mt-1 text-xs text-slate-500">
            当前掌握度概览
          </p>
        </div>
        <Link
          to="/knowledge"
          className="text-sm font-medium text-cyan-700 hover:text-cyan-900"
        >
          查看全部
        </Link>
      </div>

      {knowledgeTopics.length === 0 ? (
        <div className="px-5 py-10 text-center">
          <p className="text-sm text-slate-500">知识主题尚未初始化</p>
          <button
            type="button"
            onClick={() => void seedKnowledge().catch(() => undefined)}
            className="mt-4 rounded-lg bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700"
          >
            初始化知识主题
          </button>
        </div>
      ) : (
        <ul className="divide-y divide-slate-100">
          {displayTopics.map((topic) => {
            const mastery = masteryByTopic.get(topic.topic_id);
            const score = mastery?.mastery_score ?? topic.mastery_score;
            return (
              <li key={topic.id} className="px-5 py-4">
              <div className="flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <Link
                    to={`/knowledge/${topic.topic_id}`}
                    className="truncate text-sm font-medium hover:text-cyan-700"
                  >
                    {topic.title}
                  </Link>
                  <p className="mt-1 text-xs text-slate-400">
                    {categoryLabels[topic.category] ?? topic.category}
                  </p>
                </div>
                <span className="text-sm font-semibold text-slate-700">
                  {formatPercent(score)}
                </span>
              </div>
              <ProgressBar value={score} className="mt-3" />
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
