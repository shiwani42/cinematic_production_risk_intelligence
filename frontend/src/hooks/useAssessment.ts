import { useMemo, useState } from "react";
import { api } from "../api";
import type { Brief, Callsheet, HazardRow, Question, Stack, Step, What, When, Where, Who } from "../types";

export function useAssessment() {
  const [step, setStep] = useState<Step>("home");
  const [q, setQ] = useState<Question>("who");
  const [hcat, setHcat] = useState("Production Activities");
  const [title, setTitle] = useState("Untitled production");
  const [location, setLocation] = useState("");
  const [date, setDate] = useState("2026-09-20");
  const [who, setWho] = useState<Who>({ crew_size: "", key_roles: "", specialists: "", experience: "" });
  const [what, setWhat] = useState<What>({ production_type: "scripted", activities: "", equipment: "", script_text: "" });
  const [where, setWhere] = useState<Where>({ environment: "" });
  const [when, setWhen] = useState<When>({ notes: "" });
  const [callsheet, setCallsheet] = useState<Callsheet>({ crew: [] });
  const [csText, setCsText] = useState("{}");
  const [brief, setBrief] = useState<Brief | null>(null);
  const [removed, setRemoved] = useState<Set<string>>(new Set());
  const [extras, setExtras] = useState<HazardRow[]>([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [stack, setStack] = useState<Stack | null>(null);
  const [ask, setAsk] = useState(
    "In four sentences, what should the 1st AD watch on this day — and which scene needs a supervisor on set?",
  );
  const [agent, setAgent] = useState<{ text: string; tools: string[]; authors: string[] } | null>(null);

  const rows = useMemo(() => {
    if (!brief) return [];
    return [...brief.risk_register.filter((r) => !removed.has(r.id)), ...extras];
  }, [brief, removed, extras]);
  const cats = useMemo(() => [...new Set(rows.map((r) => r.category))], [rows]);

  async function loadSample() {
    const d = await api.sample();
    setTitle(d.callsheet.production || "Sample Western");
    setLocation(d.callsheet.location || "");
    setDate(d.callsheet.shoot_date || date);
    setCallsheet(d.callsheet);
    setCsText(JSON.stringify(d.callsheet, null, 2));
    setWhat({
      production_type: d.project_context.production_type,
      activities: d.project_context.what.activities,
      equipment: d.project_context.what.equipment,
      script_text: d.script_text,
    });
    setWho({
      crew_size: d.project_context.who.crew_size,
      key_roles: d.project_context.who.key_roles,
      specialists: d.project_context.who.specialists,
      experience: d.project_context.who.experience,
    });
    setWhere({ environment: d.project_context.where.environment });
    setWhen({ notes: d.project_context.when.notes });
    return d;
  }

  async function generate() {
    setErr("");
    setBusy(true);
    try {
      let sheet = callsheet;
      try {
        sheet = JSON.parse(csText);
      } catch {
        throw new Error("Call sheet JSON is not valid.");
      }
      const next = await api.analyze({
        production_title: title,
        script_text: what.script_text,
        callsheet: sheet,
        location_name: location,
        shoot_date: date,
        project_context: { production_type: what.production_type, who, what, where, when },
        extra_hazards: extras,
      });
      setBrief(next);
      setRemoved(new Set());
      setHcat(next.risk_register_sections[0]?.category || "Production Activities");
      setStep("hazards");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Analyze failed");
    } finally {
      setBusy(false);
    }
  }

  async function judgeDemo() {
    setErr("");
    setBusy(true);
    try {
      const d = await loadSample();
      const next = await api.analyze({
        production_title: d.callsheet.production,
        script_text: d.script_text,
        callsheet: d.callsheet,
        location_name: d.callsheet.location,
        shoot_date: d.callsheet.shoot_date,
        project_context: d.project_context,
      });
      setBrief(next);
      setRemoved(new Set());
      setHcat(next.risk_register_sections[0]?.category || "Production Activities");
      setStep("report");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Demo failed");
    } finally {
      setBusy(false);
    }
  }

  async function askAgent() {
    if (!brief) return;
    setBusy(true);
    setErr("");
    try {
      const res = await api.ask(ask, {
        title,
        location,
        date,
        summary: brief.executive_summary,
        top_scenes: brief.scenes?.slice(0, 4),
        hazards: rows.slice(0, 12).map((r) => r.hazard),
      });
      setAgent({ text: res.text, tools: res.tools_called, authors: res.authors });
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Agent failed");
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    setBrief(null);
    setExtras([]);
    setRemoved(new Set());
    setStep("home");
    setQ("who");
  }

  function addHazard() {
    const hazard = window.prompt("What else should we list? One sentence is enough.");
    if (!hazard) return;
    setExtras((xs) => [
      ...xs,
      {
        id: "x" + Date.now(),
        category: hcat,
        subsection: "Added on review",
        hazard,
        likelihood: "To be confirmed on scout",
        consequence: "Supervisor to set severity",
        controls: ["Tech scout and supervisor sign-off before the day"],
      },
    ]);
  }

  return {
    step, setStep, q, setQ, hcat, setHcat,
    title, setTitle, location, setLocation, date, setDate,
    who, setWho, what, setWhat, where, setWhere, when, setWhen,
    csText, setCsText, brief, rows, cats, busy, err, stack, setStack,
    ask, setAsk, agent, loadSample, generate, judgeDemo, askAgent, reset, addHazard,
    setRemoved, removed,
  };
}
