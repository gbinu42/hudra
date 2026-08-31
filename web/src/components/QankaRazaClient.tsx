"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ExclusiveTraditionPill } from "@/components/SeasonCard";
import {
  feastSeasonIdsForCycleFriday,
  seasonWhen,
} from "@/lib/feast-when";
import { occasionHasMajorDiff, hymnsDifferMajorly } from "@/lib/hymn-diff";
import { weekNumberFromLabel } from "@/lib/prayer-day";
import { isPlaceholderSyriac } from "@/lib/syriac-text";
import type {
  QankaRazaCatalog,
  QankaRazaEdition,
  QankaRazaHymn,
  QankaRazaOccasion,
  QankaRazaSeason,
} from "@/lib/qanka-raza";

const CYCLE_FEAST_IDS = new Set([
  "yalda",
  "circumcision",
  "denha-feast",
  "lazarus",
  "hosannas",
  "passover",
  "passion",
  "great-saturday",
  "easter",
  "ascension",
  "pentecost",
]);

function assetUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
  return `${base}${path}`;
}

type KindFilter = "all" | "sunday" | "feast" | "commemoration";

function occasionKind(o: QankaRazaOccasion): KindFilter | "other" {
  if (
    o.seasonGroup === "feast" ||
    o.seasonGroup === "baotha" ||
    CYCLE_FEAST_IDS.has(o.seasonId)
  ) {
    return "feast";
  }
  if (o.seasonGroup === "commemoration") return "commemoration";
  if (o.dayEn === "Sunday") return "sunday";
  if (o.dayEn === "Friday") return "commemoration";
  if (!o.dayEn && (o.seasonGroup === "feast" || o.seasonGroup === "baotha")) {
    return "feast";
  }
  return "other";
}

function HymnCell({
  hymn,
  prayerId,
  label,
  tradition,
}: {
  hymn: QankaRazaHymn | null;
  prayerId?: string;
  label: string;
  tradition: "syriac" | "chaldean";
}) {
  const accent =
    tradition === "syriac"
      ? "border-teal/40 text-teal-deep"
      : "border-gold/50 text-[color:var(--gold)]";
  if (!hymn) {
    return (
      <div className="min-w-0 rounded-sm border border-dashed border-line/80 bg-paper-deep/30 px-3 py-3">
        <p className={`text-[11px] tracking-wide uppercase ${accent}`}>
          {label}
        </p>
        <p className="mt-2 text-sm text-ink-soft/60">—</p>
      </div>
    );
  }

  return (
    <div
      className={`min-w-0 rounded-sm border bg-paper/80 px-3 py-3 ${
        tradition === "syriac" ? "border-teal/35" : "border-gold/40"
      }`}
    >
      <div className="flex items-baseline justify-between gap-2">
        <p className={`text-[11px] tracking-wide uppercase ${accent}`}>
          {label}
        </p>
        {prayerId ? (
          <Link
            href={`/prayer/${prayerId}`}
            className="text-[11px] tracking-wide text-ink-soft hover:text-ink"
          >
            Full office
          </Link>
        ) : null}
      </div>
      <div
        className="qanka-hymn syr mt-2 text-[length:var(--syr-body-size)] leading-relaxed text-ink"
        lang="syr"
        dir="rtl"
        dangerouslySetInnerHTML={{ __html: hymn.html || hymn.text }}
      />
    </div>
  );
}

function HymnPair({
  kindLabel,
  kindSyr,
  syriac,
  chaldean,
}: {
  kindLabel: string;
  kindSyr: string;
  syriac: QankaRazaEdition | null;
  chaldean: QankaRazaEdition | null;
}) {
  const sHymn = kindLabel === "qanka" ? syriac?.qanka : syriac?.raza;
  const cHymn = kindLabel === "qanka" ? chaldean?.qanka : chaldean?.raza;
  if (!sHymn && !cHymn) return null;
  const differs = hymnsDifferMajorly(sHymn, cHymn);

  return (
    <div
      className={`mt-4 rounded-sm ${
        differs
          ? "border border-[#c45c2b]/45 bg-[#c45c2b]/[0.06] px-3 py-3 sm:px-4"
          : ""
      }`}
    >
      <h4 className="flex flex-wrap items-baseline gap-x-2.5 gap-y-1 text-sm text-ink">
        <span className="syr syr-meta text-2xl text-teal-deep">{kindSyr}</span>
        <span
          className="text-ink-soft"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          {kindLabel === "qanka" ? "Onitha d-Qanke" : "Onitha d-Raze"}
        </span>
        {differs ? (
          <span className="rounded-sm border border-[#c45c2b]/50 bg-[#c45c2b]/12 px-2 py-0.5 text-[11px] tracking-wide text-[#9a3d18] uppercase">
            Texts differ
          </span>
        ) : null}
      </h4>
      <div className="mt-2 grid gap-3 md:grid-cols-2">
        <HymnCell
          hymn={sHymn ?? null}
          prayerId={syriac?.id}
          label="Assyrian"
          tradition="syriac"
        />
        <HymnCell
          hymn={cHymn ?? null}
          prayerId={chaldean?.id}
          label="Chaldean"
          tradition="chaldean"
        />
      </div>
    </div>
  );
}

