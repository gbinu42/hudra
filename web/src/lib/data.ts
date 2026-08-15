import { readFileSync, existsSync } from "fs";
import path from "path";
import type {
  Catalog,
  PrayerRecord,
  PrayerSummary,
  PsalmRecord,
  PsalmSummary,
  Season,
} from "./types";
import {
  getLiturgicalDay,
  isLiturgicalEvening,
  type LitDay,
} from "./liturgical-calendar";
import { matchPrayersForDay } from "./prayer-day";
import { comparePsalms } from "./psalm-label";

/** Catalog ships with the app; full prayer bodies live in the repo data/ tree. */
const CATALOG_PATH = path.join(process.cwd(), "data", "catalog.json");
const PRAYERS_DIR = path.resolve(process.cwd(), "..", "data", "prayers");
const PSALMS_DIR = path.resolve(process.cwd(), "..", "data", "psalms");

let catalogCache: Catalog | null = null;

export function getCatalog(): Catalog {
  if (catalogCache) return catalogCache;
  const raw = JSON.parse(readFileSync(CATALOG_PATH, "utf8")) as Catalog;
  catalogCache = {
    ...raw,
    psalms: raw.psalms ?? [],
    counts: {
      ...raw.counts,
      psalms: raw.counts.psalms ?? raw.psalms?.length ?? 0,
    },
  };
  return catalogCache;
}

export function getSeasons(group?: Season["group"]): Season[] {
  const seasons = getCatalog().seasons;
  if (!group) return seasons;
  return seasons.filter((s) => s.group === group);
}

/** Cycle seasons that are a single feast day, not a multi-week season. */
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

export function isCycleFeastSeason(id: string): boolean {
  return CYCLE_FEAST_IDS.has(id);
}

export function getCycleFeastSeasons(): Season[] {
  return getCatalog().seasons.filter((s) => CYCLE_FEAST_IDS.has(s.id));
}

/**
 * Seasons whose offices are only Assyrian or only Chaldean.
 * Shared (both) seasons are omitted.
 */
export function getExclusiveSeasonTraditions(): Map<
  string,
  "syriac" | "chaldean"
> {
  const syriac = new Set<string>();
  const chaldean = new Set<string>();
  for (const p of getCatalog().prayers) {
    if (p.tradition.includes("syriac")) syriac.add(p.seasonId);
    if (p.tradition.includes("chaldean")) chaldean.add(p.seasonId);
  }
  const out = new Map<string, "syriac" | "chaldean">();
  for (const id of new Set([...syriac, ...chaldean])) {
    const hasS = syriac.has(id);
    const hasC = chaldean.has(id);
    if (hasS && !hasC) out.set(id, "syriac");
    else if (hasC && !hasS) out.set(id, "chaldean");
  }
  return out;
}

export function getSeason(id: string): Season | undefined {
  return getCatalog().seasons.find((s) => s.id === id);
}

export function getPrayersForSeason(seasonId: string): PrayerSummary[] {
  return getCatalog().prayers.filter((p) => p.seasonId === seasonId);
}

export function getPrayerSummary(id: string): PrayerSummary | undefined {
  return getCatalog().prayers.find((p) => p.id === id);
}

export function getPrayer(id: string): PrayerRecord | null {
  const file = path.join(PRAYERS_DIR, `${id}.json`);
  if (!existsSync(file)) return null;
  return JSON.parse(readFileSync(file, "utf8")) as PrayerRecord;
}

export function getPsalms(): PsalmSummary[] {
  return [...(getCatalog().psalms ?? [])].sort(comparePsalms);
}

export function getPsalmSummary(id: string): PsalmSummary | undefined {
  return getPsalms().find((p) => p.id === id);
}

export function getPsalmByNumber(number: number): PsalmSummary | undefined {
  return getPsalms().find((p) => p.number === number);
}

