import type { LitDay } from "./liturgical-calendar";
import type { PrayerSummary } from "./types";

/** Syriac alphabetic numerals used in week labels (ܫܒܬܐ ܐ …). */
const WEEK_LETTERS = "ܐܒܓܕܗܘܙܚܛܝܟܠܡܢܣܥܦܨܩܪܫܬ";

function weekLetter(weekNum: number): string {
  if (weekNum < 1) return WEEK_LETTERS[0];
  if (weekNum > WEEK_LETTERS.length) {
    return WEEK_LETTERS[WEEK_LETTERS.length - 1];
  }
  return WEEK_LETTERS[weekNum - 1];
}

export function matchesWeek(prayerWeek: string, weekNum: number): boolean {
  if (!prayerWeek || prayerWeek === "—") return true;
  const letter = weekLetter(weekNum);
  const bare = stripSyriacMarks(prayerWeek);
  // Week labels look like "ܫܒܬܐ ܓ" — match the numeral after ܫܒܬܐ,
  // not a letter that also appears inside the word ܫܒܬܐ itself.
  const m = bare.match(/ܫܒܬܐ\s*([ܐ-ܬ])/);
  if (m) return m[1] === letter;
  const parts = bare.trim().split(/\s+/);
  return parts[parts.length - 1] === letter;
}

/** Strip East Syriac vowels / diacritics so pointed labels still match catalog days. */
function stripSyriacMarks(s: string): string {
  return s.replace(/[\u0730-\u074A\u0308\u0323\u032E\u0307]/g, "");
}

export function matchesDay(p: PrayerSummary, lit: LitDay): boolean {
  if (p.dayEn && lit.weekdayEn) {
    return p.dayEn.toLowerCase() === lit.weekdayEn.toLowerCase();
  }
  if (p.day && lit.weekdaySyr) {
    const day = stripSyriacMarks(p.day);
    const litDay = stripSyriacMarks(lit.weekdaySyr);
    return day.includes(litDay) || litDay.includes(day);
  }
  return !p.day && !p.dayEn;
}

export function sortHours(a: PrayerSummary, b: PrayerSummary) {
  return a.hourOrder - b.hourOrder || a.name.localeCompare(b.name, "syr");
}

/** Strip bidi marks / trailing punctuation so near-duplicate titles compare equal. */
export function normalizePrayerName(name: string): string {
  return name
    .replace(/[\u200e\u200f\u200c\u200d\ufeff]/g, "")
    .replace(/[.\u00b7\u2022]+$/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function traditionKey(tradition: string[]): string {
  return [...tradition].sort().join("+");
}

const TRADITION_RANK: Record<string, number> = {
  syriac: 0,
  chaldean: 1,
  unspecified: 2,
};

function primaryTradition(tradition: string[]): string {
  return (
    [...tradition].sort(
      (a, b) => (TRADITION_RANK[a] ?? 9) - (TRADITION_RANK[b] ?? 9),
    )[0] || "unspecified"
  );
}

function sortEditions(a: PrayerSummary, b: PrayerSummary) {
  return (
    (TRADITION_RANK[primaryTradition(a.tradition)] ?? 9) -
      (TRADITION_RANK[primaryTradition(b.tradition)] ?? 9) ||
    b.chars - a.chars
  );
}

/**
 * hudra.org sometimes lists the same Assyrian (or Chaldean) office twice with
 * nearly identical titles. Keep the longer copy per hour + tradition slot.
 */
export function dedupeSameSlot(prayers: PrayerSummary[]): PrayerSummary[] {
  const best = new Map<string, PrayerSummary>();
  for (const p of prayers) {
    const key = [
      p.seasonId,
      p.week,
      p.day || p.dayEn,
      p.hourEn || p.hour,
      traditionKey(p.tradition),
      normalizePrayerName(p.name),
    ].join("|");
    const prev = best.get(key);
    if (!prev || p.chars > prev.chars) best.set(key, p);
  }
  return [...best.values()].sort(sortHours);
}

export type OfficeEdition = {
  id: string;
  name: string;
  tradition: string[];
  chars: number;
};

/** One liturgical office with one row per tradition edition (Assyrian / Chaldean). */
export type OfficeGroup = {
  key: string;
  name: string;
  hour: string;
  hourEn: string;
  hourOrder: number;
  editions: OfficeEdition[];
};

/**
 * Pair near-identical titles in the same hour so Assyrian + Chaldean share one row.
 */
export function groupOfficeEditions(prayers: PrayerSummary[]): OfficeGroup[] {
  const buckets = new Map<string, PrayerSummary[]>();
  for (const p of prayers) {
    const key = [
      p.hourOrder,
      p.hourEn || p.hour || "hour",
      normalizePrayerName(p.name),
    ].join("|");
    const list = buckets.get(key);
    if (list) list.push(p);
    else buckets.set(key, [p]);
  }

  const groups: OfficeGroup[] = [];
  for (const [key, list] of buckets) {
    const sorted = [...list].sort(sortEditions);
    const display = sorted.reduce((best, p) =>
      normalizePrayerName(p.name).length > normalizePrayerName(best.name).length
        ? p
        : best,
    );
    groups.push({
      key,
      name: normalizePrayerName(display.name),
      hour: display.hour,
      hourEn: display.hourEn,
      hourOrder: display.hourOrder,
      editions: sorted.map((p) => ({
        id: p.id,
        name: p.name,
        tradition: p.tradition,
        chars: p.chars,
      })),
    });
  }

  return groups.sort(
    (a, b) =>
      a.hourOrder - b.hourOrder || a.name.localeCompare(b.name, "syr"),
  );
}

export type DayOffice = {
  prayers: PrayerSummary[];
  /** True when week+day matched; false if we fell back to day-only or season. */
  exact: boolean;
};

/** Match catalog summaries to a liturgical day (season + week + weekday). */
export function matchPrayersForDay(
  prayers: PrayerSummary[],
  lit: LitDay,
): DayOffice {
  const inSeason = prayers.filter((p) => p.seasonId === lit.seasonId);

  const byWeekAndDay = dedupeSameSlot(
    inSeason.filter(
      (p) => matchesDay(p, lit) && matchesWeek(p.week, lit.week),
    ),
  );

  if (byWeekAndDay.length > 0) {
    return { prayers: byWeekAndDay, exact: true };
  }

  const byDay = dedupeSameSlot(
    inSeason.filter((p) => matchesDay(p, lit)),
  );
  if (byDay.length > 0) {
    return { prayers: byDay, exact: false };
  }

  const undated = dedupeSameSlot(
    inSeason.filter((p) => !p.day && !p.dayEn),
  );
  return { prayers: undated.slice(0, 12), exact: false };
}

export type HourGroup = {
  key: string;
  hour: string;
  hourEn: string;
  hourOrder: number;
  prayers: PrayerSummary[];
};

export function groupPrayersByHour(prayers: PrayerSummary[]): HourGroup[] {
  const groups: HourGroup[] = [];
  for (const p of prayers) {
    const key = `${p.hourOrder}|${p.hourEn || p.hour || "hour"}`;
    let g = groups.find((x) => x.key === key);
    if (!g) {
      g = {
        key,
        hour: p.hour,
        hourEn: p.hourEn,
        hourOrder: p.hourOrder,
        prayers: [],
      };
      groups.push(g);
    }
    g.prayers.push(p);
  }
  return groups;
}
