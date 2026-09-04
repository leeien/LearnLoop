import type { QuizSession } from "../../types/models";

export function EvaluationSummary({ quiz }: { quiz: QuizSession }) {
  const score = quiz.total_score ?? 0;
  const passed = quiz.is_passed === true;
  const reviewDays = Math.min(
    ...quiz.answers.map((answer) => answer.next_review_days ?? 1),
  );

  return (
    <section
      className={`mt-6 overflow-hidden rounded-2xl border ${
        passed
          ? "border-emerald-200 bg-emerald-50"
          : "border-amber-200 bg-amber-50"
      }`}
    >
      <div className="grid gap-6 p-6 sm:grid-cols-[auto_1fr_auto] sm:items-center">
        <div
          className={`grid h-24 w-24 place-items-center rounded-2xl text-3xl font-bold ${
            passed
              ? "bg-emerald-600 text-white"
              : "bg-amber-500 text-white"
          }`}
        >
          {Math.round(score)}
        </div>
        <div>
          <p
            className={`text-sm font-semibold ${
              passed ? "text-emerald-700" : "text-amber-700"
            }`}
          >
            {passed ? "检测通过" : "需要继续复习"}
          </p>
          <h2 className="mt-2 text-xl font-semibold text-slate-900">
            Rubric 综合评分
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            {quiz.summary}
          </p>
        </div>
        <div className="rounded-xl bg-white/70 px-4 py-3 text-center">
          <p className="text-xs text-slate-500">建议复习</p>
          <p className="mt-1 text-lg font-semibold text-slate-900">
            {reviewDays} 天后
          </p>
        </div>
      </div>
    </section>
  );
}

