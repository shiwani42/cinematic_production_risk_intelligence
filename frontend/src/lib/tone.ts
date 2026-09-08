export function tone(label?: string) {
  const t = (label || "").toLowerCase();
  if (t.includes("crit")) return "text-crit";
  if (t.includes("high")) return "text-orange";
  if (t.includes("med")) return "text-muted";
  return "text-ok";
}

export const fieldClass =
  "w-full cut border border-line bg-white px-3.5 py-2.5 text-[16px] font-sans text-ink placeholder:text-muted outline-none focus:border-orange focus:ring-2 focus:ring-orange/20";
