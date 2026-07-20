"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { DayOfficeList } from "@/components/DayOfficeList";
import {
  buildLiturgicalYear,
  daysInMonth,
  getLiturgicalDay,
  isLiturgicalEvening,
  SEASON_META,
  toLiturgicalDate,
  type LitSeasonId,
  toISO,
} from "@/lib/liturgical-calendar";
import {
  groupPrayersByHour,
  matchPrayersForDay,
} from "@/lib/prayer-day";
import type { PrayerSummary } from "@/lib/types";

const SEASON_COLORS: Record<LitSeasonId, string> = {
  subara: "bg-[#c4b48a]/35",
  "after-nativity": "bg-[#8a7340]/20",
  denha: "bg-[#1a5f6a]/18",
  "great-fast": "bg-[#5c4135]/22",
  easter: "bg-[#1a5f6a]/28",
  apostles: "bg-[#0f3f47]/18",
  summer: "bg-[#8a7340]/16",
  "elijah-cross": "bg-[#c4b48a]/40",
  moses: "bg-[#3a4a40]/15",
  dedication: "bg-[#1a5f6a]/12",
};

const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

function formatCivilDate(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export function CalendarClient({
  prayers,
  seasonLabels,
  embedded = false,
}: {
  prayers: PrayerSummary[];
  /** Syriac season titles from the prayer corpus, keyed by season id. */
  seasonLabels: Record<string, string>;
  /** Use when nested on another page (avoids a second page-level h1). */
  embedded?: boolean;
}) {
  const today = useMemo(() => new Date(), []);
  const litTodayDate = useMemo(() => toLiturgicalDate(today), [today]);
  const litTodayIso = useMemo(() => toISO(litTodayDate), [litTodayDate]);
  const fromEvening = useMemo(() => isLiturgicalEvening(today), [today]);
  const [year, setYear] = useState(litTodayDate.getFullYear());
  const [month, setMonth] = useState(litTodayDate.getMonth());
  const [selected, setSelected] = useState(litTodayIso);

  const lit = useMemo(() => buildLiturgicalYear(year), [year]);
  const days = useMemo(() => daysInMonth(year, month), [year, month]);
  const todayInfo = useMemo(() => getLiturgicalDay(today), [today]);
  const selectedDay = useMemo(() => {
    const d = days.find((x) => x.date === selected);
    if (d) return d;
    const [y, m, dd] = selected.split("-").map(Number);
    return getLiturgicalDay(new Date(y, m - 1, dd));
  }, [days, selected]);

  const selectedOffice = useMemo(
    () => matchPrayersForDay(prayers, selectedDay),
    [prayers, selectedDay],
  );
  const selectedHours = useMemo(
    () => groupPrayersByHour(selectedOffice.prayers),
    [selectedOffice.prayers],
  );

  const selectedSeasonSyr =
    selectedDay.seasonSyr || seasonLabels[selectedDay.seasonId] || "";
  const todaySeasonSyr =
    todayInfo.seasonSyr || seasonLabels[todayInfo.seasonId] || "";

  const firstWeekday = new Date(year, month, 1).getDay(); // Sun=0
  const lead = firstWeekday;

  const monthFeasts = lit.feasts.filter((f) => {
    const [, m] = f.date.split("-").map(Number);
    return m === month + 1;
  });

  function shiftMonth(delta: number) {
    const d = new Date(year, month + delta, 1);
    setYear(d.getFullYear());
    setMonth(d.getMonth());
  }

  function selectDay(iso: string) {
    setSelected(iso);
    const [y, m] = iso.split("-").map(Number);
    setYear(y);
    setMonth(m - 1);
    if (!embedded) {
      requestAnimationFrame(() => {
        document
          .getElementById("day-offices")
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  }

  return (
    <div className="space-y-12">
      <div className="grid gap-10 lg:grid-cols-[1fr_280px]">
        <div>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p
                className="text-xs tracking-[0.22em] text-gold uppercase"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                Liturgical calendar
              </p>
              {embedded ? (
                <h2
                  className="mt-2 text-3xl text-teal-deep sm:text-4xl"
                  style={{ fontFamily: "var(--font-display), Georgia, serif" }}
                >
                  {MONTHS[month]} {year}
                </h2>
              ) : (
                <h1
                  className="mt-2 text-3xl text-teal-deep sm:text-4xl"
                  style={{ fontFamily: "var(--font-display), Georgia, serif" }}
                >
                  {MONTHS[month]} {year}
                </h1>
              )}
            </div>
            <div className="flex items-center gap-2">
              {(year !== litTodayDate.getFullYear() ||
                month !== litTodayDate.getMonth()) && (
                <button
                  type="button"
                  onClick={() => selectDay(litTodayIso)}
                  className="rounded-sm border border-line bg-paper/80 px-3 py-1.5 text-sm text-ink-soft hover:bg-paper-deep/70"
                >
                  Today
                </button>
              )}
              <button
                type="button"
                onClick={() => shiftMonth(-1)}
                className="rounded-sm border border-line bg-paper/80 px-3 py-1.5 text-sm text-ink-soft hover:bg-paper-deep/70"
                aria-label="Previous month"
              >
                ←
              </button>
              <span
                className="min-w-[7.5rem] px-1 text-center text-sm text-ink"
                aria-live="polite"
              >
                {MONTHS[month]} {year}
              </span>
              <button
                type="button"
                onClick={() => shiftMonth(1)}
                className="rounded-sm border border-line bg-paper/80 px-3 py-1.5 text-sm text-ink-soft hover:bg-paper-deep/70"
                aria-label="Next month"
              >
                →
              </button>
            </div>
          </div>

          <div className="mt-6 overflow-hidden rounded-sm border border-line bg-paper/60">
            <div className="grid grid-cols-7 border-b border-line text-center text-[11px] tracking-wide text-ink-soft uppercase">
              {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
                <div key={d} className="px-1 py-2">
                  {d}
                </div>
              ))}
            </div>
            <div className="grid grid-cols-7">
              {Array.from({ length: lead }).map((_, i) => (
                <div
                  key={`e-${i}`}
                  className="min-h-[4.5rem] border-b border-r border-line/60 bg-paper-deep/20"
                />
              ))}
              {days.map((day) => {
                const dom = Number(day.date.slice(-2));
                const isToday = day.date === litTodayIso;
                const isSel = day.date === selected;
                const hasFeast = day.feasts.length > 0;
                return (
                  <button
                    key={day.date}
                    type="button"
                    onClick={() => selectDay(day.date)}
                    className={`min-h-[4.5rem] border-b border-r border-line/60 px-1.5 py-1.5 text-left transition hover:brightness-95 ${SEASON_COLORS[day.seasonId]} ${
                      isSel ? "ring-2 ring-inset ring-teal" : ""
                    }`}
                  >
                    <span
                      className={`inline-flex h-6 w-6 items-center justify-center rounded-sm text-sm tabular-nums ${
                        isToday ? "bg-teal-deep text-paper" : "text-ink"
                      }`}
                    >
                      {dom}
                    </span>
                    {hasFeast && (
                      <span className="mt-1 block truncate text-[10px] leading-tight text-teal-deep">
                        {day.feasts[0].en}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {(Object.keys(SEASON_META) as LitSeasonId[]).map((id) => (
              <span
                key={id}
                className={`inline-flex items-center gap-1.5 rounded-sm border border-line px-2 py-1 text-[11px] text-ink-soft ${SEASON_COLORS[id]}`}
              >
                {SEASON_META[id].en}
              </span>
            ))}
          </div>
        </div>

        <aside className="space-y-6">
          <section className="rounded-sm border border-line bg-paper/70 p-5">
            <p className="text-xs tracking-wide text-ink-soft uppercase">
              Today
            </p>
            <p className="mt-1 text-sm text-ink-soft">
              {todayInfo.date}
              {fromEvening ? " · from evening" : ""}
            </p>
            {todaySeasonSyr ? (
              <p className="syr syr-meta mt-3 text-2xl text-teal-deep">
                {todaySeasonSyr}
              </p>
            ) : null}
            <p className="mt-1 text-base text-ink">{todayInfo.seasonEn}</p>
            <p className="mt-2 text-sm text-ink-soft">
              Week {todayInfo.week} · {todayInfo.weekdayEn}
              <span className="syr syr-inline ml-2 text-xl">
                {todayInfo.weekdaySyr}
              </span>
            </p>
            {!embedded ? (
              <button
                type="button"
                onClick={() => selectDay(litTodayIso)}
                className="mt-4 text-sm text-teal hover:underline"
              >
                Show today&apos;s offices →
              </button>
            ) : (
              <Link
                href="/calendar"
                className="mt-4 inline-block text-sm text-teal hover:underline"
              >
                Open full calendar →
              </Link>
            )}
          </section>

          <section className="rounded-sm border border-line bg-paper/70 p-5">
            <p className="text-xs tracking-wide text-ink-soft uppercase">
              {MONTHS[month]} feasts
            </p>
            <ul className="mt-3 max-h-72 space-y-2 overflow-y-auto text-sm">
              {monthFeasts.length === 0 && (
                <li className="text-ink-soft">No major feasts listed.</li>
              )}
              {monthFeasts.map((f) => (
                <li key={f.date + f.en}>
                  <button
                    type="button"
                    onClick={() => selectDay(f.date)}
                    className="text-left hover:text-teal"
                  >
                    <span className="tabular-nums text-ink-soft">
                      {f.date.slice(8)}
                    </span>{" "}
                    <span className="text-ink">{f.en}</span>
                    {f.movable && (
                      <span className="ml-1 text-[10px] text-gold">movable</span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </section>

          <p className="text-xs leading-relaxed text-ink-soft/80">
            {embedded
              ? "The liturgical day begins at evening (6 PM local time). Calendar after Isaac, Ph., 2007, "
              : "Click a day to open its offices. The liturgical day begins at evening (6 PM local time). Calendar after Isaac, Ph., 2007, "}
            <em>The Perpetual Calendar</em>.
          </p>
        </aside>
      </div>

      {!embedded ? (
      <section
        id="day-offices"
        className="scroll-mt-8 border-t border-line/80 pt-10"
      >
        <div className="fade-up grid gap-10 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)] lg:items-start lg:gap-14">
          <div>
            <p
              className="text-xs tracking-[0.22em] text-gold uppercase"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              {selected === litTodayIso ? "Today" : "Selected day"}
            </p>
            <p className="syr syr-block mt-3 text-4xl leading-none text-teal-deep sm:text-5xl">
              {selectedDay.weekdaySyr}
            </p>
            <p
              className="mt-2 text-2xl text-ink"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              {selectedDay.weekdayEn}
            </p>
            <p className="mt-1 text-sm text-ink-soft">
              {formatCivilDate(selectedDay.date)}
            </p>

            <div className="mt-6 border-t border-line/80 pt-5">
            {selectedSeasonSyr ? (
              <p className="syr syr-meta text-2xl text-ink sm:text-3xl">
                {selectedSeasonSyr}
              </p>
            ) : null}
            <p className="mt-2 text-sm text-ink-soft">
              {selectedDay.seasonEn}
              <span className="mx-2 opacity-40">·</span>
              Week {selectedDay.week}
            </p>
            {selectedDay.feasts.length > 0 && (
              <ul className="mt-4 space-y-1.5">
                {selectedDay.feasts.map((f) => (
                  <li key={f.en} className="text-sm text-gold">
                    {f.en}
                  </li>
                ))}
              </ul>
            )}
            </div>

            <Link
              href={`/season/${selectedDay.seasonId}`}
              className="mt-6 inline-block text-sm text-teal underline-offset-4 hover:underline"
            >
              Full season →
            </Link>
          </div>

          <div className="min-w-0">
            <div className="mb-5 flex items-baseline justify-between gap-3">
              <h2
                className="text-xl text-ink sm:text-2xl"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                Offices
              </h2>
              {selectedHours.length > 0 && (
                <p className="text-xs tracking-wide text-ink-soft tabular-nums">
                  {selectedHours.length}{" "}
                  {selectedHours.length === 1 ? "hour" : "hours"} ·{" "}
                  {selectedOffice.prayers.length} prayers
                </p>
              )}
            </div>
            <DayOfficeList
              prayers={selectedOffice.prayers}
              seasonId={selectedDay.seasonId}
              exact={selectedOffice.exact}
            />
          </div>
        </div>
      </section>
      ) : null}
    </div>
  );
}
