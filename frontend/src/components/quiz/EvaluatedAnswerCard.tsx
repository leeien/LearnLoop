import type { QuizAnswer } from "../../types/models";
import { questionTypeLabels } from "./questionLabels";

const dimensionItems = [
  ["概念准确性", "concept_accuracy", 40],
  ["关键点覆盖", "key_points_coverage", 30],
  ["工程理解", "engineering_understanding", 20],
  ["表达清晰度", "clarity", 10],
] as const;

export function EvaluatedAnswerCard({
  answer,
  index,
}: {
  answer: QuizAnswer;
  index: number;
}) {
  return (
    <li className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-col gap-4 border-b border-slate-100 p-5 sm:flex-row sm:items-start sm:justify-between sm:p-6">
        <div className="flex gap-4">
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-950 text-sm font-semibold text-white">
            {index + 1}
          </span>
          <div>
            <span className="rounded-full bg-cyan-50 px-2.5 py-1 text-xs font-medium text-cyan-700">
              {questionTypeLabels[answer.question_type]}
            </span>
            <p className="mt-3 font-medium leading-7">{answer.question}</p>
          </div>
        </div>
        <div
          className={`shrink-0 rounded-xl px-4 py-2 text-center ${
            answer.is_passed
              ? "bg-emerald-50 text-emerald-700"
              : "bg-amber-50 text-amber-700"
          }`}
        >
          <strong className="text-xl">{Math.round(answer.score ?? 0)}</strong>
          <span className="ml-1 text-xs">/100</span>
        </div>
      </div>

      <div className="space-y-6 p-5 sm:p-6">
        <div>
          <h3 className="text-sm font-semibold text-slate-700">你的回答</h3>
          <p className="mt-2 whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">
            {answer.user_answer}
          </p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {dimensionItems.map(([label, key, maxScore]) => (
            <div key={key} className="rounded-xl border border-slate-100 p-3">
              <p className="text-xs text-slate-500">{label}</p>
              <p className="mt-1 font-semibold">
                {answer[key] ?? 0}
                <span className="text-xs font-normal text-slate-400">
                  /{maxScore}
                </span>
              </p>
            </div>
          ))}
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl bg-emerald-50 p-4">
            <h3 className="text-sm font-semibold text-emerald-800">优点</h3>
            <ul className="mt-2 space-y-2 text-sm leading-6 text-emerald-700">
              {(answer.strengths ?? []).map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl bg-amber-50 p-4">
            <h3 className="text-sm font-semibold text-amber-800">薄弱点</h3>
            <ul className="mt-2 space-y-2 text-sm leading-6 text-amber-700">
              {(answer.weaknesses ?? []).map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="rounded-xl border border-cyan-100 bg-cyan-50/60 p-4">
          <h3 className="text-sm font-semibold text-cyan-900">修正答案</h3>
          <p className="mt-2 text-sm leading-6 text-cyan-900/75">
            {answer.corrected_answer}
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
          <p className="whitespace-pre-line text-slate-500">
            {answer.feedback}
          </p>
          <span className="rounded-full bg-violet-50 px-3 py-1.5 text-xs font-medium text-violet-700">
            建议 {answer.next_review_days ?? 1} 天后复习
          </span>
        </div>
      </div>
    </li>
  );
}

