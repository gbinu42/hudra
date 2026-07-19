"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { TraditionPills } from "@/components/SeasonCard";
import { prayerParagraphs } from "@/lib/prayer-text";
import type { PrayerRecord, PrayerSummary, Season } from "@/lib/types";

function assetUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
  return `${base}${path}`;
}

function MetaRow({
  label,
  syriac,
  english,
}: {
  label: string;
  syriac: string;
  english?: string;
}) {
  return (
    <div className="min-w-0">
      <dt className="text-xs tracking-wide text-ink-soft uppercase">{label}</dt>
      <dd className="mt-1 flex flex-wrap items-baseline gap-x-2.5 gap-y-0.5">
        {syriac ? (
          <span className="syr syr-meta text-3xl text-ink" lang="syr">
            {syriac}
          </span>
        ) : (
          <span className="text-3xl text-ink-soft">—</span>
        )}
        {english ? (
          <span className="text-sm text-ink-soft">{english}</span>
        ) : null}
      </dd>
    </div>
  );
}

export function PrayerClient({
  id,
  summary,
  season,
}: {
  id: string;
  summary: PrayerSummary;
  season?: Season;
}) {
  const [prayer, setPrayer] = useState<PrayerRecord | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setError(false);
    setPrayer(null);
    fetch(assetUrl(`/data/prayers/${id}.json`))
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then((data: PrayerRecord) => {
        if (!cancelled) setPrayer(data);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  const paragraphs = prayer ? prayerParagraphs(prayer.text) : [];
  const hasHtml = Boolean(prayer?.html?.trim());
  const seasonSyr =
    season?.syriac && season.syriac !== "ܠܐ ܝܕܝܥܐ" ? season.syriac : "";

  return (
    <main className="mx-auto max-w-3xl px-5 py-12 sm:px-8 sm:py-16">
      <nav className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-ink-soft">
        {season && (
          <>
            <Link href={`/season/${season.id}`} className="hover:text-teal">
              {season.english}
            </Link>
            <span className="opacity-50">/</span>
          </>
        )}
        <span className="syr syr-inline text-2xl text-ink" lang="syr">
          {summary.name}
        </span>
      </nav>

      <header className="mt-6 border-b border-line pb-8 fade-up">
        <h1
          className="syr syr-block text-4xl leading-snug text-teal-deep sm:text-5xl"
          lang="syr"
        >
          {prayer?.itemName || summary.name}
        </h1>
        {(summary.holidayEn || season?.english) && (
          <p
            className="mt-2 text-base text-ink-soft"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            {summary.holidayEn || season?.english}
          </p>
        )}
        <dl className="mt-6 grid gap-x-8 gap-y-4 text-sm sm:grid-cols-2">
          <MetaRow
            label="Season"
            syriac={
              seasonSyr ||
              prayer?.itemRelatedHoliday ||
              summary.holiday ||
              ""
            }
            english={season?.english}
          />
          <MetaRow label="Week" syriac={prayer?.week || summary.week || ""} />
          <MetaRow
            label="Day"
            syriac={prayer?.day || summary.day || ""}
            english={summary.dayEn || undefined}
          />
          <MetaRow
            label="Hour"
            syriac={prayer?.prayerTime || summary.hour || ""}
            english={
              summary.hourEn &&
              summary.hourEn !== (prayer?.prayerTime || summary.hour)
                ? summary.hourEn
                : undefined
            }
          />
        </dl>
        <div className="mt-5">
          <TraditionPills
            tradition={prayer?.tradition || summary.tradition}
          />
        </div>
      </header>

      {error ? (
        <p className="mt-10 text-sm text-ink-soft">
          Could not load this prayer.
        </p>
      ) : !prayer ? (
        <p className="mt-10 text-sm text-ink-soft">Loading prayer…</p>
      ) : hasHtml ? (
        <article
          className="prayer-body mt-10"
          dangerouslySetInnerHTML={{ __html: prayer.html! }}
        />
      ) : (
        <article className="prayer-body mt-10">
          {paragraphs.map((p, i) => (
            <p key={i}>{p}</p>
          ))}
        </article>
      )}

      {prayer ? (
        <p className="mt-14 border-t border-line pt-6 text-xs text-ink-soft">
          Source:{" "}
          <a
            href={prayer.source}
            className="text-teal hover:underline"
            target="_blank"
            rel="noreferrer"
          >
            {prayer.source}
          </a>{" "}
          · ID {prayer.itemId}
        </p>
      ) : null}
    </main>
  );
}
