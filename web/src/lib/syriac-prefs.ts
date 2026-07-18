export const SYRIAC_FONTS = [
  {
    id: "adiabene",
    family: "East Syriac Adiabene",
    label: "East Syriac Adiabene",
  },
  {
    id: "ctesiphon",
    family: "East Syriac Ctesiphon",
    label: "East Syriac Ctesiphon",
  },
  { id: "ramsina", family: "Ramsina", label: "Ramsina" },
  { id: "idiqlat", family: "Idiqlat", label: "Idiqlat" },
  {
    id: "malankara-classical",
    family: "East Syriac Malankara Classical",
    label: "East Syriac Malankara Classical",
  },
  {
    id: "malankara",
    family: "East Syriac Malankara",
    label: "East Syriac Malankara",
  },
] as const;

export type SyriacFontId = (typeof SYRIAC_FONTS)[number]["id"];

/** Relative scale applied to Syriac UI + prayer body. */
export const SYRIAC_SIZES = [
  { id: "sm", label: "S", scale: 0.9 },
  { id: "md", label: "M", scale: 1 },
  { id: "lg", label: "L", scale: 1.15 },
  { id: "xl", label: "XL", scale: 1.3 },
] as const;

export type SyriacSizeId = (typeof SYRIAC_SIZES)[number]["id"];

export const DEFAULT_SYRIAC_FONT: SyriacFontId = "adiabene";
export const DEFAULT_SYRIAC_SIZE: SyriacSizeId = "md";

export const SYRIAC_FONT_KEY = "hudra.syriacFont";
export const SYRIAC_SIZE_KEY = "hudra.syriacSize";

export function fontFamilyForId(id: string): string {
  return (
    SYRIAC_FONTS.find((f) => f.id === id)?.family ??
    SYRIAC_FONTS[0].family
  );
}

export function sizeScaleForId(id: string): number {
  return SYRIAC_SIZES.find((s) => s.id === id)?.scale ?? 1;
}

export function isSyriacFontId(id: string): id is SyriacFontId {
  return SYRIAC_FONTS.some((f) => f.id === id);
}

export function isSyriacSizeId(id: string): id is SyriacSizeId {
  return SYRIAC_SIZES.some((s) => s.id === id);
}

/** Apply prefs to <html> for CSS variables. */
export function applySyriacPrefs(fontId: string, sizeId: string) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.style.setProperty("--font-syriac", `"${fontFamilyForId(fontId)}", serif`);
  root.style.setProperty("--syr-scale", String(sizeScaleForId(sizeId)));
  root.dataset.syrFont = fontId;
  root.dataset.syrSize = sizeId;
}
