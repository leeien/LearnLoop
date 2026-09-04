import type { RAGSource } from "../../types/models";

export function SourceCard({ source }: { source: RAGSource }) {
  return (
    <article className="rounded-xl border border-cyan-100 bg-cyan-50 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-semibold text-cyan-950">
          {source.citation} {source.document_title}
        </p>
        <span className="text-xs text-cyan-700">
          {(source.similarity_score * 100).toFixed(1)}%
        </span>
      </div>
      <p className="mt-1 text-xs text-cyan-700">{source.heading}</p>
      <p className="mt-3 line-clamp-4 text-sm leading-6 text-cyan-950/75">
        {source.content}
      </p>
    </article>
  );
}
