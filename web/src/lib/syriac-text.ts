/** True for empty / placeholder Syriac season labels. */
export function isPlaceholderSyriac(s: string | undefined | null): boolean {
  if (!s || s === "—") return true;
  const bare = s.replace(/[\u0730-\u074A\u0308\u0323\u032E\u0307]/g, "");
  return bare === "ܠܐ ܝܕܝܥܐ";
}
