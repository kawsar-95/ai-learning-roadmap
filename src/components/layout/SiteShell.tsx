import type { ReactNode } from "react";
import Link from "next/link";
import { getNavItems } from "@/lib/topics";
import { REPO_URL, UI, contentsHref, dashboardHref, homeHref, interviewHref, resourcesHref, roadmapHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { SiteHeader } from "./SiteHeader";
import { SearchPalette } from "@/components/navigation/SearchPalette";

const FOOTER_LINK = "text-[14px] leading-snug text-text-dim no-underline transition-colors hover:text-accent";

/**
 * The footer: the brand with one line about the site, the site links in one
 * row, and the copyright. It does not list the Parts again: the home page,
 * the sidebar, and the mobile menu already do.
 */
function SiteFooter({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const links: [string, string][] = [
    [roadmapHref(lang), ui.roadmap],
    [resourcesHref(lang), ui.resources],
    [contentsHref(lang), ui.contentsTitle],
    [dashboardHref(lang), ui.dashboard],
    [interviewHref(lang), ui.interview],
  ];
  return (
    <footer className="border-t border-border bg-bg-raised-2">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6 md:flex-row md:items-start md:justify-between">
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
        <nav aria-label={ui.footerSite}>
          <ul className="m-0 flex list-none flex-wrap gap-x-6 gap-y-2.5 p-0">
            {links.map(([href, label]) => (
              <li key={href}>
                <Link href={href} className={FOOTER_LINK}>
                  {label}
                </Link>
              </li>
            ))}
            <li>
              <a href={REPO_URL} target="_blank" rel="noopener noreferrer" className={FOOTER_LINK}>
                {ui.footerSource} ↗
              </a>
            </li>
          </ul>
        </nav>
      </div>
      <div className="border-t border-border">
        <p className="mx-auto max-w-6xl px-4 py-4 text-[13px] text-text-faint sm:px-6">
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
      <SiteFooter lang={lang} />
    </div>
  );
}
