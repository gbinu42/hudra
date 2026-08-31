import { depointSyriac } from "@/lib/depoint-syriac";
import type { QankaRazaEdition, QankaRazaHymn, QankaRazaOccasion } from "@/lib/qanka-raza";

/** Recitation / psalm cues that often precede the onitha itself. */
const CUES = new Set([
  "ܒܠܟܘ",
  "ܩܪܝܢܢ",
  "ܫܒܚ",
  "ܬܢܝ",
  "ܥܠܡ",
  "ܪܫ",
  "ܩܠܐ",
  "ܪܫܩܠܐ",
  "ܕܩܢܟܐ",
  "ܕܩܢܟ",
  "ܕܐܪܙܐ",
  "ܕܐܪܙ",
  "ܥܘܢܝܬܐ",
  "ܥܘܢܝܐ",
  "ܐܩܦܬܐ",
  "ܡܙܡܘܪܐ",
]);

function hymnTokens(text: string): string[] {
  const bare = depointSyriac(text)
    .replace(/<[^>]+>/g, " ")
    .replace(/[\u0700-\u070d.:;*·()[\]،؛?!«»"'/\-–—|\\]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  let tokens = bare.split(" ").filter(Boolean);
  while (tokens.length && CUES.has(tokens[0])) {
    tokens = tokens.slice(1);
  }
  if (tokens[0]?.startsWith("ܒ") && tokens[0].length > 2) {
    tokens = [tokens[0].slice(1), ...tokens.slice(1)];
  }
  return tokens;
}

function jaccard(a: string[], b: string[]): number {
  const A = new Set(a);
  const B = new Set(b);
  if (!A.size && !B.size) return 1;
  if (!A.size || !B.size) return 0;
  let share = 0;
  for (const x of A) if (B.has(x)) share += 1;
  return share / (A.size + B.size - share);
}

function headOverlap(a: string[], b: string[], n = 8): number {
  const A = new Set(a.slice(0, n));
  const B = new Set(b.slice(0, n));
  if (!A.size || !B.size) return 0;
  let share = 0;
  for (const x of A) if (B.has(x)) share += 1;
  return share / Math.max(A.size, B.size);
}

/** True when the two recensions are not the same onitha (ignore pointing / psalm cues). */
export function hymnsDifferMajorly(
  a: QankaRazaHymn | null | undefined,
  b: QankaRazaHymn | null | undefined,
): boolean {
  if (!a?.text || !b?.text) return false;
  const ta = hymnTokens(a.text);
  const tb = hymnTokens(b.text);
  if (ta.length < 4 || tb.length < 4) return false;
  return headOverlap(ta, tb) < 0.4 && jaccard(ta, tb) < 0.45;
}

function pairFor(
  kind: "qanka" | "raza",
  syriac: QankaRazaEdition | null,
  chaldean: QankaRazaEdition | null,
): boolean {
  return hymnsDifferMajorly(
    kind === "qanka" ? syriac?.qanka : syriac?.raza,
    kind === "qanka" ? chaldean?.qanka : chaldean?.raza,
  );
}

export function occasionHasMajorDiff(o: QankaRazaOccasion): boolean {
  return (
    pairFor("qanka", o.syriac, o.chaldean) ||
    pairFor("raza", o.syriac, o.chaldean)
  );
}
