import { cn } from "../lib/cn";
import type { Stack, Step } from "../types";
import { Button } from "./Button";
import { Wordmark } from "./Wordmark";

const STEPS: { id: Step; label: string }[] = [
  { id: "home", label: "Home" },
  { id: "questions", label: "Brief" },
  { id: "hazards", label: "Hazards" },
  { id: "report", label: "Assessment" },
  { id: "intel", label: "Details" },
];

export function Header({
  step, setStep, stack, onReset, overHero = false,
}: {
  step: Step;
  setStep: (s: Step) => void;
  stack: Stack | null;
  onReset: () => void;
  overHero?: boolean;
}) {
  return (
    <header className={cn("no-print z-30 w-full", overHero ? "absolute top-0 left-0" : "sticky top-0 bg-ink")}>
      <div className="max-w-6xl mx-auto px-6 py-5 flex flex-wrap items-center gap-4 justify-between">
        <button type="button" onClick={() => setStep("home")} className="text-left">
          <Wordmark light />
        </button>
        <nav className="hidden md:flex items-center gap-5">
          {STEPS.map((s) => (
            <button
              key={s.id}
              onClick={() => setStep(s.id)}
              className={cn(
                "text-[13px] font-display font-bold uppercase tracking-[0.16em] transition-colors",
                step === s.id ? "text-orange" : "text-white/70 hover:text-white",
              )}
            >
              {s.label}
            </button>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          {stack && (
            <span className="hidden sm:block text-[11px] uppercase tracking-widest text-white/45">
              {stack.gemini_configured ? "Gemini ready" : "No key needed"}
            </span>
          )}
          <Button onClick={onReset}>New assessment</Button>
        </div>
      </div>
    </header>
  );
}
