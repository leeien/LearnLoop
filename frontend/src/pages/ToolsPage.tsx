import { useEffect, useState, type FormEvent } from "react";

import { toolsApi, type ToolDefinition } from "../api/toolsApi";
import type { Memory, MemoryType } from "../types/models";

const memoryTypes: Array<{ value: MemoryType; label: string }> = [
  { value: "goal_memory", label: "目标" },
  { value: "completion_memory", label: "完成记录" },
  { value: "weakness_memory", label: "知识薄弱点" },
  { value: "mistake_memory", label: "错因" },
  { value: "insight_memory", label: "学习收获" },
  { value: "review_memory", label: "复习记录" },
];

export default function ToolsPage() {
  const [definitions, setDefinitions] = useState<ToolDefinition[]>([]);
  const [results, setResults] = useState<Memory[]>([]);
  const [query, setQuery] = useState("");
  const [searchTopic, setSearchTopic] = useState("");
  const [writeType, setWriteType] =
    useState<MemoryType>("weakness_memory");
  const [writeTopic, setWriteTopic] = useState("");
  const [writeContent, setWriteContent] = useState("");
  const [writeSource, setWriteSource] = useState("manual-tools-page");
  const [lastCreated, setLastCreated] = useState<Memory | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isWriting, setIsWriting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    toolsApi
      .list()
      .then(setDefinitions)
      .catch((requestError: unknown) =>
        setError(
          requestError instanceof Error
            ? requestError.message
            : "工具列表加载失败",
        ),
      );
  }, []);

  async function searchMemory(event: FormEvent) {
    event.preventDefault();
    setIsSearching(true);
    setError(null);
    try {
      const memories = await toolsApi.call<Memory[]>("memory.search", {
        query: query.trim(),
        ...(searchTopic.trim() ? { topic: searchTopic.trim() } : {}),
        limit: 10,
      });
      setResults(memories);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Memory 检索失败",
      );
    } finally {
      setIsSearching(false);
    }
  }

  async function writeMemory(event: FormEvent) {
    event.preventDefault();
    setIsWriting(true);
    setError(null);
    try {
      const memory = await toolsApi.call<Memory>("memory.write", {
        memory_type: writeType,
        topic: writeTopic.trim(),
        content: writeContent.trim(),
        source: writeSource.trim(),
        importance: 0.7,
        confidence: 0.8,
        tags: ["mcp-tool"],
      });
      setLastCreated(memory);
      setWriteContent("");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Memory 写入失败",
      );
    } finally {
      setIsWriting(false);
    }
  }

  return (
    <main className="mx-auto max-w-7xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <div>
        <p className="text-sm font-medium text-cyan-700">Memory MCP</p>
        <h1 className="mt-2 text-3xl font-semibold">Memory Tools</h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-500">
          通过固定 Tool Registry 调用长期记忆能力。工具仅访问
          MemoryService，不执行 Shell、文件读取或 Prompt MCP。
        </p>
      </div>

      {error && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <form
          onSubmit={(event) => void searchMemory(event)}
          className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <h2 className="text-lg font-semibold">memory.search</h2>
          <label className="mt-5 block text-sm font-medium" htmlFor="tool-query">
            检索内容
          </label>
          <input
            id="tool-query"
            required
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例如：ReAct Observation"
            className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-cyan-500"
          />
          <label className="mt-4 block text-sm font-medium" htmlFor="search-topic">
            Topic（可选）
          </label>
          <input
            id="search-topic"
            value={searchTopic}
            onChange={(event) => setSearchTopic(event.target.value)}
            placeholder="例如：ReAct"
            className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-cyan-500"
          />
          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            className="mt-5 w-full rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50"
          >
            {isSearching ? "检索中…" : "调用 memory.search"}
          </button>

          <div className="mt-5 space-y-3">
            {results.length === 0 ? (
              <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">
                暂无检索结果
              </p>
            ) : (
              results.map((memory) => (
                <article key={memory.id} className="rounded-xl bg-slate-50 p-4">
                  <p className="text-xs text-slate-500">
                    {memory.topic} · {memory.memory_type}
                  </p>
                  <p className="mt-2 text-sm leading-6">{memory.content}</p>
                </article>
              ))
            )}
          </div>
        </form>

        <form
          onSubmit={(event) => void writeMemory(event)}
          className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <h2 className="text-lg font-semibold">memory.write</h2>
          <label className="mt-5 block text-sm font-medium" htmlFor="write-type">
            Memory 类型
          </label>
          <select
            id="write-type"
            value={writeType}
            onChange={(event) => setWriteType(event.target.value as MemoryType)}
            className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm"
          >
            {memoryTypes.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
          <label className="mt-4 block text-sm font-medium" htmlFor="write-topic">
            Topic
          </label>
          <input
            id="write-topic"
            required
            value={writeTopic}
            onChange={(event) => setWriteTopic(event.target.value)}
            placeholder="例如：ReAct"
            className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-cyan-500"
          />
          <label className="mt-4 block text-sm font-medium" htmlFor="write-content">
            长期学习信息
          </label>
          <textarea
            id="write-content"
            required
            rows={5}
            value={writeContent}
            onChange={(event) => setWriteContent(event.target.value)}
            placeholder="记录有长期价值的薄弱点、错因或收获"
            className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm leading-6 outline-none focus:border-cyan-500"
          />
          <label className="mt-4 block text-sm font-medium" htmlFor="write-source">
            Source
          </label>
          <input
            id="write-source"
            required
            value={writeSource}
            onChange={(event) => setWriteSource(event.target.value)}
            className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-cyan-500"
          />
          <button
            type="submit"
            disabled={
              isWriting ||
              !writeTopic.trim() ||
              !writeContent.trim() ||
              !writeSource.trim()
            }
            className="mt-5 w-full rounded-xl bg-cyan-700 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50"
          >
            {isWriting ? "写入中…" : "调用 memory.write"}
          </button>

          {lastCreated && (
            <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
              已创建 Memory #{lastCreated.id}：{lastCreated.topic}
            </div>
          )}
        </form>
      </div>

      <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6">
        <h2 className="font-semibold">已注册工具</h2>
        {definitions.length === 0 ? (
          <p className="mt-3 text-sm text-slate-500">尚未加载工具定义</p>
        ) : (
          <ul className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {definitions.map((tool) => (
              <li key={tool.name} className="rounded-xl bg-slate-50 p-4">
                <p className="font-mono text-sm font-semibold">{tool.name}</p>
                <p className="mt-2 text-xs leading-5 text-slate-500">
                  {tool.description}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