export function getPsalm(id: string): PsalmRecord | null {
  const file = path.join(PSALMS_DIR, `${id}.json`);
  if (!existsSync(file)) return null;
  return JSON.parse(readFileSync(file, "utf8")) as PsalmRecord;
}

export function searchPrayers(query: string, limit = 60): PrayerSummary[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const results: PrayerSummary[] = [];
  for (const p of getCatalog().prayers) {
    const hay = `${p.name} ${p.holiday} ${p.holidayEn || ""} ${p.week} ${p.day} ${p.dayEn} ${p.hour} ${p.hourEn}`.toLowerCase();
    if (hay.includes(q) || p.name.includes(query.trim())) {
      results.push(p);
      if (results.length >= limit) break;
    }
  }
  return results;
}

export type TodaysPrayers = {
  lit: LitDay;
  season: Season | undefined;
  prayers: PrayerSummary[];
  /** True when week+day matched; false if we fell back to day-only or season. */
  exact: boolean;
  seasonPrayers?: PrayerSummary[];
  seasonExact?: boolean;
  /** True when the civil clock is at/after 18:00 (day already advanced). */
  fromEvening: boolean;
};

/** Prayers for a liturgical calendar date (YYYY-MM-DD, midnight — no evening shift). */
export function getPrayersForLiturgicalDate(iso: string): TodaysPrayers {
  const [y, m, d] = iso.split("-").map(Number);
  const lit = getLiturgicalDay(new Date(y, m - 1, d));
  const office = matchPrayersForDay(getCatalog().prayers, lit);
  return {
    lit,
    season: getSeason(lit.seasonId),
    prayers: office.prayers,
    exact: office.exact,
    seasonPrayers: office.seasonPrayers,
    seasonExact: office.seasonExact,
    fromEvening: false,
  };
}

/** Prayers for the current liturgical day (season + week + weekday). */
export function getTodaysPrayers(date: Date = new Date()): TodaysPrayers {
  const lit = getLiturgicalDay(date);
  const office = matchPrayersForDay(getCatalog().prayers, lit);
  return {
    lit,
    season: getSeason(lit.seasonId),
    prayers: office.prayers,
    exact: office.exact,
    seasonPrayers: office.seasonPrayers,
    seasonExact: office.seasonExact,
    fromEvening: isLiturgicalEvening(date),
  };
}

export type DayBucket = {
  day: string;
  dayEn: string;
  dayOrder: number;
  hours: PrayerSummary[];
};

export type WeekBucket = {
  week: string;
  days: DayBucket[];
};

/** Group a season's prayers by week → day → hour order. */
export function organizeSeason(prayers: PrayerSummary[]): WeekBucket[] {
  const byWeek = new Map<string, PrayerSummary[]>();
  for (const p of prayers) {
    const key = p.week || "—";
    if (!byWeek.has(key)) byWeek.set(key, []);
    byWeek.get(key)!.push(p);
  }

  const weeks: WeekBucket[] = [];
  for (const [week, items] of byWeek) {
    const byDay = new Map<string, PrayerSummary[]>();
    for (const p of items) {
      const key = p.day || "—";
      if (!byDay.has(key)) byDay.set(key, []);
      byDay.get(key)!.push(p);
    }
    const days: DayBucket[] = [];
    for (const [day, dayItems] of byDay) {
      const sorted = [...dayItems].sort(
        (a, b) =>
          a.hourOrder - b.hourOrder || a.name.localeCompare(b.name, "syr"),
      );
      days.push({
        day,
        dayEn: dayItems[0]?.dayEn || "",
        dayOrder: dayItems[0]?.dayOrder ?? 99,
        hours: sorted,
      });
    }
    days.sort((a, b) => a.dayOrder - b.dayOrder || a.day.localeCompare(b.day));
    weeks.push({ week, days });
  }

  weeks.sort((a, b) => {
    if (a.week === "—") return 1;
    if (b.week === "—") return -1;
    return a.week.localeCompare(b.week, "syr");
  });
  return weeks;
}

export { prayerParagraphs } from "./prayer-text";
