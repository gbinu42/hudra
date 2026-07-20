/**
 * East Syriac liturgical calendar, ported from hudra.org's Flutter app
 * (Isaac, Ph., 2007, "The Perpetual Calendar").
 *
 * Easter follows Isaac's 28-year / 19-year tables (matches Gregorian Easter
 * for practical years). Season boundaries follow the same markers the app
 * uses for its Calendar page.
 */

export type LitSeasonId =
  | "subara"
  | "after-nativity"
  | "denha"
  | "great-fast"
  | "easter"
  | "apostles"
  | "summer"
  | "elijah-cross"
  | "moses"
  | "dedication";

export type LitDay = {
  date: string; // YYYY-MM-DD
  seasonId: LitSeasonId;
  seasonEn: string;
  seasonSyr: string;
  week: number;
  weekdayEn: string;
  weekdaySyr: string;
  feasts: { en: string; syr: string }[];
};

export type LitSeasonRange = {
  id: LitSeasonId;
  en: string;
  syr: string;
  start: string;
  end: string;
};

export type LitYear = {
  year: number;
  easter: string;
  lentStart: string;
  pentecost: string;
  advent: string;
  seasons: LitSeasonRange[];
  feasts: { date: string; en: string; syr: string; movable?: boolean }[];
};

const WEEKDAYS_EN = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];
const WEEKDAYS_SYR = [
  "ܬܪܹܝܢܒ݁ܫܲܒܵܐ",
  "ܬ݂ܠܵܬ݂ܒ݁ܫܲܒܵܐ",
  "ܐܲܪܒܲܥܒ݁ܫܲܒܵܐ",
  "ܚܲܡܫܵܒ݁ܫܲܒܵܐ",
  "ܥܪܘܼܒ݂ܬܵܐ",
  "ܫܲܒ݁ܬ݂ܵܐ",
  "ܚܲܕ݂ܒ݁ܫܲܒܵܐ",
];

const SEASON_META: Record<
  LitSeasonId,
  { en: string; syr: string; order: number }
> = {
  subara: { en: "Annunciation", syr: "ܣܘܼܒܵܪܵܐ", order: 1 },
  "after-nativity": {
    en: "Sundays after Nativity",
    syr: "ܚܲܕ݂ܒ݁ܫܲܒܹ̈ܐ ܕܒ݂ܵܬܲܪ ܝܲܠܕܵܐ",
    order: 2,
  },
  denha: { en: "Epiphany", syr: "ܕܸܢܚܵܐ", order: 3 },
  "great-fast": { en: "Great Fast", syr: "ܨܵܘܡܵܐ ܪܲܒܵܐ", order: 4 },
  easter: { en: "Resurrection", syr: "ܩܝܵܡܬܵܐ", order: 5 },
  apostles: { en: "Apostles", syr: "ܫܠܝܼ̈ܚܹܐ", order: 6 },
  summer: { en: "Summer", syr: "ܩܲܝܛܵܐ", order: 7 },
  "elijah-cross": {
    en: "Elijah — Holy Cross",
    syr: "ܐܹܠܝܼܵܐ — ܨܠܝܼܒ݂ܵܐ",
    order: 8,
  },
  moses: { en: "Moses", syr: "ܡܘܼܫܹܐ", order: 9 },
  dedication: {
    en: "Sanctification of the Church",
    syr: "ܩܘܼܕܵܫ ܥܹܕܬܵܐ",
    order: 10,
  },
};

/** Isaac 28-year Sunday-letter cycle from 1900. */
const RJ = [
  1, 2, 3, 4, 6, 7, 1, 2, 4, 5, 6, 7, 2, 3, 4, 5, 7, 1, 2, 3, 5, 6, 7, 1, 3, 4,
  5, 6,
];
/** Leap-year adjustment keys inside the 28-year cycle. */
const BCA_KEYS = [5, 3, 1, 6, 4, 2, 7];
/** Isaac 19-year (Metonic) epact table from 1898: [first day, weekday code]. */
const IZ: Record<number, [number, number]> = {
  1: [25, 1],
  2: [13, 6],
  3: [2, 2],
  4: [22, 5],
  5: [10, 3],
  6: [30, 6],
  7: [18, 4],
  8: [7, 7],
  9: [27, 3],
  10: [15, 1],
  11: [4, 4],
  12: [24, 7],
  13: [12, 5],
  14: [1, 1],
  15: [21, 4],
  16: [9, 2],
  17: [29, 5],
  18: [17, 3],
  19: [6, 6],
};