function collapseWs(s: string): string {
  return s.replace(/\s+/g, " ").trim();
}

function sameLabel(a: string, b: string): boolean {
  return collapseWs(a) === collapseWs(b);
}

type NamedFeast = { id?: string; syr: string; en: string };

function dukhranaFromName(name: string): string {
  const m = name.match(/ܕܘܼ?ܟ݂?ܪܵ?ܢܵ?ܐ[\s\S]*$/);
  return m ? collapseWs(m[0].replace(/[.\u200f\u200e]+$/g, "")) : "";
}

function namedFeastsFor(
  o: QankaRazaOccasion,
  seasons: Map<string, QankaRazaSeason>,
  lastFridayWeek?: number,
): NamedFeast[] {
  const kind = occasionKind(o);
  if (
    kind === "feast" ||
    (kind === "commemoration" && o.seasonGroup === "commemoration")
  ) {
    const syr = !isPlaceholderSyriac(o.holiday)
      ? o.holiday
      : collapseWs(o.name);
    const en = (o.holidayEn || o.seasonEnglish).trim();
    if (syr || en) return [{ id: o.seasonId, syr, en }];
  }

  if (o.dayEn !== "Friday") return [];

  const weekN = weekNumberFromLabel(o.week);
  const ids =
    weekN != null
      ? feastSeasonIdsForCycleFriday(o.seasonId, weekN, lastFridayWeek)
      : [];
  const fromCatalog: NamedFeast[] = [];
  for (const id of ids) {
    const s = seasons.get(id);
    if (!s) continue;
    fromCatalog.push({
      id: s.id,
      syr: isPlaceholderSyriac(s.syriac) ? "" : s.syriac,
      en: s.english.trim(),
    });
  }
  if (fromCatalog.length) return fromCatalog;

  const fromName = dukhranaFromName(o.name);
  return fromName ? [{ syr: fromName, en: "" }] : [];
}

