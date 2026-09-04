import type { LearningHarnessLog } from "../../types/models";

const eventLabels: Record<string, string> = {
  task_completed: "Step 1：识别完成任务",
  quiz_generated: "Step 2：生成检测问题",
  answer_submitted: "Step 3：接收用户回答",
  answer_evaluated: "Step 4：评分与反馈",
  memory_created: "Step 5：写入 Memory",
  mastery_updated: "Step 6：更新掌握度",
  review_scheduled: "Step 7：安排复习",
  review_generated: "生成学习复盘",
  reminder_triggered: "更新学习提醒",
  tool_called: "调用受控工具",
};

function summarize(payload: Record<string, unknown>): string {
  const text = JSON.stringify(payload);
  if (text === "{}") return "无";
  return text.length > 140 ? `${text.slice(0, 140)}…` : text;
}

function PayloadBlock({
  title,
  payload,
}: {
  title: string;
  payload: Record<string, unknown>;
}) {
  return (
    <div>
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        {title}
      </p>
      <pre className="max-h-72 overflow-auto whitespace-pre-wrap break-all rounded-xl bg-slate-950 p-4 text-xs leading-5 text-slate-200">
        {JSON.stringify(payload, null, 2)}
      </pre>
    </div>
  );
}

export function TraceEventCard({ log }: { log: LearningHarnessLog }) {
  const succeeded = log.status === "success";

  return (
    <article className="relative pl-9">
      <span
        className={`absolute left-0 top-6 h-4 w-4 rounded-full border-4 border-white ${
          succeeded ? "bg-emerald-500" : "bg-rose-500"
        }`}
      />
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-slate-950">
              {eventLabels[log.event_type] ?? log.event_type}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              {log.event_type} · {log.entity_type}:{log.entity_id}
            </p>
          </div>
          <div className="text-right text-xs text-slate-500">
            <span
              className={`inline-flex rounded-full px-2 py-1 font-medium ${
                succeeded
                  ? "bg-emerald-50 text-emerald-700"
                  : "bg-rose-50 text-rose-700"
              }`}
            >
              {log.status}
            </span>
            <p className="mt-2">
              {new Date(log.created_at).toLocaleString("zh-CN")}
            </p>
            <p className="mt-1">{log.latency_ms} ms</p>
          </div>
        </div>

        <div className="mt-4 grid gap-3 text-xs text-slate-600 sm:grid-cols-2">
          <p className="rounded-xl bg-slate-50 p-3">
            <span className="font-semibold text-slate-800">输入摘要：</span>
            {summarize(log.input_payload)}
          </p>
          <p className="rounded-xl bg-slate-50 p-3">
            <span className="font-semibold text-slate-800">输出摘要：</span>
            {summarize(log.output_payload)}
          </p>
        </div>

        <details className="mt-4 rounded-xl border border-slate-200">
          <summary className="cursor-pointer px-4 py-3 text-sm font-medium text-slate-700">
            展开可审计 Payload
          </summary>
          <div className="grid gap-4 border-t border-slate-200 p-4 lg:grid-cols-2">
            <PayloadBlock title="Input" payload={log.input_payload} />
            <PayloadBlock title="Output" payload={log.output_payload} />
          </div>
        </details>
      </div>
    </article>
  );
}
