import type { Metadata } from "next";
import { CalendarClient } from "@/components/CalendarClient";
import { getCatalog } from "@/lib/data";
import { isPlaceholderSyriac } from "@/lib/syriac-text";

export const metadata: Metadata = {
  title: "Liturgical Calendar",
  description:
    "East Syriac liturgical calendar — seasons, weeks, and feasts of the Hudra cycle.",
};

export default function CalendarPage() {
  const catalog = getCatalog();
  const seasonLabels: Record<string, string> = {};
  for (const s of catalog.seasons) {
    if (!isPlaceholderSyriac(s.syriac)) {
      seasonLabels[s.id] = s.syriac;
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-5 py-12 sm:px-8 sm:py-16">
      <CalendarClient prayers={catalog.prayers} seasonLabels={seasonLabels} />
    </main>
  );
}
