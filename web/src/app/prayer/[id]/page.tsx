import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { PrayerClient } from "@/components/PrayerClient";
import {
  getCatalog,
  getPrayerSummary,
  getSeason,
} from "@/lib/data";

type Props = { params: Promise<{ id: string }> };

export async function generateStaticParams() {
  return getCatalog().prayers.map((p) => ({ id: p.id }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const summary = getPrayerSummary(id);
  if (!summary) return { title: "Prayer" };
  return { title: summary.name };
}

export default async function PrayerPage({ params }: Props) {
  const { id } = await params;
  const summary = getPrayerSummary(id);
  if (!summary) notFound();
  const season = getSeason(summary.seasonId);

  return <PrayerClient id={id} summary={summary} season={season} />;
}
