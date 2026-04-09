// Cleanup service worker — replaces any stale cached SW.
// Serwist doesn't compile with Turbopack (Next.js 16 default),
// so this static file ensures the old SW is replaced and all
// requests pass through to the network without interference.

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  // Take control of all clients immediately
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.map((name) => caches.delete(name)))
    ).then(() => self.clients.claim())
  );
});

// All fetch requests pass through to the network — no caching
self.addEventListener("fetch", () => {
  // Do nothing — let the browser handle it naturally
});
