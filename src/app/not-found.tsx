import Link from "next/link";
import { SiteShell } from "@/components/layout/SiteShell";
import { PAGE_TITLE } from "@/components/layout/PageHeader";
import { UI } from "@/lib/i18n";

const LINK = "text-[16px] font-medium text-accent no-underline hover:underline";

/**
 * The one 404 page for both languages (GitHub Pages serves it for every
 * unknown URL). It shows the English text with the Bangla text under it.
 * Like every other page, it opens with the title, with no label above it.
 * Its language switch opens the Bangla home page, because the URL asked for
 * is not a page in either language.
 */
export default function NotFound() {
  const { en, bn } = UI;
  return (
    <SiteShell lang="en" languageSwitchToHome>
      <div className="mx-auto max-w-2xl px-4 pt-12 pb-20 sm:px-6 sm:pt-16">
        <h1 className={PAGE_TITLE}>{en.notFoundTitle}</h1>
        <p lang="bn" className="mt-2 font-display text-2xl text-text-dim">
          {bn.notFoundTitle}
        </p>
        <p className="mt-6 text-lg leading-relaxed text-pretty text-text-dim">{en.notFoundText}</p>
        <p lang="bn" className="mt-2 text-lg leading-relaxed text-pretty text-text-dim">
          {bn.notFoundText}
        </p>
        <p className="mt-10 flex flex-wrap gap-x-8 gap-y-3 border-t border-border pt-6">
          <Link href="/" className={LINK}>
            {en.notFoundBack}
          </Link>
          <Link href="/bn/" lang="bn" className={LINK}>
            {bn.notFoundBack}
          </Link>
        </p>
      </div>
    </SiteShell>
  );
}
