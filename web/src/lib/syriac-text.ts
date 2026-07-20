/** True for empty / placeholder Syriac season labels. */
export function isPlaceholderSyriac(s: string | undefined | null): boolean {
  if (!s || s === "—") return true;
  const bare = s.replace(/[\u0730-\u074A\u0308\u0323\u032E\u0307]/g, "");
  return bare === "ܠܐ ܝܕܝܥܐ";
}

const RISH = "\u072a";
const DOTLESS_RISH = "\u0716";
const SYAME = "\u0308";

/**
 * Meltho East Syriac Adiabene mis-stacks syame + vowel on dotted ܪ.
 * Use the Meltho plural-rish carrier ܖ when syame is present (display only).
 */
export function adiabenePluralRish(text: string): string {
  if (!text || !text.includes(RISH) || !text.includes(SYAME)) return text;

  let out = "";
  let i = 0;
  const n = text.length;
  while (i < n) {
    const ch = text[i];
    if (ch === RISH) {
      let j = i + 1;
      let marks = "";
      let hasSyame = false;
      while (j < n) {
        const cat = text[j].charCodeAt(0);
        // Combining marks: Mn/Mc/Me — Syriac + generic
        const c = text[j];
        const code = c.charCodeAt(0);
        const isMark =
          (code >= 0x0300 && code <= 0x036f) ||
          (code >= 0x0730 && code <= 0x074a) ||
          code === 0x0323 ||
          code === 0x032e;
        if (!isMark) break;
        if (c === SYAME) hasSyame = true;
        marks += c;
        j++;
      }
      out += (hasSyame ? DOTLESS_RISH : RISH) + marks;
      i = j;
    } else {
      out += ch;
      i++;
    }
  }
  return out;
}
