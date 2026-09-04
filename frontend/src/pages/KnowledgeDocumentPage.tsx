import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ragApi } from "../api/ragApi";
import type { KnowledgeDocumentDetail } from "../types/models";

export default function KnowledgeDocumentPage() {
  const { documentId = "" } = useParams();
  const id = Number(documentId);
  const [document, setDocument] =
    useState<KnowledgeDocumentDetail | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    const result = await ragApi.getDocument(id);
    setDocument(result);
    setTitle(result.title);
    setContent(result.content);
    setTags(result.tags.join(", "));
  }

  useEffect(() => {
    if (!Number.isInteger(id) || id <= 0) {
      setError("文档 ID 无效");
      return;
    }
    void load().catch((requestError: unknown) =>
      setError(
        requestError instanceof Error
          ? requestError.message
          : "文档加载失败",
      ),
    );
  }, [id]);

  async function save() {
    setIsBusy(true);
    setError(null);
    setMessage(null);
    try {
      await ragApi.updateDocument(id, {
        title: title.trim(),
        content,
        tags: tags
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
      });
      await load();
      setMessage("文档已保存；内容修改后需要重新向量化。");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "保存失败",
      );
    } finally {
      setIsBusy(false);
    }
  }

  async function indexDocument() {
    setIsBusy(true);
    setError(null);
    setMessage(null);
    try {
      const result = await ragApi.indexDocument(id);
      await load();
      setMessage(
        `已生成 ${result.chunk_count} 个 Chunk，Embedding：${result.embedding_provider}`,
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "向量化失败",
      );
    } finally {
      setIsBusy(false);
    }
  }

  if (!document) {
    return (
      <main className="mx-auto max-w-5xl px-4 py-16 text-center text-sm text-slate-500">
        {error ?? "正在加载文档…"}
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-6xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <Link to="/knowledge-base" className="text-sm text-cyan-700">
        ← 返回知识库
      </Link>
      <div className="mt-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <h1 className="text-3xl font-semibold">编辑知识文档</h1>
          <p className="mt-2 text-sm text-slate-500">
            {document.is_indexed
              ? `已索引 ${document.chunk_count} 个 Chunk`
              : "当前内容尚未索引"}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            type="button"
            disabled={isBusy}
            onClick={() => void save()}
            className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-semibold disabled:opacity-50"
          >
            保存
          </button>
          <button
            type="button"
            disabled={isBusy}
            onClick={() => void indexDocument()}
            className="rounded-xl bg-cyan-700 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50"
          >
            向量化
          </button>
        </div>
      </div>

      {message && (
        <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          {message}
        </div>
      )}
      {error && (
        <div className="mt-5 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </div>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="rounded-2xl border border-slate-200 bg-white p-6">
          <label className="block text-sm font-medium" htmlFor="document-title">
            标题
          </label>
          <input
            id="document-title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3"
          />
          <label className="mt-4 block text-sm font-medium" htmlFor="document-tags">
            标签
          </label>
          <input
            id="document-tags"
            value={tags}
            onChange={(event) => setTags(event.target.value)}
            className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3"
          />
          <label className="mt-4 block text-sm font-medium" htmlFor="document-content">
            Markdown
          </label>
          <textarea
            id="document-content"
            rows={24}
            value={content}
            onChange={(event) => setContent(event.target.value)}
            className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 font-mono text-sm leading-6"
          />
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold">Chunk 预览</h2>
          {document.chunks.length === 0 ? (
            <p className="mt-4 text-sm text-slate-500">
              向量化后显示 Markdown 标题、Chunk 内容和索引序号。
            </p>
          ) : (
            <div className="mt-4 max-h-[48rem] space-y-3 overflow-auto">
              {document.chunks.map((chunk) => (
                <article key={chunk.id} className="rounded-xl bg-slate-50 p-4">
                  <p className="text-xs font-medium text-cyan-700">
                    #{chunk.chunk_index} ·{" "}
                    {String(chunk.metadata.heading ?? "Document")}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    {chunk.content}
                  </p>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
