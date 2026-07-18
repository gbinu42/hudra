import Link from "next/link";
import { TodaysPrayers } from "@/components/TodaysPrayers";
import { getCatalog, getSeasons } from "@/lib/data";

export default function HomePage() {
  const catalog = getCatalog();
  const cycle = getSeasons("cycle").slice(0, 6);
  const seasonLabels: Record<string, string> = {};
  for (const s of catalog.seasons) {
    if (s.syriac && s.syriac !== "ܠܐ ܝܕܝܥܐ") {
      seasonLabels[s.id] = s.syriac;
    }
  }

  return (
    <main>
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_70%_20%,rgba(26,95,106,0.16),transparent_55%)]" />
        <div className="mx-auto grid max-w-6xl gap-10 px-5 py-16 sm:px-8 sm:py-24 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
          <div className="fade-up">
            <p
              className="text-xs tracking-[0.28em] text-gold uppercase"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              East Syriac Breviary
            </p>
            <h1 className="syr syr-block drift mt-5 text-6xl leading-none text-teal-deep sm:text-7xl md:text-8xl">
              ܚܘܼܕܪܵܐ
            </h1>
            <p
              className="mt-4 text-2xl text-ink sm:text-3xl"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              The prayers of the Hudra
            </p>
            <p className="fade-up-delay mt-5 max-w-xl text-base leading-relaxed text-ink-soft">
              A complete liturgical cycle in Syriac — seasons, weeks, days, and
              hours of the Church of the East, gathered for quiet reading.
            </p>
            <div className="fade-up-delay-2 mt-8 flex flex-wrap gap-3">
              <Link
                href="/browse"
                className="rounded-sm bg-teal-deep px-5 py-2.5 text-sm tracking-wide text-white transition hover:bg-teal hover:text-white"
                style={{
                  fontFamily: "var(--font-display), Georgia, serif",
                  color: "#fff",
                }}
              >
                Enter the seasons
              </Link>
              <Link
                href="/calendar"
                className="rounded-sm border border-line bg-paper/70 px-5 py-2.5 text-sm tracking-wide text-ink transition hover:border-teal/40"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                Liturgical calendar
              </Link>
              <Link
                href="/search"
                className="rounded-sm border border-line bg-paper/70 px-5 py-2.5 text-sm tracking-wide text-ink transition hover:border-teal/40"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                Search
              </Link>
            </div>
          </div>

          <aside className="fade-up-delay border border-line bg-paper/55 p-6 backdrop-blur-sm sm:p-8">
            <p
              className="text-xs tracking-[0.2em] text-gold uppercase"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              Corpus
            </p>
            <dl className="mt-5 grid grid-cols-2 gap-5">
              {[
                ["Prayers", catalog.counts.prayers.toLocaleString()],
                ["Seasons", String(catalog.counts.seasons)],
                ["Assyrian edition", catalog.counts.syriac.toLocaleString()],
                ["Chaldean edition", catalog.counts.chaldean.toLocaleString()],
              ].map(([label, value]) => (
                <div key={label}>
                  <dt className="text-xs text-ink-soft">{label}</dt>
                  <dd
                    className="mt-1 text-2xl text-ink"
                    style={{
                      fontFamily: "var(--font-display), Georgia, serif",
                    }}
                  >
                    {value}
                  </dd>
                </div>
              ))}
            </dl>
          </aside>
        </div>
      </section>

      <TodaysPrayers
        prayers={catalog.prayers}
        seasonLabels={seasonLabels}
      />

      <section className="border-t border-line/80 bg-paper/40">
        <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8">
          <div className="flex items-end justify-between gap-4">
            <div>
              <h2
                className="text-2xl text-ink sm:text-3xl"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                Begin the cycle
              </h2>
              <p className="mt-2 text-sm text-ink-soft">
                From Annunciation through the Dedication of the Church.
              </p>
            </div>
            <Link
              href="/browse"
              className="hidden text-sm text-teal underline-offset-4 hover:underline sm:inline"
            >
              View all seasons
            </Link>
          </div>
          <ol className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {cycle.map((s, i) => (
              <li key={s.id}>
                <Link
                  href={`/season/${s.id}`}
                  className="flex items-center gap-4 border border-line bg-paper/70 px-4 py-4 transition hover:border-teal/35 hover:bg-paper"
                >
                  <span
                    className="w-8 text-sm tabular-nums text-gold"
                    style={{
                      fontFamily: "var(--font-display), Georgia, serif",
                    }}
                  >
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <span>
                    <span className="block text-xs tracking-wide text-ink-soft">
                      {s.english}
                    </span>
                    <span className="syr syr-meta mt-1 block text-2xl text-ink">
                      {s.syriac}
                    </span>
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </section>
    </main>
  );
}
