import Link from "next/link";
import type { Season } from "@/lib/types";

/** Drop placeholder / invented labels; keep corpus Syriac only. */
function corpusSyriac(s: string): string | null {
  if (!s || s === "ܠܐ ܝܕܝܥܐ" || s === "—") return null;
  return s;
}

/** English label without embedded Syriac remnants from catalog build. */
function englishLabel(s: string): string {
  const cleaned = s
    .replace(/[\u0700-\u074F\u200e\u200f\u200c]+/g, "")
    .replace(/\s*[—–-]\s*/g, " — ")
    .replace(/\s+/g, " ")
    .replace(/^—\s*|\s*—$/g, "")
    .trim();
  return cleaned || s;
}

export function SeasonCard({ season }: { season: Season }) {
  const syr = corpusSyriac(season.syriac);
  const en = englishLabel(season.english);

  return (
    <Link
      href={`/season/${season.id}`}
      className="group relative block overflow-hidden rounded-sm border border-line bg-paper/70 px-5 py-5 shadow-[0_1px_0_rgba(20,38,28,0.04)] transition duration-300 hover:-translate-y-0.5 hover:border-teal/35 hover:bg-paper hover:shadow-[0_12px_28px_rgba(20,38,28,0.08)]"
    >
      <div className="absolute inset-y-0 left-0 w-0.5 bg-teal/0 transition group-hover:bg-teal" />
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
          {syr ? (
            <h3 className="syr syr-meta text-3xl text-ink transition group-hover:text-teal-deep">
              {syr}
            </h3>
          ) : null}
          <p
            className="text-sm text-ink-soft"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            {en}
          </p>
        </div>
        <span className="shrink-0 rounded-sm bg-paper-deep/80 px-2 py-1 text-xs tabular-nums text-ink-soft">
          {season.count}
        </span>
      </div>
    </Link>
  );
}

export function TraditionPills({
  tradition,
}: {
  tradition: string[];
}) {
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