function OccasionCard({
  o,
  seasons,
  lastFridayWeek,
}: {
  o: QankaRazaOccasion;
  seasons: Map<string, QankaRazaSeason>;
  lastFridayWeek?: number;
}) {
  const named = namedFeastsFor(o, seasons, lastFridayWeek);
  const office = collapseWs(o.name);
  const showOffice =
    Boolean(office) && !named.some((n) => n.syr && sameLabel(n.syr, office));
  const seasonSyr = !isPlaceholderSyriac(o.seasonSyriac)
    ? o.seasonSyriac
    : "";
  const showSeasonSyr =
    Boolean(seasonSyr) &&
    !named.some((n) => n.syr && sameLabel(n.syr, seasonSyr));
  const showSeasonEn =
    Boolean(o.seasonEnglish) &&
    !named.some((n) => n.en && sameLabel(n.en, o.seasonEnglish));
  const when =
    seasonWhen(o.seasonId) ||
    named.map((n) => (n.id ? seasonWhen(n.id) : undefined)).find(Boolean);
  const hasHymn = [o.syriac, o.chaldean].some(
    (ed) => ed?.qanka || ed?.raza,
  );
  const officeId = o.syriac?.id || o.chaldean?.id;

  return (
    <article className="rounded-sm border border-line bg-paper/70 px-4 py-5 sm:px-5">
      <header className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <div className="min-w-0">
          {named.length
            ? named.map((n) => (
                <div key={`${n.id ?? ""}-${n.en}-${n.syr}`} className="mt-2 first:mt-0">
                  {n.syr ? (
                    <h3 className="syr syr-meta text-2xl leading-snug text-ink sm:text-3xl">
                      {n.syr}
                    </h3>
                  ) : null}
                  {n.en ? (
                    <p
                      className={`text-sm text-ink-soft ${n.syr ? "mt-1" : ""}`}
                      style={{
                        fontFamily: "var(--font-display), Georgia, serif",
                      }}
                    >
                      {n.en}
                    </p>
                  ) : null}
                </div>
              ))
            : office ? (
                <h3 className="syr syr-meta text-2xl leading-snug text-ink sm:text-3xl">
                  {office}
                </h3>
              ) : null}
          {showOffice ? (
            <p className="syr syr-meta mt-1.5 text-xl leading-snug text-teal-deep">
              {office}
            </p>
          ) : null}
          <p className="mt-1 flex flex-wrap items-baseline gap-x-2 text-sm text-ink-soft">
            {showSeasonSyr ? (
              <span className="syr syr-meta text-xl text-teal-deep">
                {seasonSyr}
              </span>
            ) : null}
            {showSeasonEn ? <span>{o.seasonEnglish}</span> : null}
            {o.week ? (
              <span className="syr syr-meta text-lg">{o.week}</span>
            ) : null}
            {o.dayEn ? <span>{o.dayEn}</span> : null}
            {when ? <span className="text-gold">{when}</span> : null}
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap items-center justify-end gap-1.5">
          {occasionHasMajorDiff(o) ? (
            <span className="rounded-sm border border-[#c45c2b]/50 bg-[#c45c2b]/12 px-2 py-0.5 text-[11px] tracking-wide text-[#9a3d18] uppercase">
              Texts differ
            </span>
          ) : null}
          {o.syriac && o.chaldean ? (
            <span className="rounded-sm border border-line bg-paper-deep/70 px-2 py-0.5 text-[11px] tracking-wide text-ink-soft uppercase">
              Both editions
            </span>
          ) : o.syriac ? (
            <ExclusiveTraditionPill tradition="syriac" />
          ) : (
            <ExclusiveTraditionPill tradition="chaldean" />
          )}
        </div>
      </header>

      {hasHymn ? (
        <>
          <HymnPair
            kindLabel="qanka"
            kindSyr="ܕܩܢܟܐ"
            syriac={o.syriac}
            chaldean={o.chaldean}
          />
          <HymnPair
            kindLabel="raza"
            kindSyr="ܕܐܪܙܐ"
            syriac={o.syriac}
            chaldean={o.chaldean}
          />
        </>
      ) : (
        <p className="mt-4 text-sm text-ink-soft">
          No ܕܩܢܟܐ or ܕܐܪܙܐ is marked in the Divine Mysteries for this day.
          {officeId ? (
            <>
              {" "}
              <Link
                href={`/prayer/${officeId}`}
                className="text-teal hover:text-teal-deep"
              >
                Open the office
              </Link>
            </>
          ) : null}
        </p>
      )}
    </article>
  );
}

const FILTERS: { id: KindFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "sunday", label: "Sundays" },
  { id: "feast", label: "Feasts" },
  { id: "commemoration", label: "Commemorations" },
];

