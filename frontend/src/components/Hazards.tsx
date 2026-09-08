import type { HazardRow } from "../types";
import { cn } from "../lib/cn";
import { PageTitle } from "./Field";

export function Hazards({
  rows, category, cats, counts, onCat, onRemove, onAdd,
}: {
  rows: HazardRow[];
  category: string;
  cats: string[];
  counts: Record<string, number>;
  onCat: (c: string) => void;
  onRemove: (id: string) => void;
  onAdd: () => void;
}) {
  const by: Record<string, HazardRow[]> = {};
  rows.forEach((r) => { (by[r.subsection || "General"] ??= []).push(r); });
  return (
    <div className="max-w-3xl">
      <PageTitle eyebrow="02 · Generate hazards" title="Review what we found">
        These are suggestions from your brief. Remove anything that does not apply, or add one we missed.
      </PageTitle>
      <div className="flex flex-wrap gap-2 mb-8">
        {cats.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => onCat(c)}
            className={cn(
              "cut px-3 py-2 text-[13px] font-display font-bold uppercase tracking-[0.08em] border",
              category === c ? "bg-orange border-orange text-white" : "border-line bg-white text-ink hover:border-orange",
            )}
          >
            {c} <span className="opacity-70 font-normal">{counts[c] || 0}</span>
          </button>
        ))}
      </div>
      {Object.entries(by).map(([sub, list]) => (
        <section key={sub} className="mb-6">
          <h3 className="text-[12px] text-muted mb-3">{sub}</h3>
          <div className="cut bg-white divide-y divide-line">
            {list.map((r) => (
              <article key={r.id} className="px-5 py-4" data-reveal>
                <div className="flex justify-between gap-4">
                  <div>
                    <p className="font-medium text-ink normal-case tracking-normal">{r.hazard}</p>
                    <p className="text-sm text-muted mt-1 normal-case tracking-normal font-normal">{r.likelihood}</p>
                    {!!r.scene_refs?.length && <p className="text-xs text-orange mt-1">Scenes {r.scene_refs.join(", ")}</p>}
                  </div>
                  <button type="button" className="text-[12px] font-display font-bold uppercase tracking-widest text-muted hover:text-crit shrink-0" onClick={() => onRemove(r.id)}>
                    Remove
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      ))}
      <button type="button" onClick={onAdd} className="w-full cut border border-dashed border-orange/50 text-orange py-3 text-[13px] font-display font-bold uppercase tracking-widest hover:bg-peach">
        Add a hazard in {category}
      </button>
    </div>
  );
}
