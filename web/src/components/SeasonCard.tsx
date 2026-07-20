import Link from "next/link";
import type { Season } from "@/lib/types";
import { isPlaceholderSyriac } from "@/lib/syriac-text";

/** Drop placeholder / invented labels; keep corpus Syriac only. */
function corpusSyriac(s: string): string | null {
  if (isPlaceholderSyriac(s)) return null;
  return s;
}

export function SeasonCard({ season }: { season: Season }) {
  const syr = corpusSyriac(season.syriac);
  const en = season.english?.trim() || "";

  return (
    <Link
      href={`/season/${season.id}`}
      className="group relative block overflow-hidden rounded-sm border border-line bg-paper/70 px-5 py-5 shadow-[0_1px_0_rgba(20,38,28,0.04)] transition duration-300 hover:-translate-y-0.5 hover:border-teal/35 hover:bg-paper hover:shadow-[0_12px_28px_rgba(20,38,28,0.08)]"
    >
      <div className="absolute inset-y-0 left-0 w-0.5 bg-teal/0 transition group-hover:bg-teal" />
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          {syr ? (
            <h3 className="syr syr-meta text-2xl leading-snug text-ink transition group-hover:text-teal-deep sm:text-3xl">
              {syr}
            </h3>
          ) : null}
          {en ? (
            <p
              className={`text-sm text-ink-soft ${syr ? "mt-1.5" : ""}`}
              style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            >
              {en}
            </p>
          ) : null}
        </div>
        <span className="shrink-0 rounded-sm bg-paper-deep/80 px-2 py-1 text-xs tabular-nums text-ink-soft">
          {season.count}
        </span>
      </div>
    </Link>
  );
}

export function TraditionPills({ tradition }: { tradition: string[] }) {
  const labels: Record<string, string> = {
    syriac: "Assyrian",
    chaldean: "Chaldean",
    unspecified: "Unspecified",
  };

  return (
    <div className="flex flex-wrap gap-1.5">
      {tradition.map((t) => (
        <span
          key={t}
          className="rounded-sm border border-line bg-paper-deep/60 px-2 py-0.5 text-[11px] tracking-wide text-ink-soft uppercase"
        >
          {labels[t] ?? t}
        </span>
      ))}
    </div>
  );
}

const TRADITION_LABELS: Record<string, string> = {
  syriac: "Assyrian",
  chaldean: "Chaldean",
  unspecified: "Open",
};

function editionLabel(tradition: string[]): string {
  if (tradition.includes("syriac")) return TRADITION_LABELS.syriac;
  if (tradition.includes("chaldean")) return TRADITION_LABELS.chaldean;
  return TRADITION_LABELS.unspecified;
}

/** Clickable tradition chips — one link per Assyrian / Chaldean edition. */
export function TraditionEditionLinks({
  editions,
}: {
  editions: { id: string; tradition: string[] }[];
}) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {editions.map((ed) => (
        <Link
          key={ed.id}
          href={`/prayer/${ed.id}`}
          className="rounded-sm border border-line bg-paper-deep/60 px-2 py-0.5 text-[11px] tracking-wide text-ink-soft uppercase transition hover:border-teal/40 hover:text-teal-deep"
        >
          {editionLabel(ed.tradition)}
        </Link>
      ))}
    </div>
  );
}
