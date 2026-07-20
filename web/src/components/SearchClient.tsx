"use client";

import Link from "next/link";
import {
  useDeferredValue,
  useEffect,
  useMemo,
  useState,
} from "react";
import { TraditionPills } from "@/components/SeasonCard";
import { depointSyriac } from "@/lib/depoint-syriac";
import type { Tradition } from "@/lib/types";

type PagefindApi = {
  options: (opts: Record<string, unknown>) => Promise<void>;
  init: () => Promise<void>;
  search: (
    query: string,
  ) => Promise<{
    results: { id: string; data: () => Promise<PagefindHit> }[];
  }>;
};

type PagefindHit = {
  url: string;
  excerpt: string;
  meta: {
    title?: string;
    kind?: string;
    subtitle?: string;
    tradition?: string;
  };
};

function assetUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
  return `${base}${path}`;
}

/** Strip basePath from Pagefind URLs for Next.js Link hrefs. */
function appPath(url: string): string {
  const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
  if (base && url.startsWith(base)) return url.slice(base.length) || "/";
  try {
    const u = new URL(url, "https://example.local");
    return u.pathname + u.search + u.hash;
  } catch {
    return url;
  }
}

function parseTradition(raw?: string): Tradition[] {
  if (!raw) return [];
  return raw
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean) as Tradition[];
}

export function SearchClient() {
  const [q, setQ] = useState("");
  const deferred = useDeferredValue(q.trim());
  const [pagefind, setPagefind] = useState<PagefindApi | null>(null);
  const [loadError, setLoadError] = useState(false);
  const [loadingIndex, setLoadingIndex] = useState(true);
  const [searching, setSearching] = useState(false);
  const [hits, setHits] = useState<PagefindHit[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
        const mod = (await import(
          /* webpackIgnore: true */
          assetUrl("/pagefind/pagefind.js")
        )) as PagefindApi;
        await mod.options({
          baseUrl: base ? `${base}/` : "/",
          excerptLength: 40,
        });
        await mod.init();
        if (!cancelled) {
          setPagefind(mod);
          setLoadError(false);
        }
      } catch {
        if (!cancelled) setLoadError(true);
      } finally {
        if (!cancelled) setLoadingIndex(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const needle = useMemo(() => depointSyriac(deferred).trim(), [deferred]);

  useEffect(() => {
    if (!pagefind || !needle) {
      setHits([]);
      setSearching(false);
      return;
    }

    let cancelled = false;
    setSearching(true);
    (async () => {
      try {
        const search = await pagefind.search(needle);
        const top = search.results.slice(0, 60);
        const data = await Promise.all(top.map((r) => r.data()));
        if (!cancelled) setHits(data);
      } catch {
        if (!cancelled) setHits([]);
      } finally {
        if (!cancelled) setSearching(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [pagefind, needle]);

  return (
    <div>
      <label className="block">
        <span
          className="mb-2 block text-xs tracking-[0.18em] text-gold uppercase"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Search prayers & psalms
        </span>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Syriac text (with or without points), season, psalm…"
          className="w-full rounded-sm border border-line bg-paper/80 px-4 py-3 text-base text-ink outline-none ring-teal/30 placeholder:text-ink-soft/50 focus:ring-2"
          dir="auto"
          disabled={loadingIndex || loadError}
        />
      </label>

      <div className="mt-6">
        {loadingIndex ? (
          <p className="text-sm text-ink-soft">Loading search index…</p>
        ) : loadError ? (
          <p className="text-sm text-ink-soft">
            Search index not found. Run{" "}
            <code className="text-ink">npm run index:search</code> (dev) or{" "}
            <code className="text-ink">npm run build</code> to generate it.
          </p>
        ) : !deferred ? (
          <p className="text-sm text-ink-soft">
            Full-text search ignores vowel points — pointed or unpointed queries
            both work.
          </p>
        ) : searching && hits.length === 0 ? (
          <p className="text-sm text-ink-soft">Searching…</p>
        ) : hits.length === 0 ? (
          <p className="text-sm text-ink-soft">
            Nothing matched “{deferred}”.
          </p>
        ) : (
          <ul className="divide-y divide-line border border-line bg-paper/60">
            {hits.map((hit) => {
              const kind = hit.meta.kind || "prayer";
              const tradition = parseTradition(hit.meta.tradition);
              return (
                <li key={hit.url}>
                  <Link
                    href={appPath(hit.url)}
                    className="flex flex-col gap-2 px-4 py-4 transition hover:bg-paper-deep/50 sm:flex-row sm:items-start sm:justify-between"
                  >
                    <div className="min-w-0">
                      <p className="syr syr-meta text-2xl text-ink">
                        {hit.meta.title || "Result"}
                      </p>
                      {hit.meta.subtitle ? (
                        <p className="mt-1 text-sm text-ink-soft">
                          {hit.meta.subtitle}
                        </p>
                      ) : null}
                      {hit.excerpt ? (
                        <p
                          className="syr syr-meta mt-2 text-lg leading-relaxed text-ink-soft [&_mark]:bg-gold/25 [&_mark]:text-ink"
                          dir="rtl"
                          dangerouslySetInnerHTML={{ __html: hit.excerpt }}
                        />
                      ) : null}
                    </div>
                    <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
                      <span
                        className="text-xs tracking-wide text-ink-soft uppercase"
                        style={{
                          fontFamily: "var(--font-display), Georgia, serif",
                        }}
                      >
                        {kind === "psalm" ? "Psalm" : "Prayer"}
                      </span>
                      {tradition.length > 0 ? (
                        <TraditionPills tradition={tradition} />
                      ) : null}
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
