"use client";

import { useEffect, useSyncExternalStore } from "react";
import { usePathname } from "next/navigation";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";

function subscribe(onChange: () => void) {
  window.addEventListener("online", onChange);
  window.addEventListener("offline", onChange);
  return () => {
    window.removeEventListener("online", onChange);
    window.removeEventListener("offline", onChange);
  };
}

/** `/roadmap/<phase>/<lesson>/`, in either language and under any base path. */
const LESSON_PATH = /\/roadmap\/[^/]+\/[^/]+\/?$/;

/**
 * A strip under the header while the device is offline. The service worker
 * saves the Parts, the contents page and the interview questions, but not the
 * 542 roadmap lessons (scripts/precache.mjs), so on the roadmap a lesson link
 * leads to a dead end unless the reader opened that lesson before. The strip
 * says so, and each lesson link that is not in any cache is dimmed and titled,
 * so the reader can tell which ones will open.
 */
export function OfflineNotice({ lang }: { lang: Lang }) {
  const online = useSyncExternalStore(
    subscribe,
    () => navigator.onLine,
    () => true,
  );
  const pathname = usePathname();
  const ui = UI[lang];

  useEffect(() => {
    if (online || !("caches" in window)) return;
    const marked: HTMLAnchorElement[] = [];
    let cancelled = false;
    for (const link of document.querySelectorAll<HTMLAnchorElement>("a[href*='/roadmap/']")) {
      if (!LESSON_PATH.test(new URL(link.href).pathname)) continue;
      caches.match(link.href, { ignoreSearch: true }).then((hit) => {
        if (hit || cancelled) return;
        link.setAttribute("data-online-only", "");
        link.title = ui.offlineLessonTitle;
        marked.push(link);
      });
    }
    return () => {
      cancelled = true;
      for (const link of marked) {
        link.removeAttribute("data-online-only");
        link.removeAttribute("title");
      }
    };
  }, [online, pathname, ui.offlineLessonTitle]);

  if (online) return null;
  return (
    <p role="status" className="m-0 border-b border-warn/40 bg-bg-raised-2 px-4 py-2 text-center text-[13px] leading-snug text-text-dim">
      {ui.offlineNotice}
    </p>
  );
}
