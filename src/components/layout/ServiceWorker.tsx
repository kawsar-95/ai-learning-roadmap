"use client";

import { useEffect } from "react";

const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/**
 * Registers public/sw.js, which saves the whole site for offline use. Only in
 * production: in development the worker would keep stale dev files.
 */
export function ServiceWorker() {
  useEffect(() => {
    if (process.env.NODE_ENV !== "production" || !("serviceWorker" in navigator)) return;
    navigator.serviceWorker
      .register(`${BASE_PATH}/sw.js`, { scope: `${BASE_PATH}/`, updateViaCache: "none" })
      .catch(() => {
        // No worker: the site still works online.
      });
    // Ask the browser not to delete the saved site when storage is low.
    navigator.storage?.persist?.().catch(() => {});
  }, []);

  return null;
}
