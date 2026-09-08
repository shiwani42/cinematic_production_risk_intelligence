import { Button } from "./Button";

const HOW = [
  { n: "01", t: "Input project context", d: "Add the who, what, where, and when of your shoot. Plain language is enough." },
  { n: "02", t: "Generate hazards", d: "Review what we suggest. Edit, remove, or add anything you know." },
  { n: "03", t: "Analyse risk", d: "Check the statements, tailor the controls, then a supervisor signs." },
];

const FOR = [
  ["Reality", "Remote formats to constructed reality — risks that actually fit the day."],
  ["Drama & scripted", "Stunts, unit moves, nights. A structured draft instead of a blank page."],
  ["Natural history", "Jungles, deserts, mountains — what the lot already brings."],
  ["Promos & specialist", "Short prep, aerials, animals. Fast first draft, then you refine."],
];

export function Home({ busy, onDemo, onStart }: { busy: boolean; onDemo: () => void; onStart: () => void }) {
  return (
    <div>
      <section className="relative min-h-[88vh] flex items-end pb-16 px-6 text-white hero-wash">
        <div className="max-w-4xl mx-auto w-full text-center">
          <p className="font-display font-bold text-orange tracking-[0.22em] text-[13px] uppercase mb-5" data-reveal>
            AI-drafted. Human-validated.
          </p>
          <h1 className="font-display font-bold text-[clamp(2.2rem,6vw,4.4rem)] leading-[1.05] drop-shadow-lg" data-reveal>
            Production risk assessments take too long. There’s a faster way.
          </h1>
          <p className="mt-6 text-[18px] leading-8 text-white/85 max-w-2xl mx-auto normal-case tracking-normal font-medium" data-reveal>
            MATRIX drafts a shoot-specific assessment from your script and call sheet — built for TV and film, not a generic template. You stay in control.
          </p>
          <div className="flex flex-wrap justify-center gap-3 mt-10" data-reveal>
            <Button disabled={busy} onClick={onDemo} className="px-7 py-3.5 text-base">
              {busy ? "Drafting…" : "Try the sample western"}
            </Button>
            <Button variant="outline" onClick={onStart} className="px-7 py-3.5 text-base border-white text-white hover:bg-white/10">
              Start a new assessment
            </Button>
          </div>
          <p className="text-sm text-white/60 mt-4 normal-case tracking-normal" data-reveal>
            No account. The sample fills itself so you can see a first draft in under a minute.
          </p>
        </div>
      </section>

      <section className="bg-cream px-6 py-20">
        <div className="max-w-5xl mx-auto">
          <p className="text-[12px] font-display font-bold text-orange uppercase tracking-[0.2em] mb-3">How it works</p>
          <h2 className="text-[clamp(1.6rem,3vw,2.2rem)] mb-10">A first draft in minutes</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {HOW.map((s) => (
              <div key={s.n} className="cut bg-white p-7" data-reveal>
                <p className="text-orange font-display font-bold tracking-[0.16em] text-sm mb-3">{s.n}</p>
                <h3 className="text-lg mb-2">{s.t}</h3>
                <p className="text-[15px] text-slate leading-7 normal-case tracking-normal font-normal">{s.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-ink text-white px-6 py-20">
        <div className="max-w-5xl mx-auto">
          <p className="text-[12px] font-display font-bold text-orange uppercase tracking-[0.2em] mb-3">Who it’s for</p>
          <h2 className="text-[clamp(1.6rem,3vw,2.2rem)] mb-10">If you’re writing a shoot-specific RA, this is built for you</h2>
          <div className="grid sm:grid-cols-2 gap-5">
            {FOR.map(([t, d]) => (
              <div key={t} className="cut border border-white/15 p-6" data-reveal>
                <h3 className="text-base text-orange mb-2">{t}</h3>
                <p className="text-[15px] text-white/75 leading-7 normal-case tracking-normal font-normal">{d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
