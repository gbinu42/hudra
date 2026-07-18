/** Split prayer body into paragraphs for display. */
export function prayerParagraphs(text: string): string[] {
  return text
    .split(/\n+/)
    .map((p) => p.trim())
    .filter(Boolean);
}
