"use client";

import Link from "next/link";
import { useState, type ReactNode } from "react";
import { TraditionEditionLinks, TraditionPills } from "@/components/SeasonCard";
import {
  groupOfficeEditions,
  groupPrayersByHour,
  type HourGroup,
  type OfficeGroup,
} from "@/lib/prayer-day";
import type { PrayerSummary } from "@/lib/types";

export type SeasonDayView = {
  day: string;
  dayEn: string;
  dayOrder: number;
  prayers: PrayerSummary[];
};

export type SeasonWeekView = {
  week: string;
  days: SeasonDayView[];
};

export function SeasonOutline({ weeks }: { weeks: SeasonWeekView[] }) {
  let dayIndex = 0;

  return (
    <div className="mt-12 space-y-10">
      {weeks.map((week) => (
        <section key={week.week} className="min-w-0">
          <header className="mb-4 border-b border-line pb-3">
            <p
              className="text-xs tracking-[0.2em] text-gold uppercase"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              Week
            </p>
            <h2 className="syr syr-meta mt-1 text-3xl text-ink sm:text-4xl">
              {week.week === "—" ? "—" : week.week}
            </h2>
          </header>

          <div className="space-y-2">
            {week.days.map((day) => {
              const openFirst = dayIndex === 0;
              dayIndex += 1;
              const hours = groupPrayersByHour(day.prayers);
              const officeCount = hours.reduce(
                (n, h) => n + groupOfficeEditions(h.prayers).length,
                0,
              );

              return (
                <DayAccordion
                  key={`${week.week}|${day.day}|${day.dayEn}`}
                  defaultOpen={openFirst}
                  count={officeCount}
                  summary={
                    <>
                      <span className="syr syr-meta text-2xl leading-none text-teal-deep sm:text-3xl">
                        {day.day === "—" ? "—" : day.day}
                      </span>
                      {day.dayEn ? (
                        <span
                          className="text-sm text-ink-soft sm:text-base"
                          style={{
                            fontFamily: "var(--font-display), Georgia, serif",
                          }}
                        >
                          {day.dayEn}
                        </span>
                      ) : null}
                    </>
                  }
                >
                  {hours.length === 0 ? (
                    <p className="text-sm text-ink-soft">No offices.</p>
                  ) : (
                    <ol className="space-y-6">
                      {hours.map((hour) => (
                        <HourBlock key={hour.key} group={hour} />
                      ))}
                    </ol>
                  )}
                </DayAccordion>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}

function DayAccordion({
  defaultOpen,
  summary,
  count,
  children,
}: {
  defaultOpen: boolean;
  summary: ReactNode;
  count: number;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <details
      className="group border border-line bg-paper/55 open:bg-paper/80"
      open={open}
      onToggle={(e) => {
        setOpen((e.target as HTMLDetailsElement).open);
      }}
    >
      <summary className="flex cursor-pointer list-none items-center gap-3 px-4 py-3.5 sm:px-5 [&::-webkit-details-marker]:hidden">
        <span
          className="flex h-6 w-6 shrink-0 items-center justify-center rounded-sm border border-line text-xs text-ink-soft transition group-open:border-teal/40 group-open:text-teal-deep"
          aria-hidden
        >
          <span className="group-open:hidden">+</span>
          <span className="hidden group-open:inline">−</span>
        </span>
        <span className="flex min-w-0 flex-1 flex-wrap items-baseline gap-x-3 gap-y-1">
          {summary}
        </span>
        <span className="shrink-0 text-xs tabular-nums text-ink-soft">
          {count}
        </span>
      </summary>
      <div className="border-t border-line px-4 py-4 sm:px-5 sm:py-5">
        {children}
      </div>
    </details>
  );
}

function HourBlock({ group }: { group: HourGroup }) {
  const offices = groupOfficeEditions(group.prayers);

  return (
    <li className="list-none">
      <div className="mb-2 flex flex-wrap items-baseline gap-x-2.5 gap-y-0.5">
        <p
          className="text-sm tracking-wide text-gold"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          {group.hourEn || group.hour || "Hour"}
        </p>
        {group.hour && group.hourEn && group.hour !== group.hourEn ? (
          <p className="syr syr-meta text-xl text-ink-soft sm:text-2xl">
            {group.hour}
          </p>
        ) : null}
      </div>
      <ul className="space-y-1.5">
        {offices.map((office) => (
          <OfficeRow key={office.key} office={office} />
        ))}
      </ul>
    </li>
  );
}

function OfficeRow({ office }: { office: OfficeGroup }) {
  const single = office.editions.length === 1;

  if (single) {
    const ed = office.editions[0];
    return (
      <li>
        <Link
          href={`/prayer/${ed.id}`}
          className="group flex flex-col gap-2 border border-transparent px-2 py-2.5 transition hover:border-line hover:bg-paper-deep/40 sm:flex-row sm:items-center sm:justify-between"
        >
          <p className="syr syr-meta min-w-0 flex-1 text-xl leading-snug text-ink transition group-hover:text-teal-deep sm:text-2xl">
            {office.name}
          </p>
          <TraditionPills tradition={ed.tradition} />
        </Link>
      </li>
    );
  }

  return (
    <li className="flex flex-col gap-2 border border-transparent px-2 py-2.5 sm:flex-row sm:items-center sm:justify-between">
      <p className="syr syr-meta min-w-0 flex-1 text-xl leading-snug text-ink sm:text-2xl">
        {office.name}
      </p>
      <TraditionEditionLinks editions={office.editions} />
    </li>
  );
}
