"use client";

import { useDeferredValue, useMemo, useState } from "react";
import Link from "next/link";
import type { PrayerSummary } from "@/lib/types";
import { TraditionPills } from "./SeasonCard";

export function SearchClient({ prayers }: { prayers: PrayerSummary[] }) {
  const [q, setQ] = useState("");
  const deferred = useDeferredValue(q.trim());

  const results = useMemo(() => {
    if (!deferred) return [];
    const needle = deferred.toLowerCase();
    const out: PrayerSummary[] = [];
    for (const p of prayers) {
      const traditionHay = p.tradition
        .map((t) =>
          t === "syriac" ? "assyrian syriac" : t === "chaldean" ? "chaldean" : t,
        )
        .join(" ");
      const hay =
        `${p.name} ${p.holiday} ${p.holidayEn || ""} ${p.week} ${p.day} ${p.dayEn} ${p.hour} ${p.hourEn} ${traditionHay}`.toLowerCase();
      if (hay.includes(needle) || p.name.includes(deferred)) {
        out.push(p);
        if (out.length >= 80) break;
      }
    }
    return out;
  }, [deferred, prayers]);

  return (
    <div>
      <label className="block">
        <span
          className="mb-2 block text-xs tracking-[0.18em] text-gold uppercase"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Search prayers
        </span>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Name, season, day, hour…"
          className="w-full rounded-sm border border-line bg-paper/80 px-4 py-3 text-base text-ink outline-none ring-teal/30 placeholder:text-ink-soft/50 focus:ring-2"
          dir="auto"
        />
      </label>

      <div className="mt-6">
        {!deferred ? (
          <p className="text-sm text-ink-soft">
            Try a season name, weekday, or hour from the corpus.
          </p>
        ) : results.length === 0 ? (
          <p className="text-sm text-ink-soft">No prayers matched “{deferred}”.</p>
        ) : (
          <ul className="divide-y divide-line border border-line bg-paper/60">
            {results.map((p) => (
              <li key={p.id}>
                <Link
                  href={`/prayer/${p.id}`}
                  className="flex flex-col gap-2 px-4 py-4 transition hover:bg-paper-deep/50 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div>
                    <p className="syr syr-meta text-2xl text-ink">{p.name}</p>
                    <p className="mt-1 text-sm text-ink-soft">
                      {[
                        p.holidayEn,
                        p.hourEn || p.hour,
                        p.dayEn || p.day,
                        p.week,
                      ]
                        .filter(Boolean)
                        .join(" · ")}
                    </p>
                  </div>
                  <TraditionPills tradition={p.tradition} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
