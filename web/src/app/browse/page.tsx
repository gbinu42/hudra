import type { Metadata } from "next";
import { SeasonCard } from "@/components/SeasonCard";
import { getSeasons } from "@/lib/data";

export const metadata: Metadata = {
  title: "Seasons",
};

export default function BrowsePage() {
  const cycle = getSeasons("cycle");
  const feasts = getSeasons("feast");
  const baotha = getSeasons("baotha");

  return (
    <main className="mx-auto max-w-6xl px-5 py-12 sm:px-8 sm:py-16">
      <header className="max-w-2xl fade-up">
        <p
          className="text-xs tracking-[0.22em] text-gold uppercase"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Liturgical year
        </p>
        <h1
          className="mt-3 text-4xl text-ink sm:text-5xl"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Seasons of the Hudra
        </h1>
        <p className="mt-4 text-base leading-relaxed text-ink-soft">
          The East Syriac cycle, ordered from Annunciation to the Dedication of
          the Church. Open a season to move through its weeks, days, and hours.
        </p>
      </header>

      <section className="mt-12">
        <h2
          className="text-lg text-ink"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          The cycle
        </h2>
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          {cycle.map((s) => (
            <SeasonCard key={s.id} season={s} />
          ))}
        </div>
      </section>

      {feasts.length > 0 && (
        <section className="mt-14">
          <h2
            className="text-lg text-ink"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            Feasts & Fridays
          </h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            {feasts.map((s) => (
              <SeasonCard key={s.id} season={s} />
            ))}
          </div>
        </section>
      )}

      {baotha.length > 0 && (
        <section className="mt-14">
          <h2
            className="text-lg text-ink"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            Rogation of the Ninevites
          </h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            {baotha.map((s) => (
              <SeasonCard key={s.id} season={s} />
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
