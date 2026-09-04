import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ragApi } from "../api/ragApi";
import { DocumentCard } from "../components/rag/DocumentCard";
import type { KnowledgeDocument } from "../types/models";

function parseTags(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export default function KnowledgeBasePage() {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("# 新笔记\n\n");
  const [tags, setTags] = useState("");
  const [tagFilter, setTagFilter] = useState("");
  const [upload, setUpload] = useState<File | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setDocuments(await ragApi.listDocuments());
  }

  useEffect(() => {
    void refresh().catch((requestError: unknown) =>
      setError(
        requestError instanceof Error
          ? requestError.message
          : "知识库加载失败",
      ),
    );
  }, []);

  const visibleDocuments = useMemo(
    () =>
      tagFilter
        ? documents.filter((document) =>
            document.tags.includes(tagFilter),
          )
        : documents,
    [documents, tagFilter],
  );
  const allTags = Array.from(
    new Set(documents.flatMap((document) => document.tags)),
  );

  async function createDocument(event: FormEvent) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      await ragApi.createDocument({
        title: title.trim(),
        source_type: "markdown",
        content,
        tags: parseTags(tags),
      });
      setTitle("");
      setContent("# 新笔记\n\n");
      setTags("");
      await refresh();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "文档创建失败",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function uploadMarkdown() {
    if (!upload) return;
    setIsSaving(true);
    setError(null);
    try {
      const markdown = await upload.text();
      await ragApi.createDocument({
        title: upload.name.replace(/\.md$/i, ""),
        source_type: "upload",
        content: markdown,
        tags: ["upload"],
      });
      setUpload(null);
      await refresh();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Markdown 上传失败",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="mx-auto max-w-7xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <div>
        <p className="text-sm font-medium text-cyan-700">Personal RAG</p>
        <h1 className="mt-2 text-3xl font-semibold">个人 Agent 知识库</h1>
        <p className="mt-3 text-sm text-slate-500">
          RAG 保存学习资料；Memory 保存你的学习状态，两者互不替代。
        </p>
      </div>

      {error && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </div>
      )}

      <div className="mt-8 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="space-y-6">
          <form
            onSubmit={(event) => void createDocument(event)}
            className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <h2 className="font-semibold">新建 Markdown 笔记</h2>
            <label className="mt-4 block text-sm font-medium" htmlFor="rag-title">
              标题
            </label>
            <input
              id="rag-title"
              required
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm"
            />
            <label className="mt-4 block text-sm font-medium" htmlFor="rag-content">
              Markdown
            </label>
            <textarea
              id="rag-content"
              required
              rows={10}
              value={content}
              onChange={(event) => setContent(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 font-mono text-sm leading-6"
            />
            <label className="mt-4 block text-sm font-medium" htmlFor="rag-tags">
              标签（逗号分隔）
            </label>
            <input
              id="rag-tags"
              value={tags}
              onChange={(event) => setTags(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm"
            />
            <button
              type="submit"
              disabled={isSaving}
              className="mt-5 w-full rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50"
            >
              {isSaving ? "保存中…" : "创建笔记"}
            </button>
          </form>

          <section className="rounded-2xl border border-slate-200 bg-white p-6">
            <h2 className="font-semibold">上传 Markdown</h2>
            <input
              type="file"
              accept=".md,text/markdown,text/plain"
              onChange={(event) =>
                setUpload(event.target.files?.[0] ?? null)
              }
              className="mt-4 block w-full text-sm"
            />
            <button
              type="button"
              disabled={!upload || isSaving}
              onClick={() => void uploadMarkdown()}
              className="mt-4 w-full rounded-xl bg-cyan-700 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50"
            >
              上传并创建
            </button>
          </section>
        </div>

        <section>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <h2 className="text-xl font-semibold">
              文档列表（{visibleDocuments.length}）
            </h2>
            <select
              value={tagFilter}
              onChange={(event) => setTagFilter(event.target.value)}
              className="rounded-xl border border-slate-200 px-3 py-2 text-sm"
            >
              <option value="">全部标签</option>
              {allTags.map((tag) => (
                <option key={tag} value={tag}>
                  {tag}
                </option>
              ))}
            </select>
          </div>
          {visibleDocuments.length === 0 ? (
            <div className="mt-5 rounded-2xl border border-dashed border-slate-300 bg-white py-14 text-center text-sm text-slate-500">
              暂无知识库文档
            </div>
          ) : (
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              {visibleDocuments.map((document) => (
                <DocumentCard key={document.id} document={document} />
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
