import type { Brief, Stack } from "../types";
import { cn } from "../lib/cn";
import { fieldClass, tone } from "../lib/tone";
import { Button } from "./Button";
import { PageTitle } from "./Field";

export function Intel({
  brief, stack, ask, setAsk, agent, onAsk, busy,
}: {
  brief: Brief;
  stack: Stack | null;
  ask: string;
  setAsk: (v: string) => void;
  agent: { text: string; tools: string[]; authors: string[] } | null;
  onAsk: () => void;
  busy: boolean;
}) {
  const loc = brief.location_intelligence;
  const ems = loc.emergency_services || {};
  const crew = brief.crew_fatigue_summary?.all || [];
  return (
    <div className="max-w-4xl">
      <PageTitle title="A closer look">
        Scenes, tired crew, and the lot — then ask a question in plain English.
      </PageTitle>

      <div className="grid grid-cols-2 md:grid-cols-4 cut bg-white divide-x divide-y md:divide-y-0 divide-line mb-10">
        {[
          ["Overall", brief.executive_summary.overall_label],
          ["Highest scene", `${brief.executive_summary.highest_scene_risk_score}/10`],
          ["Scenes to sign", String(brief.executive_summary.critical_scenes)],
          ["Crew to watch", String(brief.executive_summary.crew_at_risk)],
        ].map(([k, v]) => (
          <div key={k} className="px-6 py-5" data-reveal>
            <p className={cn("text-2xl font-display font-bold tracking-normal", k === "Overall" ? tone(v) : "text-ink")}>{v}</p>
            <p className="text-[11px] font-display font-bold text-muted uppercase tracking-[0.16em] mt-1">{k}</p>
          </div>
        ))}
      </div>

      <h2 className="text-lg mb-3">Shot list</h2>
      <div className="cut bg-white divide-y divide-line mb-10">
        {brief.scenes?.map((sc) => (
          <div key={sc.scene_number} className="px-5 py-4">
            <div className="flex justify-between gap-3">
              <p className="font-medium normal-case tracking-normal">Scene {sc.scene_number}</p>
              <span className={cn("text-sm font-display font-bold", tone(sc.risk_level))}>{sc.adjusted_risk_score}/10 · {sc.risk_level}</span>
            </div>
            <p className="text-sm text-muted normal-case tracking-normal font-normal">{sc.slug_line}</p>
          </div>
        ))}
      </div>

      <h2 className="text-lg mb-3">Crew hours</h2>
      <div className="space-y-2 mb-10">
        {crew.map((c) => (
          <div key={c.crew_role} className="cut bg-white px-5 py-4">
            <div className="flex justify-between text-sm normal-case tracking-normal">
              <span><span className="font-medium">{c.crew_role}</span> · {c.department}</span>
              <span className={tone(c.risk_level)}>{c.fatigue_score}/100</span>
            </div>
            <div className="h-1.5 bg-cream mt-2 overflow-hidden">
              <div className="h-full bg-orange" style={{ width: `${Math.min(100, c.fatigue_score)}%` }} />
            </div>
            <p className="text-xs text-muted mt-1 normal-case tracking-normal font-normal">{(c.top_contributing_factors || []).join(" · ")} · {c.hours_on_set}h</p>
          </div>
        ))}
      </div>

      <h2 className="text-lg mb-3">Location</h2>
      <div className="cut bg-white px-5 py-4 mb-10 text-sm normal-case tracking-normal">
        {loc.location_name} · {loc.location_type} · {loc.elevation_m}m
        <p className="text-muted mt-1 font-normal">Nearest trauma: {ems.nearest_trauma_center} ({ems.estimated_response_time_minutes} min) · cell {ems.cell_coverage}</p>
      </div>

      <h2 className="text-lg mb-2">Ask a question</h2>
      <p className="text-sm text-muted mb-3 normal-case tracking-normal font-normal">
        {stack?.gemini_configured ? "The specialists will answer from this draft." : "Add a Gemini key to enable this — the draft above still works without it."}
      </p>
      <textarea className={cn(fieldClass, "min-h-24")} value={ask} onChange={(e) => setAsk(e.target.value)} placeholder="e.g. Which scene should a supervisor watch in person?" />
      <div className="mt-3">
        <Button disabled={busy} onClick={onAsk}>{busy ? "Thinking…" : "Ask"}</Button>
      </div>
      {agent && (
        <div className="mt-4 cut bg-white p-5">
          <p className="text-xs text-muted mb-2 uppercase tracking-widest">{agent.authors.join(" → ") || "MATRIX"}</p>
          <p className="whitespace-pre-wrap text-sm leading-relaxed normal-case tracking-normal">{agent.text}</p>
        </div>
      )}
    </div>
  );
}
