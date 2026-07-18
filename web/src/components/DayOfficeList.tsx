import Link from "next/link";
import { TraditionPills } from "@/components/SeasonCard";
import {
  groupPrayersByHour,
  type HourGroup,
} from "@/lib/prayer-day";
import type { PrayerSummary } from "@/lib/types";

export function DayOfficeList({
  prayers,
  seasonId,
  exact,
  emptyHint,
  compact = false,
}: {
  prayers: PrayerSummary[];
  seasonId: string;
  exact?: boolean;
  emptyHint?: string;
  compact?: boolean;
}) {
  const hours = groupPrayersByHour(prayers);

  if (hours.length === 0) {
    return (
      <p className="text-sm leading-relaxed text-ink-soft">
        {emptyHint ?? "No hour prayers indexed for this day."}{" "}
        <Link href={`/season/${seasonId}`} className="text-teal hover:underline">
          Browse the season
        </Link>
        .
      </p>
    );
  }

  return (
    <div>
      {!exact && (
        <p className="mb-4 text-xs leading-relaxed text-ink-soft/80">
          Closest offices for this day in the season.
        </p>
      )}
      <ol className={compact ? "space-y-5" : "hour-spine relative space-y-0"}>
        {hours.map((g, i) =>
          compact ? (
            <CompactHour key={g.key} group={g} />
          ) : (
            <li
              key={g.key}
              className="hour-step relative grid grid-cols-[1.25rem_1fr] gap-x-4 pb-8 last:pb-0"
              style={{ animationDelay: `${0.08 + i * 0.07}s` }}
            >
              <span className="relative flex justify-center pt-2" aria-hidden>
                <span className="hour-dot absolute top-2.5 z-10 h-2.5 w-2.5 bg-teal-deep" />
              </span>
              <HourBody group={g} />
            </li>
          ),
        )}
      </ol>
    </div>
  );
}

function CompactHour({ group }: { group: HourGroup }) {
  return (
    <li className="list-none">
      <HourBody group={group} />
    </li>
  );
}

function HourBody({ group: g }: { group: HourGroup }) {
  return (
    <div className="min-w-0">
      <p className="flex flex-wrap items-baseline gap-x-2.5 gap-y-0.5">
        <span
          className="text-sm tracking-wide text-gold"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          {g.hourEn || g.hour || "Hour"}
        </span>
        {g.hour && g.hourEn && g.hour !== g.hourEn ? (
          <span className="syr syr-meta text-xl text-ink-soft">{g.hour}</span>
        ) : null}
      </p>
      <ul className="mt-2 space-y-1.5">
        {g.prayers.map((p) => (
          <li key={p.id}>
            <Link
              href={`/prayer/${p.id}`}
              className="group flex flex-col gap-1.5 border border-transparent px-2 py-2 transition hover:border-line hover:bg-paper/70 sm:flex-row sm:items-center sm:justify-between"
            >
              <p className="syr syr-meta truncate text-2xl text-ink transition group-hover:text-teal-deep">
                {p.name}
              </p>
              <TraditionPills tradition={p.tradition} />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
