import { defaultCache } from "@serwist/next/worker";
import type { PrecacheEntry, SerwistGlobalConfig } from "serwist";
import { Serwist } from "serwist";

declare global {
  interface WorkerGlobalScope extends SerwistGlobalConfig {
    __SW_MANIFEST: (PrecacheEntry | string)[] | undefined;
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const self: WorkerGlobalScope & typeof globalThis;

const serwist = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  skipWaiting: true,
  clientsClaim: true,
  navigationPreload: false,
  runtimeCaching: defaultCache,
});

// Intercept fetch BEFORE Serwist to bypass the service worker entirely
// for API calls and non-GET requests. This prevents caching interference
// that causes "Failed to fetch" on mobile PWA.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
self.addEventListener("fetch", (event: any) => {
  const request = event.request as Request;

  // Non-GET requests (POST, PUT, DELETE): pass directly to network
  if (request.method !== "GET") {
    event.respondWith(fetch(request));
    return;
  }

  // API calls: always go to network, never cache
  const url = new URL(request.url);
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(fetch(request));
    return;
  }
});

// Serwist handles caching for static assets only (JS, CSS, images, fonts)
serwist.addEventListeners();
