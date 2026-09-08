import { useEffect, useMemo, useRef } from "react";
import { api, downloadJson } from "./api";
import { BusyOverlay } from "./components/BusyOverlay";
import { Button } from "./components/Button";
import { Hazards } from "./components/Hazards";
import { Header } from "./components/Header";
import { Home } from "./components/Home";
import { Intel } from "./components/Intel";
import { Questions } from "./components/Questions";
import { Report } from "./components/Report";
import { useAssessment } from "./hooks/useAssessment";
import { reveal } from "./lib/reveal";
import type { Question } from "./types";

const Q_ORDER: Question[] = ["who", "what", "where", "when"];

export function App() {
  const a = useAssessment();
  const stage = useRef<HTMLDivElement>(null);
  const counts = useMemo(() => {
    const m: Record<string, number> = {};
    a.rows.forEach((r) => { m[r.category] = (m[r.category] || 0) + 1; });
    return m;
  }, [a.rows]);

  useEffect(() => {
    api.stack().then(a.setStack).catch(() => a.setStack(null));
  }, []);

  useEffect(() => {
    reveal(stage.current);
  }, [a.step, a.q, a.hcat, a.brief]);

  return (
    <div className={a.step === "home" ? "min-h-screen bg-ink" : "min-h-screen bg-cream"}>
      <Header
        step={a.step}
        setStep={a.setStep}
        stack={a.stack}
        onReset={a.reset}
        overHero={a.step === "home"}
      />
      <div ref={stage}>
        {a.step === "home" && (
          <Home
            busy={a.busy}
            onDemo={a.judgeDemo}
            onStart={() => a.setStep("questions")}
          />
        )}
        {a.step !== "home" && (
          <main className="max-w-6xl mx-auto px-6 py-12 pb-28">
            {a.step === "questions" && (
              <Questions
                q={a.q}
                setQ={a.setQ}
                title={a.title} setTitle={a.setTitle}
                location={a.location} setLocation={a.setLocation}
                date={a.date} setDate={a.setDate}
                who={a.who} setWho={a.setWho}
                what={a.what} setWhat={a.setWhat}
                where={a.where} setWhere={a.setWhere}
                when={a.when} setWhen={a.setWhen}
                csText={a.csText} setCsText={a.setCsText}
                onSample={() => a.loadSample().catch(() => undefined)}
              />
            )}
            {a.step === "hazards" && a.brief && (
              <Hazards
                rows={a.rows.filter((r) => r.category === a.hcat)}
                category={a.hcat}
                cats={a.cats}
                counts={counts}
                onCat={a.setHcat}
                onRemove={(id) => a.setRemoved(new Set(a.removed).add(id))}
                onAdd={a.addHazard}
              />
            )}
            {a.step === "report" && a.brief && <Report brief={a.brief} rows={a.rows} />}
            {a.step === "intel" && a.brief && (
              <Intel
                brief={a.brief}
                stack={a.stack}
                ask={a.ask}
                setAsk={a.setAsk}
                agent={a.agent}
                onAsk={a.askAgent}
                busy={a.busy}
              />
            )}
            {a.step !== "questions" && !a.brief && (
              <div className="max-w-md">
                <h1 className="text-2xl">Nothing here yet</h1>
                <p className="text-muted mt-2 text-[16px] normal-case tracking-normal font-normal">Start a brief, or try the sample western from Home.</p>
                <Button className="mt-6" onClick={() => a.setStep("home")}>Back to home</Button>
              </div>
            )}

            {a.err && <p className="mt-4 text-sm text-crit bg-peach cut px-4 py-3 max-w-xl">{a.err}</p>}

            <footer className="no-print sticky bottom-0 mt-12 -mx-6 px-6 py-4 bg-cream/95 backdrop-blur border-t border-line flex flex-wrap gap-3 justify-between items-center">
              <span className="text-xs text-muted normal-case tracking-normal">A first draft only. Someone on the production still reviews and signs.</span>
              <div className="flex flex-wrap gap-2">
                {a.step === "questions" && (
                  <>
                    {a.q !== "who" && (
                      <Button variant="ghost" onClick={() => a.setQ(Q_ORDER[Math.max(0, Q_ORDER.indexOf(a.q) - 1)])}>Back</Button>
                    )}
                    {a.q !== "when" ? (
                      <Button onClick={() => a.setQ(Q_ORDER[Q_ORDER.indexOf(a.q) + 1])}>Continue</Button>
                    ) : (
                      <Button disabled={a.busy} onClick={a.generate}>{a.busy ? "Drafting…" : "Generate hazards"}</Button>
                    )}
                  </>
                )}
                {a.step === "hazards" && a.brief && (
                  <>
                    <Button variant="ghost" onClick={() => a.setStep("questions")}>Back</Button>
                    <Button onClick={() => a.setStep("report")}>Analyse risk</Button>
                  </>
                )}
                {a.step === "report" && a.brief && (
                  <>
                    <Button variant="ghost" onClick={() => a.setStep("hazards")}>Back</Button>
                    <Button variant="ghost" onClick={() => window.print()}>Print</Button>
                    <Button variant="outline" onClick={() => downloadJson(a.brief!, a.rows)}>Download JSON</Button>
                    <Button onClick={() => a.setStep("intel")}>See details</Button>
                  </>
                )}
                {a.step === "intel" && (
                  <Button variant="ghost" onClick={() => a.setStep("report")}>Back to assessment</Button>
                )}
              </div>
            </footer>
          </main>
        )}
      </div>

      {a.busy && a.step !== "intel" && (
        <BusyOverlay label="Looking at the script, the crew hours, and the location — then putting them on one page." />
      )}
    </div>
  );
}
