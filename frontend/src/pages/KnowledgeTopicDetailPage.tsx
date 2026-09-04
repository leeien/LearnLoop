import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { knowledgeApi } from "../api/knowledgeApi";
import { tasksApi } from "../api/tasksApi";
import { DifficultyBadge } from "../components/StatusBadge";
import { ProgressBar } from "../components/ProgressBar";
import { useStudyData } from "../stores/StudyDataContext";
import type { KnowledgeTopic } from "../types/models";
import {
  categoryLabels,
  formatPercent,
} from "../utils/format";

export default function KnowledgeTopicDetailPage() {
  const { topicId = "" } = useParams();
  const navigate = useNavigate();
  const {
    knowledgeTopics,
    todayGoal,
    tasks,
    completeTask,
  } = useStudyData();
  const cachedTopic = knowledgeTopics.find(
    (item) => item.topic_id === topicId,
  );
  const [topic, setTopic] = useState<KnowledgeTopic | null>(
    cachedTopic ?? null,
  );
  const [isLoading, setIsLoading] = useState(!cachedTopic);
  const [isCompleting, setIsCompleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);
    setError(null);
    knowledgeApi
      .get(topicId)
      .then(setTopic)
      .catch((requestError: unknown) => {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "知识主题加载失败",
        );
      })
      .finally(() => setIsLoading(false));
  }, [topicId]);

  const matchingTasks = useMemo(
    () =>
      tasks.filter(
        (task) =>
          task.task_type === "agent_knowledge" && task.topic === topicId,
      ),
    [tasks, topicId],
  );
  const isCompletedToday = matchingTasks.some(
    (task) => task.status === "completed",
  );

  async function markLearningComplete() {
    if (!topic || !todayGoal || isCompletedToday) {
      return;
    }
    setIsCompleting(true);
    setError(null);
    try {
      let task = matchingTasks.find((item) => item.status === "pending");
      if (!task) {
        task = await tasksApi.create({
          goal_id: todayGoal.id,
          task_type: "agent_knowledge",
          title: `学习 ${topic.title}`,
          topic: topic.topic_id,
        });
      }
      const quizSessionId = await completeTask(task.id);
      if (quizSessionId !== null) {
        navigate(`/quiz/${quizSessionId}`);
        return;
      }
      setError("任务完成后未获得检测会话，请稍后重试。");
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "操作失败",
      );
    } finally {
      setIsCompleting(false);
    }
  }

  if (isLoading && !topic) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-16 text-center text-sm text-slate-500">
        正在加载知识主题…
      </main>
    );
  }

  if (!topic) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-16">
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 text-rose-700">
          {error ?? "未找到该知识主题"}
        </div>
        <Link
          to="/knowledge"
          className="mt-6 inline-block text-sm font-medium text-cyan-700"
        >
          ← 返回知识主题
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-5xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <Link
        to="/knowledge"
        className="text-sm font-medium text-slate-500 hover:text-slate-900"
      >
        ← 返回知识主题
      </Link>

      <section className="mt-6 overflow-hidden rounded-3xl bg-slate-950 text-white shadow-xl">
        <div className="p-7 sm:p-10">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-sm text-cyan-400">
              {categoryLabels[topic.category] ?? topic.category}
            </span>
            <DifficultyBadge difficulty={topic.difficulty} />
          </div>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight sm:text-4xl">
            {topic.title}
          </h1>
          <p className="mt-4 max-w-3xl leading-7 text-slate-300">
            {topic.description}
          </p>
          <div className="mt-8 max-w-md">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="text-slate-400">当前掌握度</span>
              <strong>{formatPercent(topic.mastery_score)}</strong>
            </div>
            <ProgressBar value={topic.mastery_score} />
          </div>
        </div>
      </section>

      {error && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      )}
      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_0.7fr]">
        <div className="space-y-6">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold">概念解释</h2>
            <p className="mt-4 leading-7 text-slate-600">
              {topic.learning_content}
            </p>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold">关键要点</h2>
            <ul className="mt-4 space-y-3">
              {topic.key_points.map((point) => (
                <li key={point} className="flex gap-3 text-slate-600">
                  <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-cyan-500" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </section>
        </div>

        <div className="space-y-6">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold">常见问题</h2>
            <ol className="mt-4 space-y-4">
              {topic.common_questions.map((question, index) => (
                <li key={question} className="flex gap-3 text-sm text-slate-600">
                  <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-slate-100 text-xs font-semibold">
                    {index + 1}
                  </span>
                  <span className="pt-0.5 leading-6">{question}</span>
                </li>
              ))}
            </ol>
          </section>

          <section className="rounded-2xl border border-cyan-200 bg-cyan-50 p-6">
            <h2 className="font-semibold text-cyan-950">今日学习记录</h2>
            <p className="mt-2 text-sm leading-6 text-cyan-800/70">
              标记完成会调用真实任务 API 并自动生成知识检测；提交评分后将更新
              Memory、掌握度和复习时间。
            </p>
            <button
              type="button"
              onClick={() => void markLearningComplete()}
              disabled={!todayGoal || isCompletedToday || isCompleting}
              className="mt-5 w-full rounded-xl bg-cyan-700 px-4 py-3 text-sm font-semibold text-white hover:bg-cyan-800 disabled:cursor-not-allowed disabled:bg-cyan-300"
            >
              {isCompleting
                ? "正在记录…"
                : isCompletedToday
                  ? "今日已完成"
                  : !todayGoal
                    ? "请先创建今日目标"
                    : "标记学习完成"}
            </button>
          </section>
        </div>
      </div>
    </main>
  );
}
