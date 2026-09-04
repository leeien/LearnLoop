import { Link } from "react-router-dom";

import type { KnowledgeDocument } from "../../types/models";

export function DocumentCard({
  document,
}: {
  document: KnowledgeDocument;
}) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <Link
            to={`/knowledge-base/${document.id}`}
            className="text-lg font-semibold hover:text-cyan-700"
          >
            {document.title}
          </Link>
          <p className="mt-2 text-xs text-slate-500">
            {document.source_type} · {document.chunk_count} chunks
          </p>
        </div>
        <span
          className={`rounded-full px-2.5 py-1 text-xs font-medium ${
            document.is_indexed
              ? "bg-emerald-50 text-emerald-700"
              : "bg-amber-50 text-amber-700"
          }`}
        >
          {document.is_indexed ? "已索引" : "待索引"}
        </span>
      </div>
      <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-600">
        {document.content}
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        {document.tags.map((tag) => (
          <span
            key={tag}
            className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600"
          >
            {tag}
          </span>
        ))}
      </div>
    </article>
  );
}
