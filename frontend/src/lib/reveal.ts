import gsap from "gsap";

export function reveal(root: HTMLElement | null) {
  if (!root) return;
  const items = root.querySelectorAll("[data-reveal]");
  if (!items.length) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    gsap.set(items, { clearProps: "all" });
    return;
  }
  gsap.fromTo(
    items,
    { y: 22, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.7, stagger: 0.07, ease: "power3.out", overwrite: true },
  );
}
