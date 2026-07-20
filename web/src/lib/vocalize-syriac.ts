import type { Catalog } from "./types";

const MARK_RE = /[\u0730-\u074A\u0308\u0323\u032E\u0307]/;
const MARK_STRIP_RE = /[\u0730-\u074A\u0308\u0323\u032E\u0307]/g;
const WORD_RE = /[\u0710-\u074F]+/g;
const PROCLITICS = new Set(["ܕ", "ܘ", "ܒ", "ܠ"]);

/** Strip East Syriac vowels / consonant dots for bare-letter lookup. */
export function stripSyriacMarks(s: string): string {
  return s.replace(MARK_STRIP_RE, "");
}

function hasPointing(s: string): boolean {
  return MARK_RE.test(s);
}

function remember(
  lex: Map<string, string>,
  pointed: string,
  opts?: { overwrite?: boolean; force?: boolean },
) {
  const overwrite = opts?.overwrite !== false;
  const force = opts?.force === true;
  const bare = stripSyriacMarks(pointed);
  if (!bare || bare === pointed) return;
  const prev = lex.get(bare);
  if (!prev) {
    lex.set(bare, pointed);
    return;
  }
  if (!overwrite) return;
  if (force || pointed.length >= prev.length) lex.set(bare, pointed);
}

/**
 * Build a bare→pointed lexicon from catalog metadata and already-vocalized
 * prayer titles so unpointed labels can be restored for display.
 */
export function buildVocalizeLexicon(catalog: Catalog): Map<string, string> {
  const lex = new Map<string, string>();

  // Seed common stems, then seasons/hours, then days last so weekdays win.
  for (const w of [
    "ܨܵܘܡܵܐ",
    "ܕܸܢܚܵܐ",
    "ܩܲܝܛܵܐ",
    "ܩܝܵܡܬ݂ܵܐ",
    "ܫܠܝܼܚܹ̈ܐ",
    "ܕܘܼܟܪܵܢܵܐ",
    "ܐܲܠܝܼܵܐ",
    "ܡܘܼܫܹܐ",
    "ܝܲܠܕܵܐ",
    "ܥܹܕ݂ܬ݂ܵܐ",
    "ܡܫܝܼܚܵܐ",
    "ܝܫܘܿܥ",
    "ܩܲܕܝܼܫܬ݂ܵܐ",
    "ܚܘܼܕܬ݂ܵܐ",
    "ܒܹܝܬ݂",
    "ܫܟܲܚܬ݂ܵܐ",
    "ܡܲܥܲܠܝܵܐ",
    "ܬܸܫܒܘܿܚܬ݂ܵܐ",
  ]) {
    remember(lex, w);
  }

  for (const s of catalog.seasons) {
    remember(lex, s.syriac);
    for (const part of s.syriac.split(/\s+/)) {
      remember(lex, part, { overwrite: false });
    }
  }
  for (const h of catalog.hours) {
    remember(lex, h.syriac);
    for (const part of h.syriac.split(/\s+/)) remember(lex, part);
  }
  // Weekday labels are authoritative for their bare forms.
  for (const d of catalog.days) remember(lex, d.syriac, { force: true });

  // Fill gaps from pointed prayer titles — never override catalog forms.
  for (const p of catalog.prayers) {
    if (p.week) remember(lex, p.week, { overwrite: false });
    if (p.day) remember(lex, p.day, { overwrite: false });
    if (p.hour) remember(lex, p.hour, { overwrite: false });
    if (!hasPointing(p.name)) continue;
    for (const w of p.name.match(WORD_RE) || []) {
      if (hasPointing(w)) remember(lex, w, { overwrite: false });
    }
  }

  return lex;
}

function lookupWord(lex: Map<string, string>, word: string): string {
  if (hasPointing(word)) return word;
  const bare = stripSyriacMarks(word);
  const hit = lex.get(bare);
  if (hit) return hit;

  // ܕܨܘܡܐ → ܕ + ܨܘܡܐ
  if (bare.length > 1 && PROCLITICS.has(bare[0])) {
    const rest = bare.slice(1);
    const restHit = lex.get(rest);
    if (restHit) return bare[0] + restHit;
  }
  return word;
}

/** Point unvocalized Syriac using a bare→pointed lexicon. */
export function vocalizeSyriac(
  text: string,
  lex: Map<string, string>,
): string {
  if (!text || text === "—") return text;
  return text.replace(WORD_RE, (w) => lookupWord(lex, w));
}

export function makeVocalizer(
  catalog: Catalog,
): (text: string) => string {
  const lex = buildVocalizeLexicon(catalog);
  return (text: string) => vocalizeSyriac(text, lex);
}
