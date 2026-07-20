import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { PsalmClient } from "@/components/PsalmClient";
import { getPsalms, getPsalmSummary } from "@/lib/data";
import { psalmDisplayNumber } from "@/lib/psalm-label";

type Props = { params: Promise<{ id: string }> };

export async function generateStaticParams() {
  return getPsalms().map((p) => ({ id: p.id }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const summary = getPsalmSummary(id);
  if (!summary) return { title: "Psalm" };
  const n = psalmDisplayNumber(summary.number);
  if (n) return { title: `Psalm ${n} · ${summary.name}` };
  return { title: summary.name };
}

export default async function PsalmPage({ params }: Props) {
  const { id } = await params;
  const psalms = getPsalms();
  const index = psalms.findIndex((p) => p.id === id);
  if (index < 0) notFound();
  const summary = psalms[index];
  const prev = index > 0 ? psalms[index - 1] : undefined;
  const next = index < psalms.length - 1 ? psalms[index + 1] : undefined;

  return <PsalmClient id={id} summary={summary} prev={prev} next={next} />;
}
