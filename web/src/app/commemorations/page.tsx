import type { Metadata } from "next";
import { SeasonCard } from "@/components/SeasonCard";
import { getSeasons } from "@/lib/data";

export const metadata: Metadata = {
  title: "Commemorations — ܕܘܼܟ݂ܪ̈ܵܢܹܐ",
};

export default function CommemorationsPage() {
  const items = getSeasons("commemoration");

  return (
    <main className="mx-auto max-w-6xl px-5 py-12 sm:px-8 sm:py-16">
      <header className="max-w-2xl">
        <h1
          className="mt-1 flex flex-wrap items-baseline gap-x-3 gap-y-1 text-4xl text-ink sm:text-5xl"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          <span>Commemorations</span>
          <span className="text-ink-soft/50" aria-hidden>
            —
          </span>
          <span className="syr syr-meta text-5xl text-teal-deep sm:text-6xl">
            ܕܘܼܟ݂ܪ̈ܵܢܹܐ
          </span>
        </h1>
        <p className="mt-4 text-base leading-relaxed text-ink-soft">
          Memorials of saints, apostles, and feasts of Our Lady that stand
          alongside the main seasonal cycle.
        </p>
      </header>

      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        {items.map((s) => (
          <SeasonCard key={s.id} season={s} />
        ))}
      </div>
    </main>
  );
}
