"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { DayOfficeList } from "@/components/DayOfficeList";
import {
  getLiturgicalDay,
  isLiturgicalEvening,
  liturgicalTodayIso,
  toISO,
} from "@/lib/liturgical-calendar";
import {
  groupPrayersByHour,
  matchPrayersForDay,
} from "@/lib/prayer-day";
import type { PrayerSummary } from "@/lib/types";

function formatCivilDate(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return date.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function shiftIso(iso: string, delta: number): string {
  const [y, m, d] = iso.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  date.setDate(date.getDate() + delta);
  return toISO(date);
}

export function TodaysPrayers({
  prayers,
  seasonLabels,
}: {
  prayers: PrayerSummary[];
  seasonLabels: Record<string, string>;
}) {
  const [todayIso, setTodayIso] = useState<string | null>(null);
  const [fromEvening, setFromEvening] = useState(false);
  const [iso, setIso] = useState<string | null>(null);

  useEffect(() => {
    const now = new Date();
    const t = liturgicalTodayIso(now);
    setTodayIso(t);
    setIso(t);
    setFromEvening(isLiturgicalEvening(now));
  }, []);

  const lit = useMemo(() => {
    if (!iso) return null;
    const [y, m, d] = iso.split("-").map(Number);
    return getLiturgicalDay(new Date(y, m - 1, d));
  }, [iso]);

  const office = useMemo(() => {
    if (!lit) return null;
    return matchPrayersForDay(prayers, lit);
  }, [prayers, lit]);

  if (!iso || !todayIso || !lit || !office) {
    return (
      <section className="border-t border-line/80">
        <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8">
          <p className="text-sm text-ink-soft">Loading today&apos;s offices…</p>
        </div>
      </section>
    );
  }

  const isToday = iso === todayIso;
  const hours = groupPrayersByHour(office.prayers);
  const seasonSyr = seasonLabels[lit.seasonId] || "";

  return (
    <section className="relative overflow-hidden border-t border-line/80">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_0%_0%,rgba(26,95,106,0.12),transparent_50%),radial-gradient(ellipse_at_100%_80%,rgba(138,115,64,0.08),transparent_45%)]" />
      <div className="relative mx-auto grid max-w-6xl gap-12 px-5 py-14 sm:px-8 sm:py-16 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] lg:gap-16 lg:items-start">
        <div className="fade-up">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p
              className="text-xs tracking-[0.22em] text-gold uppercase"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              {isToday ? "Today" : "Day"}
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setIso((d) => (d ? shiftIso(d, -1) : d))}
                className="rounded-sm border border-line bg-paper/80 px-3 py-1.5 text-sm text-ink-soft transition hover:border-teal/40 hover:text-ink"
                aria-label="Previous day"
              >
                ←
              </button>
              {!isToday && (
                <button
                  type="button"
                  onClick={() => setIso(todayIso)}
                  className="rounded-sm border border-line bg-paper/80 px-3 py-1.5 text-sm text-ink-soft transition hover:border-teal/40 hover:text-ink"
                >
                  Today
                </button>
              )}
              <button
                type="button"
                onClick={() => setIso((d) => (d ? shiftIso(d, 1) : d))}
                className="rounded-sm border border-line bg-paper/80 px-3 py-1.5 text-sm text-ink-soft transition hover:border-teal/40 hover:text-ink"
                aria-label="Next day"
              >
                →
              </button>
            </div>
          </div>

          <p className="syr syr-block mt-4 text-5xl leading-none text-teal-deep sm:text-6xl">
            {lit.weekdaySyr}
          </p>
          <p
            className="mt-3 text-2xl text-ink sm:text-3xl"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            {lit.weekdayEn}
          </p>
          <p className="mt-1 text-sm text-ink-soft">{formatCivilDate(lit.date)}</p>
          {isToday && fromEvening ? (
            <p className="mt-1 text-xs text-ink-soft/80">
              Liturgical day from evening · 6&nbsp;PM
            </p>
          ) : null}

          <div className="mt-8 border-t border-line/80 pt-6">
            {seasonSyr ? (
              <p className="syr syr-meta text-3xl text-ink">{seasonSyr}</p>
            ) : null}
            <p className="mt-2 text-sm text-ink-soft">
              {lit.seasonEn}
              <span className="mx-2 opacity-40">·</span>
              Week {lit.week}
            </p>
            {lit.feasts.length > 0 && (
              <ul className="mt-4 space-y-1.5">
                {lit.feasts.map((f) => (
                  <li key={f.en} className="text-sm text-gold">
                    {f.en}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="mt-8 flex flex-wrap gap-4 text-sm">
            <Link
              href={`/season/${lit.seasonId}`}
              className="text-teal underline-offset-4 hover:underline"
            >
              Full season
            </Link>
            <Link
              href="/calendar"
              className="text-ink-soft underline-offset-4 hover:underline"
            >
              Calendar
            </Link>
          </div>
        </div>

        <div className="fade-up-delay min-w-0">
          <div className="mb-6 flex items-baseline justify-between gap-3">
            <h2
              className="text-xl text-ink sm:text-2xl"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              The day&apos;s offices
            </h2>
            {hours.length > 0 && (
              <p className="text-xs tracking-wide text-ink-soft tabular-nums">
                {hours.length} {hours.length === 1 ? "hour" : "hours"}
              </p>
            )}
          </div>
          <DayOfficeList
            prayers={office.prayers}
            seasonId={lit.seasonId}
            exact={office.exact}
          />
        </div>
      </div>
    </section>
  );
}
