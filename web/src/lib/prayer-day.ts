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
  // Week labels look like "ܫܒܬܐ ܓ" — match the numeral after ܫܒܬܐ,
  // not a letter that also appears inside the word ܫܒܬܐ itself.
  const m = prayerWeek.match(/ܫܒܬܐ\s*([ܐ-ܬ])/);
  if (m) return m[1] === letter;
  const parts = prayerWeek.trim().split(/\s+/);
  return parts[parts.length - 1] === letter;
}

export function matchesDay(p: PrayerSummary, lit: LitDay): boolean {
  if (p.dayEn && lit.weekdayEn) {
    return p.dayEn.toLowerCase() === lit.weekdayEn.toLowerCase();
  }
  if (p.day && lit.weekdaySyr) {
    return p.day.includes(lit.weekdaySyr) || lit.weekdaySyr.includes(p.day);
  }
  return !p.day && !p.dayEn;
}

export function sortHours(a: PrayerSummary, b: PrayerSummary) {
  return a.hourOrder - b.hourOrder || a.name.localeCompare(b.name, "syr");
}

/** Strip bidi marks / trailing punctuation so near-duplicate titles compare equal. */
function normalizePrayerName(name: string): string {
  return name
    .replace(/[\u200e\u200f\u200c\u200d\ufeff]/g, "")
    .replace(/[.\u00b7\u2022]+$/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function traditionKey(tradition: string[]): string {
  return [...tradition].sort().join("+");
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
