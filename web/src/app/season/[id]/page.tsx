import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  SeasonOutline,
  type SeasonWeekView,
} from "@/components/SeasonOutline";
import {
  getCatalog,
  getPrayersForSeason,
  getSeason,
  organizeSeason,
} from "@/lib/data";
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

  return (
    <main className="mx-auto max-w-6xl px-5 py-12 sm:px-8 sm:py-16">
      <nav className="text-sm text-ink-soft">
        <Link href="/browse" className="hover:text-teal">
          Seasons
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
        <p className="mt-4 text-sm text-ink-soft/80">
          {season.count.toLocaleString()} prayers · {weeks.length} week
          {weeks.length === 1 ? "" : "s"}
        </p>
      </header>

      <SeasonOutline weeks={weeks} />
    </main>
  );
}
