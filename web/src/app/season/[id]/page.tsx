import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  SeasonOutline,
  type SeasonWeekView,
} from "@/components/SeasonOutline";
import {
  ExclusiveTraditionPill,
} from "@/components/SeasonCard";
import {
  getCatalog,
  getExclusiveSeasonTraditions,
  getPrayersForSeason,
  getSeason,
  isCycleFeastSeason,
  organizeSeason,
} from "@/lib/data";
import { seasonWhen } from "@/lib/feast-when";
import { isPlaceholderSyriac } from "@/lib/syriac-text";

type Props = { params: Promise<{ id: string }> };

export async function generateStaticParams() {
  return getCatalog().seasons.map((s) => ({ id: s.id }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const season = getSeason(id);
  if (!season) return { title: "Season" };
  return { title: `${season.english} · ${season.syriac}` };
}

function toWeekViews(
  weeks: ReturnType<typeof organizeSeason>,
): SeasonWeekView[] {
  return weeks.map((week) => ({
    week: week.week,
    days: week.days.map((day) => ({
      day: day.day,
      dayEn: day.dayEn,
      dayOrder: day.dayOrder,
      prayers: day.hours,
    })),
  }));
}

export default async function SeasonPage({ params }: Props) {
  const { id } = await params;
  const season = getSeason(id);
  if (!season) notFound();

  const prayers = getPrayersForSeason(id);
  const weeks = toWeekViews(organizeSeason(prayers));
  const seasonSyr = !isPlaceholderSyriac(season.syriac) ? season.syriac : "";
  const when = seasonWhen(season.id);
  const exclusiveTradition = getExclusiveSeasonTraditions().get(season.id);

  return (
    <main className="mx-auto max-w-6xl px-5 py-12 sm:px-8 sm:py-16">
      <nav className="text-sm text-ink-soft">
        <Link
          href={
            season.group === "cycle" && !isCycleFeastSeason(season.id)
              ? "/browse"
              : "/commemorations"
          }
          className="hover:text-teal"
        >
          {season.group === "cycle" && !isCycleFeastSeason(season.id)
            ? "Seasons"
            : "Feasts"}
        </Link>
        <span className="mx-2 opacity-50">/</span>
        <span>{season.english}</span>
      </nav>

      <header className="mt-6 max-w-3xl fade-up">
        <p
          className="text-xs tracking-[0.22em] text-gold uppercase"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          {season.english}
        </p>
        {seasonSyr ? (
          <h1 className="syr syr-meta mt-3 text-4xl text-teal-deep sm:text-5xl">
            {seasonSyr}
          </h1>
        ) : (
          <h1
            className="mt-3 text-4xl text-teal-deep sm:text-5xl"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            {season.english}
          </h1>
        )}
        {when || exclusiveTradition ? (
          <div className="mt-4 flex flex-wrap items-center gap-2">
            {when ? (
              <p className="text-sm tracking-wide text-gold">{when}</p>
            ) : null}
            {exclusiveTradition ? (
              <ExclusiveTraditionPill tradition={exclusiveTradition} />
            ) : null}
          </div>
        ) : null}
        <p
          className={`text-sm text-ink-soft/80 ${when || exclusiveTradition ? "mt-2" : "mt-4"}`}
        >
          {season.count.toLocaleString()} prayers · {weeks.length} week
          {weeks.length === 1 ? "" : "s"}
        </p>
      </header>

      <SeasonOutline weeks={weeks} />
    </main>
  );
}
