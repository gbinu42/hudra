import type { Metadata } from "next";
import { QankaRazaClient } from "@/components/QankaRazaClient";

export const metadata: Metadata = {
  title: "ܕܩܢܟܐ ܘܕܐܪܙܐ — Qanke & Raze",
};

export default function QankaRazaPage() {
  return (
    <main className="mx-auto max-w-6xl px-5 py-12 sm:px-8 sm:py-16">
      <header className="max-w-2xl fade-up">
        <p
          className="text-xs tracking-[0.22em] text-gold uppercase"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Divine Mysteries
        </p>
        <h1
          className="mt-3 flex flex-wrap items-baseline gap-x-3 gap-y-1 text-4xl text-ink sm:text-5xl"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          <span className="syr syr-meta text-5xl text-teal-deep sm:text-6xl">
            ܕܩܢܟܐ ܘܕܐܪܙܐ
          </span>
          <span className="text-ink-soft/50" aria-hidden>
            —
          </span>
          <span>Qanke and Raze</span>
        </h1>
        <p className="mt-4 text-base leading-relaxed text-ink-soft">
          Onitha d-Qanke and Onitha d-Raze of the Holy Qurbana, taken from the
          Hudra offices for Sundays, feasts, and commemorations. Assyrian and
          Chaldean recensions sit side by side when both survive.
        </p>
      </header>

      <QankaRazaClient />
    </main>
  );
}
