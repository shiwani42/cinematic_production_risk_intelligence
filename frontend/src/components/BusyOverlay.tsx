import { useEffect, useRef } from "react";
import gsap from "gsap";

export function BusyOverlay({ label }: { label: string }) {
  const bar = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = bar.current;
    if (!el) return;
    const tw = gsap.fromTo(el, { width: "12%" }, { width: "78%", duration: 2.4, ease: "power2.out" });
    return () => {
      tw.kill();
    };
  }, []);

  return (
    <div className="fixed inset-0 z-40 bg-ink/70 backdrop-blur-sm flex items-center justify-center no-print">
      <div className="w-full max-w-sm px-8 text-center text-white">
        <p className="font-display font-bold text-xl uppercase tracking-[0.12em]">Drafting your assessment</p>
        <p className="text-sm text-white/70 mt-2 normal-case tracking-normal font-normal">{label}</p>
        <div className="mt-6 h-1.5 bg-white/15 overflow-hidden cut">
          <div ref={bar} className="h-full bg-orange" />
        </div>
      </div>
    </div>
  );
}