function pad(n: number) {
  return String(n).padStart(2, "0");
}

export function toISO(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

/** Local hour when the East Syriac liturgical day begins (evening / Ramsha). */
export const LITURGICAL_DAY_START_HOUR = 18;

/**
 * Map a civil clock time to the East Syriac liturgical calendar date.
 * The day begins at 18:00 local time, so Saturday evening is already Sunday.
 */
export function toLiturgicalDate(d: Date = new Date()): Date {
  const x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  if (d.getHours() >= LITURGICAL_DAY_START_HOUR) {
    x.setDate(x.getDate() + 1);
  }
  return x;
}

export function isLiturgicalEvening(d: Date = new Date()): boolean {
  return d.getHours() >= LITURGICAL_DAY_START_HOUR;
}

/** Liturgical calendar date for “now” as YYYY-MM-DD. */
export function liturgicalTodayIso(now: Date = new Date()): string {
  return toISO(toLiturgicalDate(now));
}

function parseISO(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function addDays(d: Date, n: number): Date {
  const x = new Date(d);
  x.setDate(x.getDate() + n);
  return x;
}

function isLeap(y: number) {
  return y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
}

/** Gregorian (Western) Easter — Chaldean / hudra.org civil calendar. */
export function westernEaster(year: number): Date {
  const a = year % 19;
  const b = Math.floor(year / 100);
  const c = year % 100;
  const d = Math.floor(b / 4);
  const e = b % 4;
  const f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4);
  const k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31);
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  return new Date(year, month - 1, day);
}

/**
 * Isaac perpetual-calendar Easter (hudra.org). Falls back to Western on the
 * two known edge years in 1901–2099.
 */
export function isaacEaster(year: number): Date {
  let s = Math.abs(year - 1900);
  while (s > 0 && s - 28 > 0) s -= 28;
  let sundayLetter: number;
  let leapAdj = 0;
  if (s === 0) sundayLetter = RJ[0];
  else if (s % 4 === 0) {
    sundayLetter = RJ[s - 1];
    leapAdj = BCA_KEYS[s / 4 - 1];
  } else sundayLetter = RJ[s - 1];

  let p = Math.abs(year - 1898);
  while (p > 0 && p - 19 > 0) p -= 19;
  if (p === 0) p = 1;
  const [first, last] = IZ[p];

  const o = leapAdj !== 0 ? last + leapAdj : last + sundayLetter;
  const n = o > 7 ? o - 7 : o;

  let month: number;
  let day: number;
  if (n === 7) {
    month = first < 20 ? 4 : 3;
    let m = (first === 17 || first === 18 ? 1 : 8) + first;
    if (m > 31) {
      month = 4;
      day = m - 31;
    } else day = m;
  } else {
    const l = ({ 1: 7, 2: 6, 3: 5, 4: 4, 5: 3, 6: 2, 7: 1 } as Record<
      number,
      number
    >)[n] ?? 0;
    const m = l + first;
    month = first < 20 ? 4 : 3;
    if (m > 31) {
      month = 4;
      day = m - 31;
    } else day = m;
  }

  const isaac = new Date(year, month - 1, day);
  const western = westernEaster(year);
  // Prefer Western when Isaac drifts (1994, 2089).
  if (isaac.getTime() !== western.getTime()) return western;
  return isaac;
}

/** n-th weekday on or after the day *after* `from` (hudra c1 semantics). */
function nthWeekdayAfter(from: Date, jsWeekday: number, n: number): Date {
  let cur = new Date(from);
  let count = 0;
  while (count < n) {
    cur = addDays(cur, 1);
    if (cur.getDay() === jsWeekday) count++;
  }
  return cur;
}

function firstSundayOnOrAfter(d: Date): Date {
  if (d.getDay() === 0) return new Date(d);
  return nthWeekdayAfter(d, 0, 1);
}

/** Advent / Subara: Sunday between 27 Nov and 3 Dec. */
export function adventSunday(year: number): Date {
  const nov27 = new Date(year, 10, 27);
  let sun = firstSundayOnOrAfter(nov27);
  if (sun > new Date(year, 11, 3)) sun = addDays(sun, -7);
  return sun;
}

/**
 * Great Fast Monday — 48 days before Easter (7 weeks), matching East Syriac
 * practice used alongside Isaac Easter in hudra.org.
 */
