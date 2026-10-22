import { Suspense } from "react";
import type { ReactNode } from "react";
import Link from "next/link";
import { TOPICS } from "@/lib/topics";
import type { NavItem } from "@/lib/topics";
import { UI, contentsHref, dashboardHref, homeHref, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { LanguageSwitch, LanguageSwitchFallback } from "./LanguageSwitch";
import { MobileNav } from "./MobileNav";
import { InstallButton } from "./InstallButton";
import { ThemeToggle } from "./ThemeToggle";

/** The menu button without behavior, shown until MobileNav can render. */
function MenuButtonPlaceholder() {
  return (
    <div className="lg:hidden">
      <span aria-hidden="true" className="-ml-1.5 grid size-8 place-items-center text-text-faint">
        <svg viewBox="0 0 20 20" className="size-5" fill="none">
          <path d="M3 5.5h14M3 10h14M3 14.5h9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      </span>
    </div>
  );
}

const NAV_LINK =
  "rounded-md px-3 py-1.5 text-[15px] font-medium text-text-dim no-underline transition-colors hover:bg-bg-raised-2 hover:text-text";

/**
 * The sticky 64px top bar: the menu button (below `lg`), the logo, the
 * page links (`lg` and wider), and on the right the search trigger slot,
 * the language switch, the install button, and the theme switch.
 */
export function SiteHeader({
  items,
  lang,
  searchSlot,
}: {
  items: NavItem[];
  lang: Lang;
  searchSlot?: ReactNode;
}) {
  return (
    <header className="sticky top-0 z-40 h-16 border-b border-border">
      {/* The blur sits on its own layer. A backdrop-filter on the header
          itself would trap the fixed-position drawer inside the header. */}
      <div aria-hidden="true" className="absolute inset-0 -z-10 bg-bg/85 backdrop-blur-md backdrop-saturate-150" />
      <div className="mx-auto flex h-full max-w-6xl items-center gap-2 px-4 sm:px-6">
        <Suspense fallback={<MenuButtonPlaceholder />}>
          <MobileNav items={items} lang={lang} />
        </Suspense>
        <Link href={homeHref(lang)} className="flex min-w-0 items-center gap-2.5 text-text no-underline">
          <span
            aria-hidden="true"
            className="grid size-9 shrink-0 place-items-center rounded-[10px] bg-accent font-display text-[17px] font-bold italic leading-none text-on-accent shadow-card"
          >
            Ai
          </span>
          <span className="truncate font-display text-[19px] font-bold leading-none tracking-tight">
            {UI[lang].siteName}
          </span>
        </Link>
        <nav aria-label={UI[lang].footerSite} className="ml-6 hidden items-center gap-1 lg:flex">
          <Link href={`${homeHref(lang)}#parts`} className={NAV_LINK}>
            {UI[lang].partsNav}
          </Link>
          <Link href={contentsHref(lang)} className={NAV_LINK}>
            {UI[lang].contents}
          </Link>
          <Link href={dashboardHref(lang)} className={NAV_LINK}>
            {UI[lang].dashboard}
          </Link>
        </nav>
        <div className="ml-auto flex items-center gap-1.5">
          {searchSlot}
          <Suspense fallback={<LanguageSwitchFallback lang={lang} />}>
            <LanguageSwitch lang={lang} />
          </Suspense>
          <InstallButton lang={lang} />
          <ThemeToggle lang={lang} />
          <Link
            href={topicHref(TOPICS[0].slug, lang)}
            className="ml-1 hidden items-center whitespace-nowrap rounded-lg bg-accent px-4 py-2 text-[14px] font-semibold text-on-accent no-underline shadow-card transition hover:-translate-y-0.5 md:inline-flex"
          >
            {UI[lang].startReading}
          </Link>
        </div>
      </div>
    </header>
  );
}
