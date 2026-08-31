import type { Metadata } from "next";
import { ResearchClient } from "@/components/ResearchClient";

export const metadata: Metadata = {
  title: "Resources for researchers",
  description:
    "A clearer index of the Christian Musicological Society of India catalog — manuscripts, liturgical books, and studies, with the original CMS links.",
};

export default function ResearchPage() {
  return (
    <main className="mx-auto max-w-6xl px-5 py-12 sm:px-8 sm:py-16">
      <header className="max-w-2xl fade-up">
        <p
          className="text-xs tracking-[0.22em] text-gold uppercase"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          CMS India catalog
        </p>
        <h1
          className="mt-3 text-4xl text-ink sm:text-5xl"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Resources for researchers
        </h1>
        <p className="mt-2 syr syr-meta text-3xl text-teal-deep" lang="syr">
          ܡܲܒܘܼܥ̈ܐ
        </p>
        <p className="mt-4 text-base leading-relaxed text-ink-soft">
          Manuscripts, liturgical books, audio, and studies from the Christian
          Musicological Society of India — the same collection, arranged so you
          can scan by language and topic instead of hunting through tabs,
          login boxes, and a double A–Z bar.
        </p>
      </header>
      <ResearchClient />
    </main>
  );
}
