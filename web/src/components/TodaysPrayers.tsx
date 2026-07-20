"use client";

import Link from "next/link";
import { useMemo } from "react";
import { DayOfficeList } from "@/components/DayOfficeList";
import { getLiturgicalDay, toISO } from "@/lib/liturgical-calendar";
import {
  feastSeasonIdForTitle,
  feastSeasonIdsForDay,
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

function formatNavLabel(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return date.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
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
  iso,
  todayIso,
  fromEvening = false,
  onIsoChange,
}: {
  prayers: PrayerSummary[];
  seasonLabels: Record<string, string>;
  /** Selected liturgical day (YYYY-MM-DD). */
  iso: string;
  todayIso: string;
  fromEvening?: boolean;
  onIsoChange: (iso: string) => void;
}) {
  const lit = useMemo(() => {
    const [y, m, d] = iso.split("-").map(Number);
    return getLiturgicalDay(new Date(y, m - 1, d));
  }, [iso]);

  const office = useMemo(
    () => matchPrayersForDay(prayers, lit),
    [prayers, lit],
  );

  const isToday = iso === todayIso;
  const hours = groupPrayersByHour(office.prayers);
  const feastSeasonIds = feastSeasonIdsForDay(lit);
  const primarySeasonId = feastSeasonIds[0] || lit.seasonId;
  const seasonSyr = lit.seasonSyr || seasonLabels[lit.seasonId] || "";

  return (
    <section
      id="day-offices"
      className="relative scroll-mt-8 overflow-hidden border-t border-line/80"
    >
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
              {!isToday && (
                <button
                  type="button"
                  onClick={() => onIsoChange(todayIso)}
                  className="rounded-sm border border-line bg-paper/80 px-3 py-1.5 text-sm text-ink-soft transition hover:border-teal/40 hover:text-ink"
                >
                  Today
                </button>
              )}
              <button
                type="button"
                onClick={() => onIsoChange(shiftIso(iso, -1))}
                className="rounded-sm border border-line bg-paper/80 px-3 py-1.5 text-sm text-ink-soft transition hover:border-teal/40 hover:text-ink"
                aria-label="Previous day"
              >
                ←
              </button>
              <span
                className="min-w-[4.5rem] px-1 text-center text-sm tabular-nums text-ink"
                aria-live="polite"
              >
                {isToday ? "Today" : formatNavLabel(iso)}
              </span>
              <button
                type="button"
                onClick={() => onIsoChange(shiftIso(iso, 1))}
                className="rounded-sm border border-line bg-paper/80 px-3 py-1.5 text-sm text-ink-soft transition hover:border-teal/40 hover:text-ink"
                aria-label="Next day"
              >
                →
              </button>
            </div>
          </div>

          <div className="mt-4 flex items-baseline justify-between gap-4">
            <p
              className="text-2xl text-ink sm:text-3xl"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              {lit.weekdayEn}
            </p>
            <p
              className="syr max-w-[60%] text-4xl leading-none text-teal-deep sm:text-5xl"
              dir="rtl"
            >
              {lit.weekdaySyr}
            </p>
          </div>
          <p className="mt-1 text-sm text-ink-soft">{formatCivilDate(lit.date)}</p>
          {isToday && fromEvening ? (
            <p className="mt-1 text-xs text-ink-soft/80">
              Liturgical day from evening · 6&nbsp;PM
            </p>
          ) : null}

          <div className="mt-8 border-t border-line/80 pt-6">
            {seasonSyr ? (
              <p className="syr syr-meta text-3xl text-ink sm:text-4xl">
                {seasonSyr}
              </p>
            ) : null}
            <p className="mt-2 text-sm text-ink-soft">
              {lit.seasonEn}
              <span className="mx-2 opacity-40">·</span>
              Week {lit.week}
            </p>
            {lit.feasts.length > 0 && (
              <ul className="mt-4 space-y-1.5">
                {lit.feasts.map((f) => {
                  const feastId = feastSeasonIdForTitle(f.en);
                  const feastSyr =
                    f.syr || (feastId ? seasonLabels[feastId] : "") || "";
                  return (
                    <li key={f.en} className="text-sm text-gold">
                      <span>{f.en}</span>
                      {feastSyr ? (
                        <span className="syr syr-meta mt-0.5 block text-base text-gold/90">
                          {feastSyr}
                        </span>
                      ) : null}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <div className="mt-8 flex flex-wrap gap-4 text-sm">
            <Link
              href={`/season/${primarySeasonId}`}
              className="text-teal underline-offset-4 hover:underline"
            >
              {feastSeasonIds.length > 0 ? "Feast offices" : "Full season"}
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
              {feastSeasonIds.length > 0
                ? "Feast offices"
                : "The day's offices"}
            </h2>
            {hours.length > 0 && (
              <p className="text-xs tracking-wide text-ink-soft tabular-nums">
                {hours.length} {hours.length === 1 ? "hour" : "hours"}
              </p>
            )}
          </div>
          <DayOfficeList
            prayers={office.prayers}
            seasonId={primarySeasonId}
            exact={office.exact}
          />
          {office.seasonPrayers && office.seasonPrayers.length > 0 ? (
            <div className="mt-12 border-t border-line/80 pt-8">
              <div className="mb-6 flex items-baseline justify-between gap-3">
                <h3
                  className="text-lg text-ink sm:text-xl"
                  style={{ fontFamily: "var(--font-display), Georgia, serif" }}
                >
                  Season offices
                </h3>
                <p className="text-xs tracking-wide text-ink-soft">
                  {lit.seasonEn}
                  <span className="mx-1.5 opacity-40">·</span>
                  Week {lit.week}
                </p>
              </div>
              <DayOfficeList
                prayers={office.seasonPrayers}
                seasonId={lit.seasonId}
                exact={office.seasonExact}
              />
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
