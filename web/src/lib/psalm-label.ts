import type { PsalmSummary } from "./types";

/** Psalm 118 is stored as 22 alphabetical sections (11801–11822). */
export function isPsalm118Section(number: number): boolean {
  return number >= 11801 && number <= 11822;
}

export function psalmDisplayNumber(number: number): string {
  if (isPsalm118Section(number)) {
    return `118 · ${number - 11800}`;
  }
  if (number > 0) return String(number);
  return "";
}

/**
 * Sort so 118's letter-sections sit between 117 and 119
 * (API stores them as 11801–11822 at the end of the list).
 */
export function psalmSortKey(number: number): [number, number] {
  if (isPsalm118Section(number)) {
    return [118, number - 11800];
  }
  return [number, 0];
}

export function comparePsalms(
  a: { number: number; name?: string },
  b: { number: number; name?: string },
): number {
  const [aMajor, aMinor] = psalmSortKey(a.number);
  const [bMajor, bMinor] = psalmSortKey(b.number);
  if (aMajor !== bMajor) return aMajor - bMajor;
  if (aMinor !== bMinor) return aMinor - bMinor;
  return (a.name || "").localeCompare(b.name || "", "syr");
}

/** English list / heading label for a psalm catalog entry. */
export function psalmEnglishName(p: PsalmSummary): string {
  if (p.number <= 0) return "Opening";
  if (isPsalm118Section(p.number)) {
    return `Psalm 118 · ${p.number - 11800}`;
  }
  if (p.number >= 1 && p.number <= 150) {
    return `Psalm ${p.number}`;
  }
  if (p.number > 150) {
    return `Canticle ${p.number}`;
  }
  return psalmDisplayNumber(p.number) || "Psalm";
}

export function psalmListLabel(p: PsalmSummary): string {
  return psalmEnglishName(p);
}

export function psalmMatchesQuery(p: PsalmSummary, needle: string): boolean {
  const q = needle.trim().toLowerCase();
  if (!q) return false;
  if (String(p.number) === q) return true;
  if (p.name.includes(needle.trim())) return true;
  const english = psalmEnglishName(p).toLowerCase();
  if (english.includes(q)) return true;
  const display = psalmDisplayNumber(p.number).toLowerCase();
  if (display && display.includes(q)) return true;
  if (q === "118" && isPsalm118Section(p.number)) return true;
  const hay = `${p.name} psalm ${p.number} mazmora ${display} ${english}`.toLowerCase();
  return hay.includes(q);
}
