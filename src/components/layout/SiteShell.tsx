import type { ReactNode } from "react";
import Link from "next/link";
import { getNavItems } from "@/lib/topics";
import type { NavItem } from "@/lib/topics";
import { REPO_URL, UI, contentsHref, dashboardHref, fmtNum, homeHref, interviewHref, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { SiteHeader } from "./SiteHeader";
import { SearchPalette } from "@/components/navigation/SearchPalette";

const FOOTER_LINK = "text-[14px] leading-snug text-text-dim no-underline transition-colors hover:text-accent";
const FOOTER_HEAD = "mb-3 font-mono text-xs font-medium uppercase tracking-[0.16em] text-text-faint";

function PartLinks({ items, lang }: { items: NavItem[]; lang: Lang }) {
  return (
    <ul className="m-0 list-none space-y-2 p-0">
      {items.map((item) => (
        <li key={item.slug}>
          <Link href={topicHref(item.slug, lang)} className={FOOTER_LINK}>
            <span className="mr-2 font-mono text-[12px] text-text-faint">
              {fmtNum(lang, item.part).padStart(2, fmtNum(lang, 0))}
            </span>
            {item.title}
          </Link>
        </li>
      ))}
    </ul>
  );
}

/** The footer: the brand, the Parts in two columns, and the site links. */
function SiteFooter({ items, lang }: { items: NavItem[]; lang: Lang }) {
  const ui = UI[lang];
  const half = Math.ceil(items.length / 2);
  return (
    <footer className="border-t border-border bg-bg-raised-2">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:px-6 md:grid-cols-[1.2fr_1fr_1fr_0.8fr]">
        <div>
          <Link href={homeHref(lang)} className="inline-flex items-center gap-2.5 text-text no-underline">
            <span
              aria-hidden="true"
              className="grid size-8 place-items-center rounded-[9px] bg-accent font-display text-[15px] font-bold italic text-on-accent"
            >
              Ai
            </span>
            <span className="font-display text-lg font-bold">{ui.siteName}</span>
          </Link>
          <p className="mt-3 max-w-xs text-[14px] leading-relaxed text-text-dim">{ui.footer}</p>
        </div>
        <div>
          <p className={FOOTER_HEAD}>{ui.partsNav}</p>
          <PartLinks items={items.slice(0, half)} lang={lang} />
        </div>
        <div>
          <p aria-hidden="true" className={FOOTER_HEAD + " max-md:hidden"}>
            &nbsp;
          </p>
          <PartLinks items={items.slice(half)} lang={lang} />
        </div>
        <div>
          <p className={FOOTER_HEAD}>{ui.footerSite}</p>
          <ul className="m-0 list-none space-y-2 p-0">
            <li>
              <Link href={contentsHref(lang)} className={FOOTER_LINK}>
                {ui.contentsTitle}
              </Link>
            </li>
            <li>
              <Link href={dashboardHref(lang)} className={FOOTER_LINK}>
                {ui.dashboard}
              </Link>
            </li>
            <li>
              <Link href={interviewHref(lang)} className={FOOTER_LINK}>
                {ui.interview}
              </Link>
            </li>
            <li>
              <a href={REPO_URL} target="_blank" rel="noopener noreferrer" className={FOOTER_LINK}>
                {ui.footerSource} ↗
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t border-border">
        <p className="mx-auto max-w-6xl px-4 py-5 text-[13px] text-text-faint sm:px-6">
          © {lang === "bn" ? "২০২৬" : "2026"} {ui.footerCopy}
        </p>
      </div>
    </footer>
  );
}

/**
 * Everything around a page in one language: the skip link, the header, and
 * the footer. The English and Bangla layouts and the 404 page use it. The
 * topic pages add the sidebar of Parts themselves.
 */
export function SiteShell({ lang, children }: { lang: Lang; children: ReactNode }) {
  const items = getNavItems(lang);
  const ui = UI[lang];
  return (
    <div lang={lang} className="flex min-h-screen flex-col">
      <a
        href="#content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-md focus:border focus:border-accent focus:bg-bg-raised focus:px-4 focus:py-2 focus:text-sm focus:text-text"
      >
        {ui.skipLink}
      </a>
      <SiteHeader items={items} lang={lang} searchSlot={<SearchPalette lang={lang} />} />
      {/* The inline style beats the global :focus-visible rule for the skip-link target. */}
      <main id="content" tabIndex={-1} style={{ outline: "none" }} className="min-w-0 flex-1">
        {children}
      </main>
      <SiteFooter items={items} lang={lang} />
    </div>
  );
}