export function lentMonday(easter: Date): Date {
  return addDays(easter, -48);
}

function holyCrossSunday(year: number): Date {
  return firstSundayOnOrAfter(new Date(year, 8, 14));
}

function dedicationSunday(year: number): Date {
  // Four Sundays before Advent (Sanctification of the Church).
  return addDays(adventSunday(year), -28);
}

const FIXED_FEASTS: { m: number; d: number; en: string }[] = [
  { m: 1, d: 1, en: "Circumcision of the Lord" },
  { m: 1, d: 6, en: "Solemnity of Epiphany" },
  { m: 2, d: 2, en: "Entrance of Jesus to the Temple" },
  { m: 3, d: 19, en: "Feast of Saint Joseph" },
  { m: 3, d: 25, en: "Annunciation of the Virgin Mary" },
  { m: 6, d: 29, en: "Saints Peter and Paul" },
  { m: 7, d: 3, en: "Saint Thomas the Apostle" },
  { m: 8, d: 6, en: "Transfiguration" },
  { m: 8, d: 15, en: "Assumption of the Virgin Mary" },
  { m: 9, d: 8, en: "Nativity of the Virgin Mary" },
  { m: 9, d: 14, en: "Solemnity of the Holy Cross" },
  { m: 12, d: 6, en: "Saint Nicolas" },
  { m: 12, d: 8, en: "Immaculate Conception" },
  { m: 12, d: 25, en: "Nativity of the Lord" },
  { m: 12, d: 26, en: "Glorification of the Virgin Mary" },
  { m: 12, d: 27, en: "Holy Innocents" },
];

function buildSeasonRanges(year: number, easter: Date): LitSeasonRange[] {
  const advent = adventSunday(year);
  const xmas = new Date(year, 11, 25);
  const denhaStart = firstSundayOnOrAfter(new Date(year, 0, 6));
  const lent = lentMonday(easter);
  const pentecost = nthWeekdayAfter(easter, 0, 7);
  const summer = addDays(pentecost, 49); // 7th Sunday after Pentecost
  const cross = holyCrossSunday(year);
  const dedication = dedicationSunday(year);
  // Moses: ~4 weeks before Dedication
  const moses = addDays(dedication, -28);
  // Elijah starts at Cross Sunday (or a few weeks before if summer runs long)
  const eliyah = cross < summer ? summer : cross;

  const endOf = (start: Date, next: Date) => addDays(next, -1);

  // Cross-year: Subara spans into next year's early weeks via after-nativity.
  // For a civil year view we clip ranges to the year.
  const yStart = new Date(year, 0, 1);
  const yEnd = new Date(year, 11, 31);

  const raw: { id: LitSeasonId; start: Date; end: Date }[] = [
    { id: "denha", start: denhaStart, end: endOf(denhaStart, lent) },
    { id: "great-fast", start: lent, end: endOf(lent, easter) },
    { id: "easter", start: easter, end: endOf(easter, pentecost) },
    { id: "apostles", start: pentecost, end: endOf(pentecost, summer) },
    { id: "summer", start: summer, end: endOf(summer, eliyah) },
    { id: "elijah-cross", start: eliyah, end: endOf(eliyah, moses) },
    { id: "moses", start: moses, end: endOf(moses, dedication) },
    { id: "dedication", start: dedication, end: endOf(dedication, advent) },
    { id: "subara", start: advent, end: endOf(advent, xmas) },
    {
      id: "after-nativity",
      start: xmas,
      end: new Date(year, 11, 31),
    },
  ];

  // Early January before Denha is still after-nativity / Christmas season.
  raw.push({
    id: "after-nativity",
    start: yStart,
    end: endOf(yStart, denhaStart),
  });

  return raw
    .map((r) => {
      const start = r.start < yStart ? yStart : r.start;
      const end = r.end > yEnd ? yEnd : r.end;
      if (end < start) return null;
      const meta = SEASON_META[r.id];
      return {
        id: r.id,
        en: meta.en,
        syr: meta.syr,
        start: toISO(start),
        end: toISO(end),
      };
    })
    .filter(Boolean)
    .sort(
      (a, b) =>
        a!.start.localeCompare(b!.start) ||
        SEASON_META[a!.id].order - SEASON_META[b!.id].order,
    ) as LitSeasonRange[];
}

