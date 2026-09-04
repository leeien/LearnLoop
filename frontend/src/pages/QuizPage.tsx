import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { quizApi } from "../api/quizApi";
import { EvaluatedAnswerCard } from "../components/quiz/EvaluatedAnswerCard";
import { EvaluationSummary } from "../components/quiz/EvaluationSummary";
import { questionTypeLabels } from "../components/quiz/questionLabels";
import { useStudyData } from "../stores/StudyDataContext";
import type { QuizSession } from "../types/models";

export default function QuizPage() {
  const { sessionId = "" } = useParams();
  const numericSessionId = Number(sessionId);
  const { clearPendingQuiz, refresh } = useStudyData();
  const [quiz, setQuiz] = useState<QuizSession | null>(null);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!Number.isInteger(numericSessionId) || numericSessionId <= 0) {
      setError("Quiz Session ID 无效");
      setIsLoading(false);
      return;
    }
    quizApi
      .get(numericSessionId)
      .then((result) => {
        setQuiz(result);
        if (result.status !== "pending") {
          clearPendingQuiz();
        }
        setAnswers(
          Object.fromEntries(
            result.answers.map((answer) => [
              answer.id,
              answer.user_answer ?? "",
            ]),
          ),
        );
      })
      .catch((requestError: unknown) => {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "检测加载失败",
        );
      })
      .finally(() => setIsLoading(false));
  }, [numericSessionId, clearPendingQuiz]);

  async function evaluateQuiz(session: QuizSession) {
    setIsEvaluating(true);
    setError(null);
    try {
      const evaluated = await quizApi.evaluate(session.id);
      setQuiz(evaluated);
      await refresh();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? `评分失败：${requestError.message}`
          : "评分失败，请重试",
      );
    } finally {
      setIsEvaluating(false);
    }
  }

  async function submitAnswers() {
    if (!quiz) {
      return;
    }
    const hasEmptyAnswer = quiz.answers.some(
      (answer) => !(answers[answer.id] ?? "").trim(),
    );
    if (hasEmptyAnswer) {
      setError("请回答全部问题后再提交。");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const saved = await quizApi.submitAnswers(
        quiz.id,
        quiz.answers.map((answer) => ({
          answer_id: answer.id,
          user_answer: answers[answer.id].trim(),
        })),
      );
      setQuiz(saved);
      clearPendingQuiz();
      setIsSubmitting(false);
      await evaluateQuiz(saved);
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "提交失败",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-16 text-center text-sm text-slate-500">
        正在加载检测问题…
      </main>
    );
  }

  if (!quiz) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-16">
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 text-rose-700">
          {error ?? "未找到检测会话"}
        </div>
        <Link to="/" className="mt-6 inline-block text-sm text-cyan-700">
          ← 返回 Dashboard
        </Link>
      </main>
    );
  }

  const isPending = quiz.status === "pending";
  const isAnswered = quiz.status === "answered";
  const isEvaluated = quiz.status === "evaluated";

  return (
    <main className="mx-auto max-w-4xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <Link
        to="/"
        className="text-sm font-medium text-slate-500 hover:text-slate-900"
      >
        ← 返回 Dashboard
      </Link>

      <section className="mt-6 rounded-3xl bg-slate-950 p-7 text-white sm:p-10">
        <p className="text-sm font-medium text-cyan-400">Knowledge Check</p>
        <h1 className="mt-3 text-3xl font-semibold">{quiz.topic}</h1>
        <p className="mt-3 text-sm leading-6 text-slate-400">
          共 {quiz.answers.length} 道题。提交后将按 40/30/20/10 Rubric
          自动评分。
        </p>
      </section>

      {error && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      {isEvaluating && (
        <div className="mt-6 rounded-xl border border-cyan-200 bg-cyan-50 px-4 py-3 text-sm text-cyan-700">
          Evaluator Agent 正在评估全部回答，请稍候…
        </div>
      )}

      {isEvaluated && <EvaluationSummary quiz={quiz} />}

      {isEvaluated ? (
        <ol className="mt-6 space-y-5">
          {quiz.answers.map((answer, index) => (
            <EvaluatedAnswerCard
              key={answer.id}
              answer={answer}
              index={index}
            />
          ))}
        </ol>
      ) : (
        <>
          {isAnswered && !isEvaluating && (
            <div className="mt-6 flex flex-col gap-4 rounded-xl border border-amber-200 bg-amber-50 p-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-amber-800">
                回答已保存，但尚未完成评分。
              </p>
              <button
                type="button"
                onClick={() => void evaluateQuiz(quiz)}
                className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-700"
              >
                重新评估
              </button>
            </div>
          )}

          <ol className="mt-6 space-y-5">
            {quiz.answers.map((answer, index) => (
              <li
                key={answer.id}
                className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
              >
                <div className="flex items-start gap-4">
                  <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-950 text-sm font-semibold text-white">
                    {index + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <span className="rounded-full bg-cyan-50 px-2.5 py-1 text-xs font-medium text-cyan-700">
                      {questionTypeLabels[answer.question_type]}
                    </span>
                    <p className="mt-3 font-medium leading-7">
                      {answer.question}
                    </p>
                    <label
                      htmlFor={`answer-${answer.id}`}
                      className="mt-5 block text-sm font-medium text-slate-600"
                    >
                      你的回答
                    </label>
                    <textarea
                      id={`answer-${answer.id}`}
                      value={answers[answer.id] ?? ""}
                      onChange={(event) =>
                        setAnswers((current) => ({
                          ...current,
                          [answer.id]: event.target.value,
                        }))
                      }
                      disabled={!isPending}
                      rows={5}
                      placeholder="结合概念、边界和工程实践回答…"
                      className="mt-2 w-full resize-y rounded-xl border border-slate-200 px-4 py-3 text-sm leading-6 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100 disabled:bg-slate-50 disabled:text-slate-600"
                    />
                  </div>
                </div>
              </li>
            ))}
          </ol>

          {isPending && (
            <button
              type="button"
              onClick={() => void submitAnswers()}
              disabled={isSubmitting || isEvaluating}
              className="mt-6 w-full rounded-xl bg-cyan-700 px-5 py-3.5 text-sm font-semibold text-white hover:bg-cyan-800 disabled:cursor-wait disabled:opacity-60"
            >
              {isSubmitting ? "正在保存回答…" : "提交并自动评分"}
            </button>
          )}
        </>
      )}
    </main>
  );
}
