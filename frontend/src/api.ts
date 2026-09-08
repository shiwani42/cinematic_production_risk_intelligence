import type { Brief, Callsheet, HazardRow, Stack } from "./types";

async function parse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  stack: async () => parse<Stack>(await fetch("/api/stack")),
  sample: async () =>
    parse<{
      script_text: string;
      callsheet: Callsheet;
      project_context: {
        production_type: string;
        who: Record<string, string>;
        what: Record<string, string>;
        where: Record<string, string>;
        when: Record<string, string>;
      };
    }>(await fetch("/api/sample")),
  analyze: async (body: unknown) =>
    parse<Brief>(
      await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }),
    ),
  ask: async (message: string, context: unknown) =>
    parse<{ text: string; tools_called: string[]; authors: string[] }>(
      await fetch("/api/agent/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, context }),
      }),
    ),
};

export function downloadJson(brief: Brief, rows: HazardRow[]) {
  const blob = new Blob([JSON.stringify({ ...brief, risk_register: rows }, null, 2)], {
    type: "application/json",
  });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "matrix-risk-assessment.json";
  a.click();
}
