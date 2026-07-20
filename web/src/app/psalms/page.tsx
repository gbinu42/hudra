import type { Metadata } from "next";
import Link from "next/link";
import { getPsalms } from "@/lib/data";
import { psalmEnglishName } from "@/lib/psalm-label";

export const metadata: Metadata = {
  title: "Psalms",
};

export default function PsalmsPage() {
  const psalms = getPsalms();

  return (
    <main className="mx-auto max-w-3xl px-5 py-12 sm:px-8 sm:py-16">
      <header className="mb-10 fade-up">
        <p
          className="text-xs tracking-[0.22em] text-gold uppercase"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Psalter
        </p>
        <h1
          className="mt-3 text-4xl text-ink sm:text-5xl"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Psalms
        </h1>
        <p className="mt-2 syr syr-meta text-3xl text-teal-deep" lang="syr">
          ܡܙܡܘܪ̈ܐ
        </p>
        <p className="mt-4 max-w-xl text-base leading-relaxed text-ink-soft">
          The 150 psalms (Psalm 118 in 22 letter-sections), plus an opening
          title and biblical canticles numbered 151–167 ({psalms.length}{" "}
          readings in all).
        </p>
      </header>

      <ol className="divide-y divide-line border border-line bg-paper/60">
        {psalms.map((p) => (
          <li key={p.id}>
            <Link
              href={`/psalm/${p.id}`}
              className="group flex items-baseline justify-between gap-4 px-4 py-3.5 transition hover:bg-paper-deep/50"
            >
              <span
                className="min-w-0 text-sm text-ink transition group-hover:text-teal-deep sm:text-base"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                {psalmEnglishName(p)}
              </span>
              <span
                className="syr syr-meta shrink-0 text-end text-2xl text-ink transition group-hover:text-teal-deep"
                lang="syr"
                dir="rtl"
              >
                {p.name}
              </span>
            </Link>
          </li>
        ))}
      </ol>
    </main>
  );
}
