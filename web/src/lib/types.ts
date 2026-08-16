export type Tradition = "syriac" | "chaldean" | "unspecified";

export type SeasonGroup = "cycle" | "commemoration" | "feast" | "baotha" | "other";

export interface Season {
  id: string;
  syriac: string;
  english: string;
  description: string;
  order: number;
  group: SeasonGroup;
  sourceHoliday: string;
  count: number;
}

export interface HourMeta {
  syriac: string;
  english: string;
  order: number;
}

export interface DayMeta {
  syriac: string;
  english: string;
  order: number;
}

export interface PrayerSummary {
  id: string;
  name: string;
  holiday: string;
  /** English feast / dukrana title when known. */
  holidayEn?: string;
  seasonId: string;
  week: string;
  day: string;
  dayEn: string;
  hour: string;
  hourEn: string;
  hourOrder: number;
  dayOrder: number;
  tradition: Tradition[];
  chars: number;
}

export interface PsalmSummary {
  id: string;
  name: string;
  number: number;
  order: number;
  chars: number;
}

export interface Catalog {
  source?: string;
  counts: {
    prayers: number;
    seasons: number;
    syriac: number;
    chaldean: number;
    psalms: number;
  };
  hours: HourMeta[];
  days: DayMeta[];
  seasons: Season[];
  prayers: PrayerSummary[];
  psalms: PsalmSummary[];
}

export interface PrayerRecord {
  itemId: string;
  itemName: string;
  itemRelatedHoliday: string;
  week: string;
  day: string;
  prayerTime: string;
  tradition: Tradition[];
  text: string;
  /** Colored HTML from Quill (rubrics, alignments). */
  html?: string;
  source?: string;
}

export interface PsalmRecord {
  itemId: string;
  itemName: string;
  number: number;
  numberRaw?: string;
  order: number;
  text: string;
  html?: string;
  source?: string;
}
