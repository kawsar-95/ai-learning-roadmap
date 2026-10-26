"use client";

import { useRef, useState } from "react";
import type { FormEvent } from "react";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { useRoadmapProgress } from "@/components/progress/useProgress";

type Message = { role: "user" | "assistant"; content: string };

const TUTOR_URL = process.env.NEXT_PUBLIC_TUTOR_URL;

/** Reads the event stream of the tutor endpoint and calls back with each event. */
async function readEvents(response: Response, onEvent: (event: Record<string, unknown>) => void) {
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No stream");
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      if (part.startsWith("data: ")) onEvent(JSON.parse(part.slice(6)));
    }
  }
}

/**
 * A chat box that asks the tutor endpoint. It sends the lessons the learner
 * ticked off, so answers fit their progress, and `lesson` ("<phase folder>/
 * <lesson folder>") when the box sits on a lesson page. It renders nothing unless
 * NEXT_PUBLIC_TUTOR_URL was set when the site was built.
 */
export function TutorPanel({ lang, lesson }: { lang: Lang; lesson?: string }) {
  const ui = UI[lang];
  const done = useRoadmapProgress();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [reading, setReading] = useState<string | null>(null);
  const abort = useRef<AbortController | null>(null);

  if (!TUTOR_URL) return null;

  async function ask(event: FormEvent) {
    event.preventDefault();
    const question = input.trim();
    if (!question || busy) return;
    const history: Message[] = [...messages, { role: "user", content: question }];
    setMessages([...history, { role: "assistant", content: "" }]);
    setInput("");
    setNotice(null);
    setBusy(true);
    abort.current = new AbortController();
    try {
      const response = await fetch(TUTOR_URL!, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ messages: history.slice(-20), done: [...done], ...(lesson ? { lesson } : {}) }),
        signal: abort.current.signal,
      });
      if (!response.ok) throw new Error(String(response.status));
      await readEvents(response, (data) => {
        if (typeof data.reading === "string") {
          setReading(data.reading);
        } else if (typeof data.text === "string") {
          const text = data.text;
          setReading(null);
          setMessages((current) => {
            const last = current[current.length - 1];
            return [...current.slice(0, -1), { ...last, content: last.content + text }];
          });
        } else if (data.stopReason === "refusal") {
          setNotice(ui.tutorRefusal);
        } else if (typeof data.error === "string") {
          setNotice(ui.tutorError);
        }
      });
    } catch (error) {
      if ((error as Error).name !== "AbortError") setNotice(ui.tutorError);
    } finally {
      setReading(null);
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="tutor-title" className="mt-10 rounded-2xl border border-border bg-bg-raised p-6 shadow-card sm:p-8">
      <h2 id="tutor-title" className="m-0 font-display text-[24px] font-bold text-text">
        {ui.tutorTitle}
      </h2>
      <p className="mt-1 mb-4 text-[15px] text-text-dim">{lesson ? ui.tutorLessonIntro : ui.tutorIntro}</p>

      <div aria-live="polite" className="space-y-3">
        {messages.map((message, i) => (
          <div
            key={i}
            className={
              "whitespace-pre-wrap rounded-xl px-4 py-3 text-[15px] leading-relaxed " +
              (message.role === "user" ? "bg-bg-raised-2 text-text" : "border border-border text-text-dim")
            }
          >
            <span className="mb-1 block font-mono text-[11px] tracking-[0.12em] text-text-faint uppercase">
              {message.role === "user" ? ui.tutorYou : ui.tutorName}
            </span>
            {message.content || (busy && i === messages.length - 1 ? (reading ? ui.tutorReading(reading) : ui.tutorThinking) : "")}
          </div>
        ))}
        {notice && <p className="m-0 text-[14px] text-danger">{notice}</p>}
      </div>

      <form onSubmit={ask} className="mt-4 flex flex-col gap-3 sm:flex-row">
        <label htmlFor="tutor-input" className="sr-only">
          {ui.tutorLabel}
        </label>
        <input
          id="tutor-input"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          maxLength={4000}
          placeholder={ui.tutorPlaceholder}
          className="min-w-0 flex-1 rounded-[10px] border border-border-strong bg-bg px-4 py-2.5 text-[15px] text-text"
        />
        <button
          type="submit"
          disabled={busy || input.trim() === ""}
          className="rounded-[10px] bg-accent px-5 py-2.5 text-[15px] font-semibold text-on-accent shadow-card disabled:opacity-40"
        >
          {ui.tutorSend}
        </button>
        {messages.length > 0 && (
          <button
            type="button"
            onClick={() => {
              abort.current?.abort();
              setMessages([]);
              setNotice(null);
            }}
            className="rounded-[10px] border border-border-strong px-5 py-2.5 text-[15px] font-medium text-text-dim hover:border-danger hover:text-danger"
          >
            {ui.tutorClear}
          </button>
        )}
      </form>
    </section>
  );
}
