/**
 * The top of a secondary page (contents, dashboard, interview, roadmap,
 * resources): the title and one line under it. There is no label above the
 * title: the header already shows which page the reader is on.
 */
export function PageHeader({ title, intro }: { title: string; intro: string }) {
  return (
    <header className="mb-10">
      <h1 className="font-display text-[clamp(2rem,4.5vw,2.75rem)] font-bold leading-[1.1] tracking-[-0.02em] text-balance text-text">
        {title}
      </h1>
      <p className="mt-3 max-w-2xl text-[17px] leading-relaxed text-pretty text-text-dim">{intro}</p>
    </header>
  );
}
