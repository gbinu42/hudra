export interface QankaRazaHymn {
  text: string;
  /** Vocalized body with <span class="rubric"> for red cues. */
  html?: string;
  incipit: string;
}

export interface QankaRazaEdition {
  id: string;
  name: string;
  qanka: QankaRazaHymn | null;
  raza: QankaRazaHymn | null;
}

export interface QankaRazaOccasion {
  seasonId: string;
  week: string;
  day: string;
  dayEn: string;
  dayOrder: number;
  holiday: string;
  holidayEn: string;
  name: string;
  seasonSyriac: string;
  seasonEnglish: string;
  seasonGroup: string;
  seasonOrder: number;
  syriac: QankaRazaEdition | null;
  chaldean: QankaRazaEdition | null;
}

export interface QankaRazaSeason {
  id: string;
  syriac: string;
  english: string;
  group: string;
  order: number;
}

export interface QankaRazaCatalog {
  counts: {
    occasions: number;
    paired: number;
    qanka: number;
    raza: number;
  };
  seasons: QankaRazaSeason[];
  occasions: QankaRazaOccasion[];
}
