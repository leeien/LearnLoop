export function PlaceholderPanel({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <section className="rounded-2xl border border-dashed border-slate-300 bg-white/60 p-5">
      <h2 className="font-semibold text-slate-700">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-slate-400">{description}</p>
      <span className="mt-4 inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-500">
        后续阶段开放
      </span>
    </section>
  );
}

