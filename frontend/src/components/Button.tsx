import { type ButtonHTMLAttributes } from "react";
import { cn } from "../lib/cn";

export function Button({
  variant = "primary",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" | "outline" | "teal" }) {
  return (
    <button
      type="button"
      className={cn(
        "cut inline-flex items-center justify-center px-5 py-2.5 text-[15px] font-display font-bold uppercase tracking-[0.12em] transition-colors disabled:opacity-50 disabled:pointer-events-none",
        variant === "primary" && "bg-orange text-white hover:bg-[#e55a14]",
        variant === "teal" && "bg-orange text-white hover:bg-[#e55a14]",
        variant === "outline" && "border border-orange text-orange bg-transparent hover:bg-peach",
        variant === "ghost" && "text-ink bg-transparent hover:bg-cream",
        className,
      )}
      {...props}
    />
  );
}
