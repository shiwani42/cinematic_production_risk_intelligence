import { cn } from "../lib/cn";

export function Stepper({
  items,
  current,
  onPick,
}: {
  items: { id: string; label: string }[];
  current: string;
  onPick: (id: string) => void;
}) {
  const idx = items.findIndex((i) => i.id === current);
  return (
    <ol className="flex flex-wrap gap-2 mb-10" data-reveal>
      {items.map((item, i) => {
        const done = i < idx;
        const active = item.id === current;
        return (
          <li key={item.id}>
            <button
              type="button"
              onClick={() => onPick(item.id)}
              className={cn(
                "cut flex items-center gap-2 px-3 py-2 text-[13px] font-display font-bold uppercase tracking-[0.14em] transition-colors",
                active && "bg-orange text-white",
                done && "bg-peach text-ink",
                !active && !done && "bg-white text-muted hover:text-ink",
              )}
            >
              <span className={cn("text-[11px]", active ? "text-white" : "text-orange")}>{String(i + 1).padStart(2, "0")}</span>
              {item.label}
            </button>
          </li>
        );
      })}
    </ol>
  );
}
