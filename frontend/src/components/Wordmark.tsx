export function Wordmark({ light = false }: { light?: boolean }) {
  const fill = light ? "#ffffff" : "#1b1b1b";
  return (
    <div className="flex items-center gap-2.5">
      <svg width="28" height="28" viewBox="0 0 32 32" fill="none" aria-hidden>
        <circle cx="16" cy="16" r="13" stroke="#ff671d" strokeWidth="2" />
        <path d="M16 5 L17.2 14.2 L27 16 L17.2 17.8 L16 27 L14.8 17.8 L5 16 L14.8 14.2 Z" fill="#ff671d" />
      </svg>
      <span className="font-display font-bold text-[17px] tracking-[0.18em] uppercase" style={{ color: fill }}>
        Matrix
      </span>
    </div>
  );
}
