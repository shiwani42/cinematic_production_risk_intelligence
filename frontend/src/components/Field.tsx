import { type ReactNode } from "react";

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="block mb-6">
      <span className="block font-display font-bold text-[13px] uppercase tracking-[0.14em] text-ink">{label}</span>
      {hint ? <span className="block text-sm text-muted mt-1 mb-2 normal-case tracking-normal font-sans font-normal">{hint}</span> : <span className="block h-2" />}
      {children}
    </label>
  );
}

export function PageTitle({ eyebrow, title, children }: { eyebrow?: string; title: string; children?: ReactNode }) {
  return (
    <div className="mb-8" data-reveal>
      {eyebrow && (
        <p className="text-[12px] font-display font-bold text-orange uppercase tracking-[0.2em] mb-3">{eyebrow}</p>
      )}
      <h1 className="font-display font-bold text-[clamp(1.7rem,3vw,2.4rem)] text-ink leading-tight">{title}</h1>
      {children && <p className="mt-3 text-[17px] text-slate max-w-xl leading-relaxed normal-case tracking-normal font-sans font-normal">{children}</p>}
    </div>
  );
}
