"use client";

import { useEffect } from "react";

const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** The Network Information API is not in the TypeScript DOM types, and only Chromium has it. */
function isMeteredConnection(): boolean {
  const connection = (navigator as Navigator & { connection?: { saveData?: boolean; effectiveType?: string } }).connection;
  return Boolean(connection?.saveData) || connection?.effectiveType === "slow-2g" || connection?.effectiveType === "2g";
}

/**
 * Registers public/sw.js, which saves the whole site for offline use. Only in
 * production: in development the worker would keep stale dev files.
 *
 * The worker downloads the whole site when it installs, tens of megabytes. It
 * is registered after the page has loaded and the browser is idle, so that
 * download does not compete with the page the reader is looking at. It is not
 * registered at all when the reader asked the browser to save data, or the
 * connection is 2G: the site then works online only, which is better than a
 * silent download of tens of megabytes on that connection.
 */
export function ServiceWorker() {
  useEffect(() => {
    if (process.env.NODE_ENV !== "production" || !("serviceWorker" in navigator)) return;
    if (isMeteredConnection()) return;

    const register = () => {
      navigator.serviceWorker
        .register(`${BASE_PATH}/sw.js`, { scope: `${BASE_PATH}/`, updateViaCache: "none" })
        .catch(() => {
          // No worker: the site still works online.
        });
      // Ask the browser not to delete the saved site when storage is low.
      navigator.storage?.persist?.().catch(() => {});
    };
    // Safari has no requestIdleCallback; a short timeout does the same job.
    const whenIdle = () => {
      if ("requestIdleCallback" in window) window.requestIdleCallback(register, { timeout: 5000 });
      else setTimeout(register, 2000);
    };

    if (document.readyState === "complete") {
      whenIdle();
      return;
    }
    window.addEventListener("load", whenIdle, { once: true });
    return () => window.removeEventListener("load", whenIdle);
  }, []);

  return null;
}
