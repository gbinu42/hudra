import type { Metadata } from "next";
import { SearchClient } from "@/components/SearchClient";
import { getCatalog, getPsalms } from "@/lib/data";

export const metadata: Metadata = {
  title: "Search",
};

export default function SearchPage() {
  const catalog = getCatalog();

  return (
    <main className="mx-auto max-w-3xl px-5 py-12 sm:px-8 sm:py-16">
      <header className="mb-10">
        <p
          className="text-xs tracking-[0.22em] text-gold uppercase"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Find a prayer or psalm
        </p>
        <h1
          className="mt-3 text-4xl text-ink"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Search
        </h1>
      </header>
      <SearchClient prayers={catalog.prayers} psalms={getPsalms()} />
    </main>
  );
}