export function buildLiturgicalYear(year: number): LitYear {
  const easter = isaacEaster(year);
  const lent = lentMonday(easter);
  const pentecost = nthWeekdayAfter(easter, 0, 7);
  const advent = adventSunday(year);
  const seasons = buildSeasonRanges(year, easter);

  const feasts: LitYear["feasts"] = FIXED_FEASTS.map((f) => ({
    date: toISO(new Date(year, f.m - 1, f.d)),
    en: f.en,
    syr: "",
  }));

  // Movable feasts from Easter (hudra.org calendar) — English labels only;
  // Syriac feast titles come from the prayer corpus when browsing seasons.
  const movable: { offset: number; en: string }[] = [
    { offset: -48, en: "Beginning of the Great Fast" },
    { offset: -20, en: "Baʿutha of the Ninevites (day 1)" },
    { offset: -19, en: "Baʿutha of the Ninevites (day 2)" },
    { offset: -18, en: "Baʿutha of the Ninevites (day 3)" },
    { offset: -7, en: "Hosanna Sunday" },
    { offset: -3, en: "Passover Thursday" },
    { offset: -2, en: "Friday of the Passion" },
    { offset: -1, en: "Great Saturday" },
    { offset: 0, en: "Great Sunday of the Resurrection" },
    { offset: 39, en: "Ascension" },
    { offset: 49, en: "Pentecost" },
    { offset: 50, en: "Golden Friday" },
  ];
  for (const m of movable) {
    feasts.push({
      date: toISO(addDays(easter, m.offset)),
      en: m.en,
      syr: "",
      movable: true,
    });
  }

  feasts.sort((a, b) => a.date.localeCompare(b.date));

  return {
    year,
    easter: toISO(easter),
    lentStart: toISO(lent),
    pentecost: toISO(pentecost),
    advent: toISO(advent),
    seasons,
    feasts,
  };
}

function seasonForDate(iso: string, seasons: LitSeasonRange[]): LitSeasonRange {
  const hits = seasons.filter((s) => s.start <= iso && iso <= s.end);
  if (hits.length === 0) {
    return {
      id: "denha",
      en: SEASON_META.denha.en,
      syr: SEASON_META.denha.syr,
      start: iso,
      end: iso,
    };
  }
  // Prefer more specific / later-starting range when overlapping.
  hits.sort((a, b) => b.start.localeCompare(a.start));
  return hits[0];
}

function weekInSeason(iso: string, seasonStart: string): number {
  const a = parseISO(seasonStart);
  const b = parseISO(iso);
  const days = Math.round((b.getTime() - a.getTime()) / 86400000);
  return Math.floor(days / 7) + 1;
}

export function getLiturgicalDay(d: Date = new Date()): LitDay {
  // Date-only values (midnight) stay put; clock times after 18:00 roll forward.
  const litDate = toLiturgicalDate(d);
  const iso = toISO(litDate);
  const year = litDate.getFullYear();
  const lit = buildLiturgicalYear(year);
  // Also consider previous year Advent spilling — already clipped.
  const season = seasonForDate(iso, lit.seasons);
  const feasts = lit.feasts
    .filter((f) => f.date === iso)
    .map((f) => ({ en: f.en, syr: f.syr }));
  const wd = (litDate.getDay() + 6) % 7; // Mon=0
  return {
    date: iso,
    seasonId: season.id,
    seasonEn: season.en,
    seasonSyr: season.syr,
    week: weekInSeason(iso, season.start),
    weekdayEn: WEEKDAYS_EN[wd],
    weekdaySyr: WEEKDAYS_SYR[wd],
    feasts,
  };
}

export function daysInMonth(year: number, monthIndex: number): LitDay[] {
  const lit = buildLiturgicalYear(year);
  const last = new Date(year, monthIndex + 1, 0).getDate();
  const out: LitDay[] = [];
  for (let day = 1; day <= last; day++) {
    const d = new Date(year, monthIndex, day);
    const iso = toISO(d);
    const season = seasonForDate(iso, lit.seasons);
    const feasts = lit.feasts
      .filter((f) => f.date === iso)
      .map((f) => ({ en: f.en, syr: f.syr }));
    const wd = (d.getDay() + 6) % 7;
    out.push({
      date: iso,
      seasonId: season.id,
      seasonEn: season.en,
      seasonSyr: season.syr,
      week: weekInSeason(iso, season.start),
      weekdayEn: WEEKDAYS_EN[wd],
      weekdaySyr: WEEKDAYS_SYR[wd],
      feasts,
    });
  }
  return out;
}

export { SEASON_META };
