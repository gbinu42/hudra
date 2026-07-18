import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { TraditionPills } from "@/components/SeasonCard";
import {
  getCatalog,
  getPrayersForSeason,
  getSeason,
  organizeSeason,
} from "@/lib/data";

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

export default async function SeasonPage({ params }: Props) {
  const { id } = await params;
  const season = getSeason(id);
  if (!season) notFound();

  const prayers = getPrayersForSeason(id);
  const weeks = organizeSeason(prayers);

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
        {season.syriac && season.syriac !== "ܠܐ ܝܕܝܥܐ" ? (
          <h1 className="syr syr-block mt-3 text-5xl text-teal-deep sm:text-6xl">
            {season.syriac}
          </h1>
        ) : (
          <h1
            className="mt-3 text-5xl text-teal-deep sm:text-6xl"
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

      <div className="mt-12 space-y-10">
        {weeks.map((week) => (
          <section key={week.week} className="border border-line bg-paper/55">
            <div className="border-b border-line px-5 py-4 sm:px-6">
              <p
                className="text-xs tracking-wide text-ink-soft uppercase"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                Week
              </p>
              <h2 className="syr syr-meta mt-1 text-3xl text-ink">
                {week.week === "—" ? "—" : week.week}
              </h2>
            </div>

            <div className="divide-y divide-line">
              {week.days.map((day) => (
                <div key={day.day} className="px-5 py-5 sm:px-6">
                  <div className="mb-3 flex flex-wrap items-baseline gap-x-3 gap-y-0.5">
                    <h3 className="syr syr-meta text-2xl text-teal-deep">
                      {day.day === "—" ? "—" : day.day}
                    </h3>
                    {day.dayEn && (
                      <span className="text-sm text-ink-soft">{day.dayEn}</span>
                    )}
                  </div>
                  <ul className="space-y-2">
                    {day.hours.map((p) => (
                      <li key={p.id}>
                        <Link
                          href={`/prayer/${p.id}`}
                          className="group flex flex-col gap-2 rounded-sm border border-transparent px-3 py-3 transition hover:border-line hover:bg-paper-deep/40 sm:flex-row sm:items-center sm:justify-between"
                        >
                          <div className="min-w-0">
                            <p className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5 text-xs tracking-wide text-gold">
                              <span>{p.hourEn || p.hour || "Hour"}</span>
                              {p.hour && p.hourEn && p.hour !== p.hourEn ? (
                                <span className="syr syr-meta text-xl text-ink-soft">
                                  {p.hour}
                                </span>
                              ) : null}
                            </p>
                            <p className="syr syr-meta mt-1 truncate text-2xl text-ink group-hover:text-teal-deep">
                              {p.name}
                            </p>
                          </div>
                          <TraditionPills tradition={p.tradition} />
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </main>
  );
}
