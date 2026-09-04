import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { DifficultyBadge } from "../components/StatusBadge";
import { ProgressBar } from "../components/ProgressBar";
import { useStudyData } from "../stores/StudyDataContext";
import type { KnowledgeTopic } from "../types/models";
import {
  categoryLabels,
  formatPercent,
} from "../utils/format";

export default function KnowledgeTopicsPage() {
  const {
    knowledgeTopics,
    seedKnowledge,
    isLoading,
    error,
  } = useStudyData();
  const [isSeeding, setIsSeeding] = useState(false);

  const groupedTopics = useMemo(() => {
    return knowledgeTopics.reduce<Record<string, KnowledgeTopic[]>>(
      (groups, topic) => {
        (groups[topic.category] ??= []).push(topic);
        return groups;
      },
      {},
    );
  }, [knowledgeTopics]);

  async function handleSeed() {
    setIsSeeding(true);
    try {
      await seedKnowledge();
    } catch {
      // The shared store renders the request error.
    } finally {
      setIsSeeding(false);
    }
  }

  return (
    <main className="mx-auto max-w-7xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-medium text-cyan-700">Knowledge Map</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">
            Agent 知识主题
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
            按能力域浏览 Agent
            专业知识。本阶段展示后端保存的掌握度，不自动计算或更新分数。
          </p>
        </div>
        {knowledgeTopics.length > 0 && (
          <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm">
            <span className="text-slate-500">主题总数</span>
            <strong className="ml-3 text-lg">{knowledgeTopics.length}</strong>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          后端请求失败：{error}
        </div>
      )}

      {isLoading ? (
        <div className="mt-8 grid animate-pulse gap-4 md:grid-cols-2 xl:grid-cols-3">
          {[0, 1, 2, 3, 4, 5].map((item) => (
            <div key={item} className="h-48 rounded-2xl bg-slate-200" />
          ))}
        </div>
      ) : knowledgeTopics.length === 0 ? (
        <section className="mt-8 rounded-3xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center">
          <h2 className="text-xl font-semibold">知识主题尚未初始化</h2>
          <p className="mt-2 text-sm text-slate-500">
            初始化后将创建 25 个 Agent 核心知识主题。
          </p>
          <button
            type="button"
            onClick={() => void handleSeed()}
            disabled={isSeeding}
            className="mt-6 rounded-xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60"
          >
            {isSeeding ? "正在初始化…" : "初始化知识主题"}
          </button>
        </section>
      ) : (
        <div className="mt-10 space-y-10">
          {Object.entries(groupedTopics).map(([category, topics]) => (
            <section key={category}>
              <div className="mb-4 flex items-center gap-3">
                <h2 className="text-lg font-semibold">
                  {categoryLabels[category] ?? category}
                </h2>
                <span className="rounded-full bg-slate-200 px-2.5 py-1 text-xs text-slate-600">
                  {topics.length}
                </span>
              </div>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {topics.map((topic) => (
                  <Link
                    key={topic.id}
                    to={`/knowledge/${topic.topic_id}`}
                    className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-cyan-300 hover:shadow-md"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          {categoryLabels[topic.category] ?? topic.category}
                        </p>
                        <h3 className="mt-2 font-semibold group-hover:text-cyan-700">
                          {topic.title}
                        </h3>
                      </div>
                      <DifficultyBadge difficulty={topic.difficulty} />
                    </div>
                    <p className="mt-4 line-clamp-2 text-sm leading-6 text-slate-500">
                      {topic.description}
                    </p>
                    <div className="mt-5 flex items-center justify-between text-xs">
                      <span className="text-slate-400">掌握度</span>
                      <strong className="text-slate-700">
                        {formatPercent(topic.mastery_score)}
                      </strong>
                    </div>
                    <ProgressBar value={topic.mastery_score} className="mt-2" />
                  </Link>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </main>
  );
}

