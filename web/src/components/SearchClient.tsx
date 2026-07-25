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

type MatchMode = "all" | "any" | "phrase";
type KindFilter = "all" | "prayer" | "psalm";
type TraditionFilter = "all" | "syriac" | "chaldean";

type PagefindResult = {
  id: string;
  score?: number;
  data: () => Promise<PagefindHit>;
};

type PagefindApi = {
  options: (opts: Record<string, unknown>) => Promise<void>;
  init: () => Promise<void>;
  search: (
    query: string,
    opts?: {
      filters?: Record<string, string | string[]>;
    },
  ) => Promise<{ results: PagefindResult[] }>;
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

function buildFilters(
  kind: KindFilter,
  tradition: TraditionFilter,
): Record<string, string | string[]> | undefined {
  const filters: Record<string, string | string[]> = {};
  if (kind !== "all") filters.kind = kind;
  // Psalms aren't tagged with tradition in the index.
  if (tradition !== "all" && kind !== "psalm") {
    filters.tradition = tradition;
  }
  return Object.keys(filters).length ? filters : undefined;
}

function tokenize(needle: string): string[] {
  return needle.split(/\s+/).filter(Boolean);
}

async function runSearch(
  pagefind: PagefindApi,
  needle: string,
  mode: MatchMode,
  filters?: Record<string, string | string[]>,
): Promise<PagefindResult[]> {
  const opts = filters ? { filters } : undefined;
  const terms = tokenize(needle);

  if (mode === "phrase") {
    const phrase = `"${needle.replace(/"/g, "").trim()}"`;
    const search = await pagefind.search(phrase, opts);
    return search.results;
  }

  if (mode === "any" && terms.length > 1) {
    const searches = await Promise.all(
      terms.map((t) => pagefind.search(t, opts)),
    );
    const byId = new Map<string, PagefindResult>();
    for (const s of searches) {
      for (const r of s.results) {
        const prev = byId.get(r.id);
        if (!prev || (r.score ?? 0) > (prev.score ?? 0)) {
          byId.set(r.id, r);
        }
      }
    }
    return [...byId.values()].sort(
      (a, b) => (b.score ?? 0) - (a.score ?? 0),
    );
  }

  // "all" words — Pagefind's default AND matching
  const search = await pagefind.search(needle, opts);
  return search.results;
}

function OptionGroup<T extends string>({
  label,
  value,
  onChange,
  options,
  disabled,
}: {
  label: string;
  value: T;
  onChange: (v: T) => void;
  options: { id: T; label: string; activeClass?: string }[];
  disabled?: boolean;
}) {
  return (
    <div className="min-w-0">
      <p className="mb-1.5 text-[11px] tracking-[0.14em] text-ink-soft uppercase">
        {label}
      </p>
      <div className="flex flex-wrap gap-1.5" role="group" aria-label={label}>
        {options.map((opt) => {
          const active = value === opt.id;
          return (
            <button
              key={opt.id}
              type="button"
              disabled={disabled}
              aria-pressed={active}
              onClick={() => onChange(opt.id)}
              className={`rounded-sm border px-2.5 py-1.5 text-sm transition disabled:opacity-50 ${
                active
                  ? (opt.activeClass ??
                    "border-teal/50 bg-teal-deep text-white")
                  : "border-line bg-paper/80 text-ink-soft hover:border-teal/40 hover:text-ink"
              }`}
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function SearchClient() {
  const [q, setQ] = useState("");
  const deferred = useDeferredValue(q.trim());
  const [matchMode, setMatchMode] = useState<MatchMode>("all");
  const [kind, setKind] = useState<KindFilter>("all");
  const [tradition, setTradition] = useState<TraditionFilter>("all");
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
  const filters = useMemo(
    () => buildFilters(kind, tradition),
    [kind, tradition],
  );

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
        const results = await runSearch(
          pagefind,
          needle,
          matchMode,
          filters,
        );
        const top = results.slice(0, 60);
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
  }, [pagefind, needle, matchMode, filters]);

  const controlsDisabled = loadingIndex || loadError;

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
          disabled={controlsDisabled}
        />
      </label>

      <div className="mt-5 flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:gap-x-8 sm:gap-y-4">
        <OptionGroup
          label="Match"
          value={matchMode}
          onChange={setMatchMode}
          disabled={controlsDisabled}
          options={[
            { id: "all", label: "AND" },
            { id: "any", label: "OR" },
            { id: "phrase", label: "Exact phrase" },
          ]}
        />
        <OptionGroup
          label="Type"
          value={kind}
          onChange={setKind}
          disabled={controlsDisabled}
          options={[
            { id: "all", label: "All" },
            { id: "prayer", label: "Prayers" },
            { id: "psalm", label: "Psalms" },
          ]}
        />
        <OptionGroup
          label="Tradition"
          value={tradition}
          onChange={setTradition}
          disabled={controlsDisabled || kind === "psalm"}
          options={[
            { id: "all", label: "All" },
            {
              id: "syriac",
              label: "Assyrian",
              activeClass: "border-teal/50 bg-teal-deep text-white",
            },
            {
              id: "chaldean",
              label: "Chaldean",
              activeClass:
                "border-gold/55 bg-[color:var(--gold)] text-white",
            },
          ]}
        />
      </div>

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
          <>
            <p className="mb-3 text-xs tracking-wide text-ink-soft tabular-nums">
              {hits.length}
              {hits.length >= 60 ? "+" : ""}{" "}
              {hits.length === 1 ? "result" : "results"}
            </p>
            <ul className="divide-y divide-line border border-line bg-paper/60">
              {hits.map((hit) => {
                const hitKind = hit.meta.kind || "prayer";
                const hitTradition = parseTradition(hit.meta.tradition);
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
                          {hitKind === "psalm" ? "Psalm" : "Prayer"}
                        </span>
                        {hitTradition.length > 0 ? (
                          <TraditionPills tradition={hitTradition} />
                        ) : null}
                      </div>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}
