import type { Brief, HazardRow } from "../types";
import { cn } from "../lib/cn";
import { tone } from "../lib/tone";
import { PageTitle } from "./Field";

export function Report({ brief, rows }: { brief: Brief; rows: HazardRow[] }) {
  const sections: Record<string, HazardRow[]> = {};
  rows.forEach((r) => { (sections[r.category] ??= []).push(r); });
  return (
    <div className="max-w-4xl">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <PageTitle eyebrow="03 · Analyse risk" title="Your first draft">
          {brief.meta.production_title} · {brief.meta.location} · {brief.meta.shoot_date}
        </PageTitle>
        <span className={cn("mt-1 text-[12px] font-display font-bold uppercase tracking-widest px-3 py-1.5 cut bg-peach", tone(brief.executive_summary.overall_label))}>
          {brief.executive_summary.overall_label}
        </span>
      </div>
      <p className="mb-8 max-w-2xl text-[17px] leading-8 text-slate" data-reveal>{brief.executive_summary.one_liner}</p>

      {brief.thesis && (
        <div className="grid md:grid-cols-3 gap-4 mb-10">
          <Card title="The location already" items={brief.thesis.location_brings} />
          <Card title="The unit brings" items={brief.thesis.production_brings} />
          <div className="cut bg-peach p-5" data-reveal>
            <p className="text-[12px] font-display font-bold text-orange uppercase tracking-[0.16em] mb-2">Review this first</p>
            <p className="text-sm font-medium normal-case tracking-normal">{brief.thesis.do_not_roll}</p>
            <p className="text-xs text-slate mt-2 normal-case tracking-normal font-normal">{brief.thesis.if_we_miss_this}</p>
          </div>
        </div>
      )}

      {!!brief.location_intelligence?.citations?.length && (
        <div className="cut bg-white p-5 mb-10" data-reveal>
          <p className="text-[12px] font-display font-bold text-muted uppercase tracking-[0.16em] mb-3">Live lot sources</p>
          <p className="text-xs text-slate mb-3 normal-case tracking-normal font-normal">
            Review these. They do not replace a scout or dispatch.
          </p>
          <ul className="space-y-2 text-sm normal-case tracking-normal">
            {brief.location_intelligence.citations.map((c) => (
              <li key={c.url || c.title}>
                <a className="text-orange underline" href={c.url} target="_blank" rel="noreferrer">{c.title}</a>
                {c.excerpt ? <span className="block text-muted text-xs mt-0.5 font-normal">{c.excerpt}</span> : null}
              </li>
            ))}
          </ul>
        </div>
      )}

      {!!brief.agent_trace?.length && (
        <div className="cut bg-white p-5 mb-10" data-reveal>
          <p className="text-[12px] font-display font-bold text-muted uppercase tracking-[0.16em] mb-3">How this draft was built</p>
          <ol className="space-y-2 text-sm">
            {brief.agent_trace.map((t, i) => (
              <li key={t.agent} className="flex gap-3">
                <span className="font-display font-bold text-orange w-6">{String(i + 1).padStart(2, "0")}</span>
                <span className="normal-case tracking-normal"><span className="font-medium">{t.agent}</span> · {t.tool}<span className="block text-muted">{t.detail}</span></span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {Object.entries(sections).map(([cat, list]) => (
        <section key={cat} className="mb-8">
          <p className="text-[12px] font-display font-bold text-orange uppercase tracking-[0.16em] mb-2">{cat}</p>
          <div className="overflow-x-auto cut bg-white">
            <table className="w-full text-[13px]">
              <thead>
                <tr className="text-left bg-cream">
                  <th className="p-3 font-display font-bold uppercase tracking-wider w-1/3">Hazard</th>
                  <th className="p-3 font-display font-bold uppercase tracking-wider w-1/3">Risk</th>
                  <th className="p-3 font-display font-bold uppercase tracking-wider w-1/3">What to do</th>
                </tr>
              </thead>
              <tbody>
                {list.map((r) => (
                  <tr key={r.id} className="border-t border-line align-top">
                    <td className="p-3"><span className="block text-muted text-xs mb-0.5 uppercase tracking-wider">{r.subsection}</span><span className="normal-case tracking-normal">{r.hazard}</span></td>
                    <td className="p-3 text-muted normal-case tracking-normal">
                      <span className="text-ink">Likelihood.</span> {r.likelihood}<br />
                      <span className="text-ink">If it happens.</span> {r.consequence}
                      {r.interaction_notes?.map((n) => <div key={n} className="mt-1">{n}</div>)}
                    </td>
                    <td className="p-3 normal-case tracking-normal"><ul className="list-disc pl-4 space-y-1">{r.controls?.map((c) => <li key={c}>{c}</li>)}</ul></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}
      <p className="text-xs text-muted normal-case tracking-normal">{brief.disclaimer}</p>
    </div>
  );
}

function Card({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="cut bg-white p-5" data-reveal>
      <p className="text-[12px] font-display font-bold text-orange uppercase tracking-[0.16em] mb-2">{title}</p>
      <ul className="text-sm space-y-1.5 normal-case tracking-normal">{items.map((x) => <li key={x}>{x}</li>)}</ul>
    </div>
  );
}
