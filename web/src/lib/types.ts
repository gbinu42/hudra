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

export interface Catalog {
  source: string;
  counts: {
    prayers: number;
    seasons: number;
    syriac: number;
    chaldean: number;
  };
  hours: HourMeta[];
  days: DayMeta[];
  seasons: Season[];
  prayers: PrayerSummary[];
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
  source: string;
}
