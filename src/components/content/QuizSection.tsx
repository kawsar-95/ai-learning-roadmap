"use client";

import { useRef, useState } from "react";
import type { QuizQuestion } from "@/lib/content-schema";
import { scoreQuiz } from "@/lib/quiz";
import type { QuizAnswers } from "@/lib/quiz";
import { UI, fmtNum } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { saveQuizScore, useQuizScores } from "@/components/progress/useProgress";

type Choice = { value: number | boolean; label: string };

/** The choices of a question: the options of an `mcq`, or True and False. */
function choicesOf(question: QuizQuestion, lang: Lang): Choice[] {
  if (question.kind === "mcq") return question[lang].options.map((label, value) => ({ value, label }));
  return [
    { value: true, label: UI[lang].quizTrue },
    { value: false, label: UI[lang].quizFalse },
  ];
}

const BUTTON =
  "rounded-lg px-5 py-2.5 text-[15px] font-semibold transition disabled:cursor-not-allowed disabled:opacity-50";

/** The quiz at the end of a topic page: answer, check, see the score. The best score is saved. */
export function QuizSection({ slug, questions, lang }: { slug: string; questions: QuizQuestion[]; lang: Lang }) {
  const ui = UI[lang];
  const [answers, setAnswers] = useState<QuizAnswers>({});
  const [checked, setChecked] = useState(false);
  // The button that was pressed disappears, so focus goes to the next useful place.
  const retryRef = useRef<HTMLButtonElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const saved = useQuizScores()[slug];
  const best = saved && saved.total === questions.length ? saved : null;
  const allAnswered = questions.every((q) => q.id in answers);
  const { correct, total } = scoreQuiz(questions, answers);

  function check() {
    setChecked(true);
    saveQuizScore(slug, correct, total);
    requestAnimationFrame(() => retryRef.current?.focus());
  }

  function retry() {
    setAnswers({});
    setChecked(false);
    requestAnimationFrame(() => titleRef.current?.focus());
  }

  return (
    <section id="quiz" aria-labelledby="quiz-title" className="scroll-mt-24">
      <h2
        id="quiz-title"
        ref={titleRef}
        tabIndex={-1}
        className="font-display text-[clamp(1.75rem,3.6vw,2.25rem)] font-bold leading-[1.12] tracking-[-0.015em] text-text"
      >
        {ui.quizTitle}
      </h2>
      <p className="mt-3 text-[17px] leading-[1.75] text-text-dim">
        {ui.quizIntro(questions.length)}
        {best && (
          <span className="ml-2 inline-block font-mono text-[13px] whitespace-nowrap text-text-faint">
            {ui.quizBest(fmtNum(lang, best.best), fmtNum(lang, best.total))}
          </span>
        )}
      </p>

      <div className="mt-6 space-y-5">
        {questions.map((question, index) => {
          const text = question[lang];
          const right = answers[question.id] === question.answer;
          const rightLabel = choicesOf(question, lang).find((c) => c.value === question.answer)?.label;
          return (
            <div key={question.id} role="radiogroup" aria-labelledby={`${slug}-${question.id}-q`} className="rounded-2xl border border-border bg-bg-raised p-5 shadow-card sm:p-6">
              <p id={`${slug}-${question.id}-q`} className="m-0 mb-3 text-[17px] font-semibold leading-snug text-text">
                {fmtNum(lang, index + 1)}. {text.q}
              </p>
              <div className="space-y-2">
                {choicesOf(question, lang).map((choice) => {
                  const picked = answers[question.id] === choice.value;
                  let tone = "border-border-strong";
                  if (checked && choice.value === question.answer) tone = "border-good bg-bg-raised-2";
                  else if (checked && picked) tone = "border-danger";
                  else if (picked) tone = "border-accent bg-bg-raised-2";
                  return (
                    <label
                      key={String(choice.value)}
                      className={`flex items-start gap-3 rounded-lg border px-3 py-2.5 text-[16px] leading-snug text-text ${checked ? "" : "cursor-pointer"} ${tone}`}
                    >
                      <input
                        type="radio"
                        name={`${slug}-${question.id}`}
                        checked={picked}
                        disabled={checked}
                        onChange={() => setAnswers((a) => ({ ...a, [question.id]: choice.value }))}
                        className="mt-0.5 size-4 shrink-0 accent-accent"
                      />
                      <span>{choice.label}</span>
                    </label>
                  );
                })}
              </div>
              {checked && (
                <div className="mt-4 text-[15px] leading-relaxed text-text-dim">
                  <p className={`m-0 font-semibold ${right ? "text-good" : "text-danger"}`}>
                    <span aria-hidden="true">{right ? "✓" : "✗"}</span> {right ? ui.quizCorrect : ui.quizWrong}
                    {!right && (
                      <span className="font-normal text-text-dim">
                        {" "}
                        · {ui.quizRightAnswer} {rightLabel}
                      </span>
                    )}
                  </p>
                  <p className="mt-1 mb-0">{text.why}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-4">
        {/* Always in the page and never display:none, so screen readers announce the score when it
            appears. While empty it is absolute, so it takes no space in the row. */}
        <p role="status" className="m-0 font-display text-[22px] font-bold text-text empty:absolute">
          {checked ? ui.quizScore(fmtNum(lang, correct), fmtNum(lang, total)) : null}
        </p>
        {checked ? (
          <button type="button" ref={retryRef} onClick={retry} className={`${BUTTON} border border-border-strong bg-bg-raised text-text hover:border-accent`}>
            {ui.quizRetry}
          </button>
        ) : (
          <>
            <button type="button" onClick={check} disabled={!allAnswered} className={`${BUTTON} bg-accent text-on-accent shadow-card`}>
              {ui.quizCheck}
            </button>
            {!allAnswered && <p className="m-0 text-[14px] text-text-faint">{ui.quizAnswerAll}</p>}
          </>
        )}
      </div>
    </section>
  );
}
