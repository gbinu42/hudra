"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { prayerParagraphs } from "@/lib/prayer-text";
import { psalmDisplayNumber } from "@/lib/psalm-label";
import type { PsalmRecord, PsalmSummary } from "@/lib/types";

function assetUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
  return `${base}${path}`;
}

export function PsalmClient({
  id,
  summary,
  prev,
  next,
}: {
  id: string;
  summary: PsalmSummary;
  prev?: PsalmSummary;
  next?: PsalmSummary;
}) {
  const [psalm, setPsalm] = useState<PsalmRecord | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [id]);

  useEffect(() => {
    let cancelled = false;
    setError(false);
    setPsalm(null);
    fetch(assetUrl(`/data/psalms/${id}.json`))
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then((data: PsalmRecord) => {
        if (!cancelled) setPsalm(data);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  const paragraphs = psalm ? prayerParagraphs(psalm.text) : [];
  const hasHtml = Boolean(psalm?.html?.trim());
  const numberLabel = psalmDisplayNumber(summary.number);

  return (
    <main className="mx-auto max-w-3xl px-5 py-12 sm:px-8 sm:py-16">
      <nav className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-ink-soft">
        <Link href="/psalms" className="hover:text-teal">
          Psalms
        </Link>
        <span className="opacity-50">/</span>
        <span className="syr syr-inline text-2xl text-ink" lang="syr">
          {summary.name}
        </span>
      </nav>

      <header className="mt-6 border-b border-line pb-8 fade-up">
        {numberLabel ? (
          <p
            className="text-xs tracking-[0.22em] text-gold uppercase"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            Psalm {numberLabel}
          </p>
        ) : null}
        <h1
          className="syr syr-block mt-2 text-4xl leading-snug text-teal-deep sm:text-5xl"
          lang="syr"
        >
          {psalm?.itemName || summary.name}
        </h1>
      </header>

      {error ? (
        <p className="mt-10 text-sm text-ink-soft">Could not load this psalm.</p>
      ) : !psalm ? (
        <p className="mt-10 text-sm text-ink-soft">Loading psalm…</p>
      ) : hasHtml ? (
        <article
          className="prayer-body mt-10"
          dangerouslySetInnerHTML={{ __html: psalm.html! }}
        />
      ) : (
        <article className="prayer-body mt-10">
          {paragraphs.map((p, i) => (
            <p key={i}>{p}</p>
          ))}
        </article>
      )}

      <nav className="mt-14 flex flex-wrap items-center justify-between gap-4 border-t border-line pt-6 text-sm">
        {prev ? (
          <Link
            href={`/psalm/${prev.id}`}
            className="text-teal transition hover:underline"
          >
            ←{" "}
            {psalmDisplayNumber(prev.number)
              ? `Psalm ${psalmDisplayNumber(prev.number)}`
              : prev.name}
          </Link>
        ) : (
          <span />
        )}
        {next ? (
          <Link
            href={`/psalm/${next.id}`}
            className="ms-auto text-teal transition hover:underline"
          >
            {psalmDisplayNumber(next.number)
              ? `Psalm ${psalmDisplayNumber(next.number)}`
              : next.name}{" "}
            →
          </Link>
        ) : null}
      </nav>

      {psalm ? (
        <p className="mt-8 text-xs text-ink-soft">ID {psalm.itemId}</p>
      ) : null}
    </main>
  );
}
