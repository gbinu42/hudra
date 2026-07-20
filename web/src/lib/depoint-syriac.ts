/**
 * Strip East Syriac vowels / diacritics for consonant-only matching.
 * Keep in sync with scripts/build-pagefind.mjs.
 */
export function depointSyriac(s: string): string {
  return s
    .replace(/[\u0730-\u074A\u0308\u0323\u032E\u0307]/g, "")
    .replace(/[\u200e\u200f\u200c\u200d\ufeff]/g, "");
}