export function QankaRazaClient() {
  const [data, setData] = useState<QankaRazaCatalog | null>(null);
  const [error, setError] = useState(false);
  const [kind, setKind] = useState<KindFilter>("all");
  const [seasonId, setSeasonId] = useState<string>("all");
  const [pairedOnly, setPairedOnly] = useState(false);
  const [diffOnly, setDiffOnly] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetch(assetUrl("/data/qanka-raza.json"))
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then((json: QankaRazaCatalog) => {
        if (!cancelled) setData(json);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = useMemo(() => {
    if (!data) return [];
    return data.occasions.filter((o) => {
      if (pairedOnly && !(o.syriac && o.chaldean)) return false;
      if (diffOnly && !occasionHasMajorDiff(o)) return false;
      if (seasonId !== "all" && o.seasonId !== seasonId) return false;
      if (kind !== "all" && occasionKind(o) !== kind) return false;
      return true;
    });
  }, [data, kind, seasonId, pairedOnly, diffOnly]);

  const grouped = useMemo(() => {
    const by = new Map<string, QankaRazaOccasion[]>();
    for (const o of filtered) {
      const list = by.get(o.seasonId) ?? [];
      list.push(o);
      by.set(o.seasonId, list);
    }
    return [...by.entries()];
  }, [filtered]);

  if (error) {
    return (
      <p className="mt-10 text-ink-soft">
        Could not load the ܕܩܢܟܐ / ܕܐܪܙܐ list. Run{" "}
        <code className="text-sm">python3 scripts/extract_qanka_raza.py</code>{" "}
        and rebuild.
      </p>
    );
  }

  if (!data) {
    return <p className="mt-10 text-ink-soft">Loading…</p>;
  }

  const seasonMeta = new Map(data.seasons.map((s) => [s.id, s]));
  const lastFridayWeek = new Map<string, number>();
  for (const o of data.occasions) {
    if (o.dayEn !== "Friday") continue;
    const n = weekNumberFromLabel(o.week);
    if (n == null) continue;
    lastFridayWeek.set(
      o.seasonId,
      Math.max(lastFridayWeek.get(o.seasonId) ?? 0, n),
    );
  }

  return (
    <>
      <p className="mt-4 text-sm text-ink-soft">
        {data.counts.occasions} days · {data.counts.paired} with both editions ·{" "}
        {data.occasions.filter(occasionHasMajorDiff).length} with differing
        texts · {data.counts.qanka} ܕܩܢܟܐ · {data.counts.raza} ܕܐܪܙܐ
      </p>

      <div className="mt-6 flex flex-wrap items-center gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            type="button"
            onClick={() => setKind(f.id)}
            className={`rounded-sm border px-3 py-1.5 text-xs tracking-wide transition ${
              kind === f.id
                ? "border-teal bg-teal/15 text-teal-deep"
                : "border-line bg-paper/70 text-ink-soft hover:border-teal/35"
            }`}
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            {f.label}
          </button>
        ))}
        <button
          type="button"
          onClick={() => setPairedOnly((v) => !v)}
          className={`rounded-sm border px-3 py-1.5 text-xs tracking-wide transition ${
            pairedOnly
              ? "border-gold bg-gold/15 text-[color:var(--gold)]"
              : "border-line bg-paper/70 text-ink-soft hover:border-gold/40"
          }`}
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Side by side only
        </button>
        <button
          type="button"
          onClick={() => setDiffOnly((v) => !v)}
          className={`rounded-sm border px-3 py-1.5 text-xs tracking-wide transition ${
            diffOnly
              ? "border-[#c45c2b]/60 bg-[#c45c2b]/15 text-[#9a3d18]"
              : "border-line bg-paper/70 text-ink-soft hover:border-[#c45c2b]/40"
          }`}
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Texts differ
        </button>
        <select
          value={seasonId}
          onChange={(e) => setSeasonId(e.target.value)}
          className="rounded-sm border border-line bg-paper/80 px-2 py-1.5 text-xs text-ink"
        >
          <option value="all">Every season</option>
          {data.seasons.map((s) => (
            <option key={s.id} value={s.id}>
              {s.english}
            </option>
          ))}
        </select>
      </div>

      <p className="mt-3 text-xs text-ink-soft">
        Showing {filtered.length} of {data.counts.occasions}
      </p>

      <div className="mt-10 space-y-14">
        {grouped.length === 0 ? (
          <p className="text-ink-soft">No days match these filters.</p>
        ) : (
          grouped.map(([sid, items]) => {
          const s = seasonMeta.get(sid);
          return (
            <section key={sid} id={sid}>
              <h2
                className="flex flex-wrap items-baseline gap-x-3 text-xl text-ink"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                {s && !isPlaceholderSyriac(s.syriac) ? (
                  <span className="syr syr-meta text-3xl text-teal-deep">
                    {s.syriac}
                  </span>
                ) : null}
                <span>{s?.english ?? sid}</span>
                <span className="text-sm font-normal text-ink-soft">
                  {items.length}
                </span>
              </h2>
              <div className="mt-4 space-y-5">
                {items.map((o, i) => (
                  <OccasionCard
                    key={`${o.seasonId}-${o.week}-${o.day}-${i}`}
                    o={o}
                    seasons={seasonMeta}
                    lastFridayWeek={lastFridayWeek.get(o.seasonId)}
                  />
                ))}
              </div>
            </section>
          );
        })
        )}
      </div>
    </>
  );
}
