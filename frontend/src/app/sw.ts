import { defaultCache } from "@serwist/next/worker";
import type { PrecacheEntry, SerwistGlobalConfig } from "serwist";
import { NetworkFirst, NetworkOnly } from "serwist";
import { Serwist } from "serwist";

declare global {
  interface WorkerGlobalScope extends SerwistGlobalConfig {
    __SW_MANIFEST: (PrecacheEntry | string)[] | undefined;
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const self: WorkerGlobalScope & typeof globalThis;

const runtimeCaching = [
  // Non-GET requests (POST, PUT, DELETE) always bypass cache entirely
  {
    matcher: ({ request }: { request: Request }) => request.method !== "GET",
    handler: new NetworkOnly(),
  },
  // GET API calls use network-first with generous timeout for mobile
  {
    matcher: /\/api\//,
    handler: new NetworkFirst({ networkTimeoutSeconds: 30 }),
  },
  ...defaultCache,
];

const serwist = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  skipWaiting: true,
  clientsClaim: true,
  navigationPreload: true,
  runtimeCaching,
});

serwist.addEventListeners();
