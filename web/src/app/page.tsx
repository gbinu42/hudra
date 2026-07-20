import Link from "next/link";
import { CalendarClient } from "@/components/CalendarClient";
import { TodaysPrayers } from "@/components/TodaysPrayers";
import { getCatalog } from "@/lib/data";
import { isPlaceholderSyriac } from "@/lib/syriac-text";
import { HudraMark } from "@/components/HudraMark";

export default function HomePage() {
  const catalog = getCatalog();
  const seasonLabels: Record<string, string> = {};
  for (const s of catalog.seasons) {
    if (!isPlaceholderSyriac(s.syriac)) {
      seasonLabels[s.id] = s.syriac;
    }
  }

  return (
    <main>
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_70%_20%,rgba(26,95,106,0.16),transparent_55%)]" />
        <div className="mx-auto grid max-w-6xl items-center gap-12 px-5 py-16 sm:px-8 sm:py-24 lg:grid-cols-[1fr_auto] lg:gap-16">
          <div className="fade-up order-2 lg:order-1">
            <p
              className="text-xs tracking-[0.28em] text-gold uppercase"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              East Syriac Breviary
            </p>
            <p
              className="mt-5 text-2xl text-ink sm:text-3xl"
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              The prayers of the Hudra
            </p>
            <p className="fade-up-delay mt-5 max-w-xl text-base leading-relaxed text-ink-soft">
              A complete liturgical cycle in East Syriac — Hudra, Kashkol and
              Gazza of the Assyrian and Chaldean churches.
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
                Seasons
              </Link>
              <Link
                href="/calendar"
                className="rounded-sm border border-line bg-paper/70 px-5 py-2.5 text-sm tracking-wide text-ink transition hover:border-teal/40"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                Liturgical calendar
              </Link>
              <Link
                href="/psalms"
                className="rounded-sm border border-line bg-paper/70 px-5 py-2.5 text-sm tracking-wide text-ink transition hover:border-teal/40"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                Psalms
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

          <div className="fade-up-delay order-1 flex flex-col items-center text-teal-deep lg:order-2 lg:justify-self-center">
            <HudraMark className="h-36 w-auto sm:h-48 lg:h-56" />
            <h1
              className="syr drift mt-4 text-center text-5xl !leading-none sm:mt-5 sm:text-6xl"
              dir="rtl"
            >
              ܚܘܼܕܪܵܐ
            </h1>
          </div>
        </div>
      </section>

      <TodaysPrayers prayers={catalog.prayers} seasonLabels={seasonLabels} />

      <section className="border-t border-line/80 bg-paper/40">
        <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8">
          <CalendarClient
            prayers={catalog.prayers}
            seasonLabels={seasonLabels}
            embedded
          />
        </div>
      </section>
    </main>
  );
}
