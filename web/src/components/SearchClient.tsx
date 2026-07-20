"use client";

import { useDeferredValue, useMemo, useState } from "react";
import Link from "next/link";
import type { PrayerSummary, PsalmSummary } from "@/lib/types";
import { psalmEnglishName, psalmMatchesQuery } from "@/lib/psalm-label";
import { TraditionPills } from "./SeasonCard";

type SearchHit =
  | { kind: "prayer"; item: PrayerSummary }
  | { kind: "psalm"; item: PsalmSummary };

export function SearchClient({
  prayers,
  psalms,
}: {
  prayers: PrayerSummary[];
  psalms: PsalmSummary[];
}) {
  const [q, setQ] = useState("");
  const deferred = useDeferredValue(q.trim());

  const results = useMemo(() => {
    if (!deferred) return [] as SearchHit[];
    const needle = deferred.toLowerCase();
    const out: SearchHit[] = [];

    for (const p of psalms) {
      if (psalmMatchesQuery(p, deferred)) {
        out.push({ kind: "psalm", item: p });
        if (out.length >= 80) return out;
      }
    }

    for (const p of prayers) {
      const traditionHay = p.tradition
        .map((t) =>
          t === "syriac" ? "assyrian syriac" : t === "chaldean" ? "chaldean" : t,
        )
        .join(" ");
      const hay =
        `${p.name} ${p.holiday} ${p.holidayEn || ""} ${p.week} ${p.day} ${p.dayEn} ${p.hour} ${p.hourEn} ${traditionHay}`.toLowerCase();
      if (hay.includes(needle) || p.name.includes(deferred)) {
        out.push({ kind: "prayer", item: p });
        if (out.length >= 80) break;
      }
    }
    return out;
  }, [deferred, prayers, psalms]);

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
          placeholder="Name, season, day, hour, psalm number…"
          className="w-full rounded-sm border border-line bg-paper/80 px-4 py-3 text-base text-ink outline-none ring-teal/30 placeholder:text-ink-soft/50 focus:ring-2"
          dir="auto"
        />
      </label>

      <div className="mt-6">
        {!deferred ? (
          <p className="text-sm text-ink-soft">
            Try a season name, weekday, hour, or psalm number.
          </p>
        ) : results.length === 0 ? (
          <p className="text-sm text-ink-soft">
            Nothing matched “{deferred}”.
          </p>
        ) : (
          <ul className="divide-y divide-line border border-line bg-paper/60">
            {results.map((hit) =>
              hit.kind === "psalm" ? (
                <li key={`psalm-${hit.item.id}`}>
                  <Link
                    href={`/psalm/${hit.item.id}`}
                    className="flex flex-col gap-1 px-4 py-4 transition hover:bg-paper-deep/50 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div>
                      <p className="syr syr-meta text-2xl text-ink">
                        {hit.item.name}
                      </p>
                      <p className="mt-1 text-sm text-ink-soft">
                        {psalmEnglishName(hit.item)}
                      </p>
                    </div>
                    <span
                      className="text-xs tracking-wide text-ink-soft uppercase"
                      style={{
                        fontFamily: "var(--font-display), Georgia, serif",
                      }}
                    >
                      Psalm
                    </span>
                  </Link>
                </li>
              ) : (
                <li key={`prayer-${hit.item.id}`}>
                  <Link
                    href={`/prayer/${hit.item.id}`}
                    className="flex flex-col gap-2 px-4 py-4 transition hover:bg-paper-deep/50 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div>
                      <p className="syr syr-meta text-2xl text-ink">
                        {hit.item.name}
                      </p>
                      <p className="mt-1 text-sm text-ink-soft">
                        {[
                          hit.item.holidayEn,
                          hit.item.hourEn || hit.item.hour,
                          hit.item.dayEn || hit.item.day,
                          hit.item.week,
                        ]
                          .filter(Boolean)
                          .join(" · ")}
                      </p>
                    </div>
                    <TraditionPills tradition={hit.item.tradition} />
                  </Link>
                </li>
              ),
            )}
          </ul>
        )}
      </div>
    </div>
  );
}
