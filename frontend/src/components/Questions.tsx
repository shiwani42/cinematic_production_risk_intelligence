import { useState } from "react";
import type { Question, What, When, Where, Who } from "../types";
import { fieldClass } from "../lib/tone";
import { cn } from "../lib/cn";
import { Field, PageTitle } from "./Field";
import { Stepper } from "./Stepper";

const STEPS: { id: Question; label: string }[] = [
  { id: "who", label: "Who" },
  { id: "what", label: "What" },
  { id: "where", label: "Where" },
  { id: "when", label: "When" },
];

const COPY: Record<Question, { title: string; body: string }> = {
  who: {
    title: "Who is on set?",
    body: "A few names and numbers. If you are not sure, write your best guess — you can change it later.",
  },
  what: {
    title: "What are you filming?",
    body: "The action and kit that change the risk picture. Paste a script if you have one; a scene list is fine too.",
  },
  where: {
    title: "Where is the shoot?",
    body: "What the location already brings — before anyone arrives with cameras.",
  },
  when: {
    title: "When is it happening?",
    body: "Nights, long days, and company moves are what wear people out. A call sheet is optional.",
  },
};

const TYPES = [
  { id: "scripted", label: "Drama / scripted" },
  { id: "reality", label: "Reality" },
  { id: "natural_history", label: "Natural history" },
  { id: "promo", label: "Promo" },
  { id: "specialist", label: "Specialist" },
];

export function Questions(props: {
  q: Question;
  setQ: (q: Question) => void;
  title: string; setTitle: (v: string) => void;
  location: string; setLocation: (v: string) => void;
  date: string; setDate: (v: string) => void;
  who: Who; setWho: (v: Who) => void;
  what: What; setWhat: (v: What) => void;
  where: Where; setWhere: (v: Where) => void;
  when: When; setWhen: (v: When) => void;
  csText: string; setCsText: (v: string) => void;
  onSample: () => void;
}) {
  const copy = COPY[props.q];
  const [showJson, setShowJson] = useState(false);

  return (
    <div className="max-w-2xl">
      <PageTitle eyebrow="01 · Input project context" title={copy.title}>
        {copy.body}
      </PageTitle>
      <Stepper items={STEPS} current={props.q} onPick={(id) => props.setQ(id as Question)} />

      {props.q === "who" && (
        <>
          <Field label="How many people are on the unit?" hint="Cast, crew, day-players, specialists.">
            <input className={fieldClass} placeholder="e.g. 42 including 6 stunt" value={props.who.crew_size} onChange={(e) => props.setWho({ ...props.who, crew_size: e.target.value })} />
          </Field>
          <Field label="Who is responsible for safety?" hint="1st AD, safety supervisor, medic — whoever holds the page.">
            <textarea className={cn(fieldClass, "min-h-24")} placeholder="e.g. Safety supervisor on set; 1st AD holds the call." value={props.who.key_roles} onChange={(e) => props.setWho({ ...props.who, key_roles: e.target.value })} />
          </Field>
          <Field label="Any specialists?" hint="Stunt, SFX, wrangler, medic, aviation, armourer. Leave blank if none.">
            <textarea className={cn(fieldClass, "min-h-24")} placeholder="e.g. SFX pyro, horse wrangler, helicopter coordinator" value={props.who.specialists} onChange={(e) => props.setWho({ ...props.who, specialists: e.target.value })} />
          </Field>
          <Field label="Have they done this kind of day before?">
            <textarea className={cn(fieldClass, "min-h-24")} placeholder="e.g. Key grip on day 6 of 6; wrangler new to this lot." value={props.who.experience} onChange={(e) => props.setWho({ ...props.who, experience: e.target.value })} />
          </Field>
        </>
      )}

      {props.q === "what" && (
        <>
          <Field label="What kind of production is this?">
            <div className="flex flex-wrap gap-2">
              {TYPES.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => props.setWhat({ ...props.what, production_type: t.id })}
                  className={cn(
                    "cut px-3 py-2 text-[13px] font-display font-bold uppercase tracking-[0.08em] border",
                    props.what.production_type === t.id ? "bg-orange border-orange text-white" : "border-line bg-white text-ink hover:border-orange",
                  )}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </Field>
          <Field label="What are you filming on the day?">
            <textarea className={cn(fieldClass, "min-h-24")} placeholder="e.g. Night canyon ride, squib gunfight, helicopter insert" value={props.what.activities} onChange={(e) => props.setWhat({ ...props.what, activities: e.target.value })} />
          </Field>
          <Field label="Kit that changes the risk" hint="Helicopters, pyro, animals, weapons, water, heights.">
            <textarea className={cn(fieldClass, "min-h-20")} placeholder="e.g. Helicopter, blank-fire weapons, horses, SFX fire" value={props.what.equipment} onChange={(e) => props.setWhat({ ...props.what, equipment: e.target.value })} />
          </Field>
          <Field label="Script or scene list" hint="Paste scenes if you have them. Headings like SCENE 12 help us attach risk to each shot.">
            <textarea className={cn(fieldClass, "min-h-40")} placeholder={"SCENE 12 — EXT. CANYON RIDGE — NIGHT\nA rider takes the ridge. Pyro on the slope…"} value={props.what.script_text} onChange={(e) => props.setWhat({ ...props.what, script_text: e.target.value })} />
          </Field>
        </>
      )}

      {props.q === "where" && (
        <>
          <div className="grid sm:grid-cols-2 gap-4">
            <Field label="Location">
              <input className={fieldClass} placeholder="e.g. Vasquez Rocks, CA" value={props.location} onChange={(e) => props.setLocation(e.target.value)} />
            </Field>
            <Field label="Shoot date">
              <input type="date" className={fieldClass} value={props.date} onChange={(e) => props.setDate(e.target.value)} />
            </Field>
          </div>
          <Field label="What is already there?" hint="Terrain, wildlife, weather, phone signal, how long for an ambulance.">
            <textarea className={cn(fieldClass, "min-h-28")} placeholder="e.g. Sandstone cliffs, rattlesnakes, weak cell, 20+ min to trauma" value={props.where.environment} onChange={(e) => props.setWhere({ environment: e.target.value })} />
          </Field>
        </>
      )}

      {props.q === "when" && (
        <>
          <Field label="Production title">
            <input className={fieldClass} placeholder="e.g. Dust & Echoes — Unit A" value={props.title} onChange={(e) => props.setTitle(e.target.value)} />
          </Field>
          <Field label="Schedule notes" hint="Nights, back-to-back days, company moves.">
            <textarea className={cn(fieldClass, "min-h-24")} placeholder="e.g. Night shoot, sixth consecutive day, wrap after 16 hours" value={props.when.notes} onChange={(e) => props.setWhen({ notes: e.target.value })} />
          </Field>
          <button type="button" className="text-sm font-display font-bold uppercase tracking-widest text-orange mb-3" onClick={() => setShowJson((v) => !v)}>
            {showJson ? "Hide call sheet" : "I have a call sheet (optional)"}
          </button>
          {showJson && (
            <Field label="Call sheet" hint="Paste JSON if you have one. Roles, call, wrap, and commute help us flag tired crew. Skip this if you do not.">
              <textarea className={cn(fieldClass, "min-h-36 font-mono text-[13px]")} value={props.csText} onChange={(e) => props.setCsText(e.target.value)} />
            </Field>
          )}
        </>
      )}

      <p className="text-sm text-muted normal-case tracking-normal">
        Stuck? <button type="button" className="text-orange font-bold uppercase tracking-wider" onClick={props.onSample}>Load the sample western</button> and follow along.
      </p>
    </div>
  );
}
