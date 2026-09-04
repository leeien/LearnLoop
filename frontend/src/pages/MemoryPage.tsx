import { useMemo, useState } from "react";

import { memoryApi } from "../api/memoryApi";
import { useStudyData } from "../stores/StudyDataContext";
import type { Memory, MemoryType } from "../types/models";

const memoryTypeLabels: Record<MemoryType, string> = {
  goal_memory: "目标",
  completion_memory: "完成记录",
  weakness_memory: "薄弱点",
  mistake_memory: "错因",
  insight_memory: "学习收获",
  review_memory: "复习计划",
};

interface EditDraft {
  content: string;
  importance: number;
  confidence: number;
}

export default function MemoryPage() {
  const { memories, refresh, error } = useStudyData();
  const [typeFilter, setTypeFilter] = useState<MemoryType | "">("");
  const [topicFilter, setTopicFilter] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [draft, setDraft] = useState<EditDraft | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const filtered = useMemo(
    () =>
      memories.filter(
        (memory) =>
          (!typeFilter || memory.memory_type === typeFilter) &&
          (!topicFilter ||
            memory.topic.toLowerCase().includes(topicFilter.toLowerCase())),
      ),
    [memories, typeFilter, topicFilter],
  );

  function beginEdit(memory: Memory) {
    setEditingId(memory.id);
    setDraft({
      content: memory.content,
      importance: memory.importance,
      confidence: memory.confidence,
    });
  }

  async function saveEdit() {
    if (editingId === null || draft === null || !draft.content.trim()) {
      return;
    }
    setIsSaving(true);
    try {
      await memoryApi.update(editingId, {
        content: draft.content.trim(),
        importance: draft.importance,
        confidence: draft.confidence,
      });
      setEditingId(null);
      setDraft(null);
      await refresh();
    } finally {
      setIsSaving(false);
    }
  }

  async function deleteMemory(memoryId: number) {
    await memoryApi.delete(memoryId);
    await refresh();
  }

  return (
    <main className="mx-auto max-w-6xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <p className="text-sm font-medium text-cyan-700">Long-term Memory</p>
      <h1 className="mt-2 text-3xl font-semibold">学习记忆</h1>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
        这里只保存薄弱点、错因、收获和复习计划等长期有价值的信息，不保存完整聊天记录。
      </p>

      {error && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      <div className="mt-8 grid gap-4 rounded-2xl border border-slate-200 bg-white p-4 sm:grid-cols-2">
        <label className="text-sm font-medium text-slate-600">
          Memory 类型
          <select
            value={typeFilter}
            onChange={(event) =>
              setTypeFilter(event.target.value as MemoryType | "")
            }
            className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5"
          >
            <option value="">全部类型</option>
            {Object.entries(memoryTypeLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium text-slate-600">
          Topic
          <input
            value={topicFilter}
            onChange={(event) => setTopicFilter(event.target.value)}
            placeholder="例如 react"
            className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5"
          />
        </label>
      </div>

      <div className="mt-6 flex items-center justify-between">
        <h2 className="font-semibold">Memory 列表</h2>
        <span className="text-sm text-slate-400">{filtered.length} 条</span>
      </div>

      {filtered.length === 0 ? (
        <div className="mt-4 rounded-2xl border border-dashed border-slate-300 bg-white py-14 text-center text-sm text-slate-400">
          暂无符合条件的长期记忆
        </div>
      ) : (
        <ul className="mt-4 grid gap-4 lg:grid-cols-2">
          {filtered.map((memory) => (
            <li
              key={memory.id}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <span className="rounded-full bg-violet-50 px-2.5 py-1 text-xs font-medium text-violet-700">
                    {memoryTypeLabels[memory.memory_type]}
                  </span>
                  <p className="mt-2 text-xs text-slate-400">
                    {memory.topic} · {memory.source}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => beginEdit(memory)}
                    className="text-xs font-medium text-cyan-700"
                  >
                    编辑
                  </button>
                  <button
                    type="button"
                    onClick={() => void deleteMemory(memory.id)}
                    className="text-xs font-medium text-rose-600"
                  >
                    删除
                  </button>
                </div>
              </div>

              {editingId === memory.id && draft ? (
                <div className="mt-4 space-y-3">
                  <textarea
                    value={draft.content}
                    onChange={(event) =>
                      setDraft({ ...draft, content: event.target.value })
                    }
                    rows={4}
                    className="w-full rounded-xl border border-slate-200 p-3 text-sm"
                  />
                  <div className="grid grid-cols-2 gap-3">
                    <label className="text-xs text-slate-500">
                      Importance
                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.1"
                        value={draft.importance}
                        onChange={(event) =>
                          setDraft({
                            ...draft,
                            importance: Number(event.target.value),
                          })
                        }
                        className="mt-1 w-full rounded-lg border border-slate-200 p-2"
                      />
                    </label>
                    <label className="text-xs text-slate-500">
                      Confidence
                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.1"
                        value={draft.confidence}
                        onChange={(event) =>
                          setDraft({
                            ...draft,
                            confidence: Number(event.target.value),
                          })
                        }
                        className="mt-1 w-full rounded-lg border border-slate-200 p-2"
                      />
                    </label>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      disabled={isSaving}
                      onClick={() => void saveEdit()}
                      className="rounded-lg bg-slate-950 px-3 py-2 text-xs font-semibold text-white"
                    >
                      保存
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditingId(null)}
                      className="rounded-lg border border-slate-200 px-3 py-2 text-xs"
                    >
                      取消
                    </button>
                  </div>
                </div>
              ) : (
                <p className="mt-4 text-sm leading-6 text-slate-600">
                  {memory.content}
                </p>
              )}

              <div className="mt-4 grid grid-cols-3 gap-3 border-t border-slate-100 pt-4 text-xs">
                <div>
                  <p className="text-slate-400">重要度</p>
                  <p className="mt-1 font-semibold">{memory.importance}</p>
                </div>
                <div>
                  <p className="text-slate-400">置信度</p>
                  <p className="mt-1 font-semibold">{memory.confidence}</p>
                </div>
                <div>
                  <p className="text-slate-400">下次复习</p>
                  <p className="mt-1 font-semibold">
                    {memory.next_review_at
                      ? new Date(memory.next_review_at).toLocaleDateString()
                      : "未设置"}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}

