import type { Metadata } from "next";
import {
  ExclusiveTraditionPill,
  SeasonCard,
} from "@/components/SeasonCard";
import {
  getCycleFeastSeasons,
  getExclusiveSeasonTraditions,
  getSeasons,
} from "@/lib/data";
import type { Season } from "@/lib/types";

export const metadata: Metadata = {
  title: "Feasts & commemorations — ܥܹܐ̈ܕܹܐ ܘܕܘܼܟ݂ܪ̈ܵܢܹܐ",
};

function SeasonGrid({
  items,
  exclusive,
}: {
  items: Season[];
  exclusive: Map<string, "syriac" | "chaldean">;
}) {
  return (
    <div className="mt-5 grid gap-4 sm:grid-cols-2">
      {items.map((s) => (
        <SeasonCard
          key={s.id}
          season={s}
          exclusiveTradition={exclusive.get(s.id)}
        />
      ))}
    </div>
  );
}

export default function CommemorationsPage() {
  const exclusive = getExclusiveSeasonTraditions();
  const lordFeasts = getCycleFeastSeasons();
  const feasts = getSeasons("feast");
  const commemorations = getSeasons("commemoration");
  const baotha = getSeasons("baotha");

  return (
    <main className="mx-auto max-w-6xl px-5 py-12 sm:px-8 sm:py-16">
      <header className="max-w-2xl">
        <h1
          className="mt-1 flex flex-wrap items-baseline gap-x-3 gap-y-1 text-4xl text-ink sm:text-5xl"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          <span>Feasts & commemorations</span>
          <span className="text-ink-soft/50" aria-hidden>
            —
          </span>
          <span className="syr syr-meta text-5xl text-teal-deep sm:text-6xl">
            ܥܹܐ̈ܕܹܐ ܘܕܘܼܟ݂ܪ̈ܵܢܹܐ
          </span>
        </h1>
        <p className="mt-4 text-base leading-relaxed text-ink-soft">
          Feasts of the Lord, memorials of the saints, and the Rogation of the
          Ninevites — every office that stands alongside the main seasonal
          cycle. Dates are civil when fixed, and the weekday in the cycle when
          movable.
        </p>
        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-ink-soft">
          <ExclusiveTraditionPill tradition="syriac" />
          <ExclusiveTraditionPill tradition="chaldean" />
          <span>Unmarked offices are in both traditions.</span>
        </div>
      </header>

      <section className="mt-12">
        <h2
          className="text-lg text-ink"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Feasts of the Lord
        </h2>
        <SeasonGrid items={lordFeasts} exclusive={exclusive} />
      </section>

      <section className="mt-14">
        <h2
          className="text-lg text-ink"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Feasts & Fridays
        </h2>
        <SeasonGrid items={feasts} exclusive={exclusive} />
      </section>

      <section className="mt-14">
        <h2
          className="text-lg text-ink"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Commemorations
        </h2>
        <SeasonGrid items={commemorations} exclusive={exclusive} />
      </section>

      <section className="mt-14">
        <h2
          className="text-lg text-ink"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Rogation of the Ninevites
        </h2>
        <SeasonGrid items={baotha} exclusive={exclusive} />
      </section>
    </main>
  );
}
