"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  applySyriacPrefs,
  DEFAULT_SYRIAC_FONT,
  DEFAULT_SYRIAC_SIZE,
  isSyriacFontId,
  isSyriacSizeId,
  SYRIAC_FONT_KEY,
  SYRIAC_FONTS,
  SYRIAC_SIZE_KEY,
  SYRIAC_SIZES,
  type SyriacFontId,
  type SyriacSizeId,
} from "@/lib/syriac-prefs";
import { adiabenePluralRish } from "@/lib/syriac-text";

type Prefs = {
  fontId: SyriacFontId;
  sizeId: SyriacSizeId;
  setFontId: (id: SyriacFontId) => void;
  setSizeId: (id: SyriacSizeId) => void;
};

const PrefsContext = createContext<Prefs | null>(null);

function readStoredFont(): SyriacFontId {
  try {
    const v = localStorage.getItem(SYRIAC_FONT_KEY);
    if (v && isSyriacFontId(v)) return v;
  } catch {
    /* ignore */
  }
  return DEFAULT_SYRIAC_FONT;
}

function readStoredSize(): SyriacSizeId {
  try {
    const v = localStorage.getItem(SYRIAC_SIZE_KEY);
    if (v && isSyriacSizeId(v)) return v;
  } catch {
    /* ignore */
  }
  return DEFAULT_SYRIAC_SIZE;
}

export function SyriacPrefsProvider({ children }: { children: ReactNode }) {
  const [fontId, setFontIdState] = useState<SyriacFontId>(DEFAULT_SYRIAC_FONT);
  const [sizeId, setSizeIdState] = useState<SyriacSizeId>(DEFAULT_SYRIAC_SIZE);

  useEffect(() => {
    const font = readStoredFont();
    const size = readStoredSize();
    setFontIdState(font);
    setSizeIdState(size);
    applySyriacPrefs(font, size);
  }, []);

  useEffect(() => {
    applySyriacPrefs(fontId, sizeId);
  }, [fontId, sizeId]);

  const setFontId = useCallback((id: SyriacFontId) => {
    setFontIdState(id);
    try {
      localStorage.setItem(SYRIAC_FONT_KEY, id);
    } catch {
      /* ignore */
    }
  }, []);

  const setSizeId = useCallback((id: SyriacSizeId) => {
    setSizeIdState(id);
    try {
      localStorage.setItem(SYRIAC_SIZE_KEY, id);
    } catch {
      /* ignore */
    }
  }, []);

  const value = useMemo(
    () => ({ fontId, sizeId, setFontId, setSizeId }),
    [fontId, sizeId, setFontId, setSizeId],
  );

  return (
    <PrefsContext.Provider value={value}>{children}</PrefsContext.Provider>
  );
}

export function useSyriacPrefs() {
  const ctx = useContext(PrefsContext);
  if (!ctx) {
    throw new Error("useSyriacPrefs must be used within SyriacPrefsProvider");
  }
  return ctx;
}

/** Shape Syriac for the active font (Adiabene plural-rish workaround). */
export function useDisplaySyriac() {
  const { fontId } = useSyriacPrefs();
  return useCallback(
    (text: string) =>
      fontId === "adiabene" ? adiabenePluralRish(text) : text,
    [fontId],
  );
}

export function SyriacPrefsControls() {
  const { fontId, sizeId, setFontId, setSizeId } = useSyriacPrefs();

  return (
    <div className="flex min-w-0 flex-wrap items-center justify-end gap-1.5 sm:gap-3">
      <label className="flex min-w-0 items-center gap-1.5 text-xs text-ink-soft">
        <span className="sr-only">Syriac font</span>
        <select
          value={fontId}
          onChange={(e) => setFontId(e.target.value as SyriacFontId)}
          className="max-w-[9rem] cursor-pointer rounded-sm border border-line bg-paper/80 px-1.5 py-1 text-xs text-ink sm:max-w-[13.5rem]"
          aria-label="Syriac font"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          {SYRIAC_FONTS.map((f) => (
            <option key={f.id} value={f.id}>
              {f.label}
            </option>
          ))}
        </select>
      </label>

      <div
        className="flex shrink-0 items-center gap-0.5 rounded-sm border border-line bg-paper/80 p-0.5"
        role="group"
        aria-label="Syriac text size"
      >
        {SYRIAC_SIZES.map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => setSizeId(s.id)}
            className={`min-w-[1.5rem] rounded-sm px-1 py-1 text-[11px] tracking-wide transition sm:min-w-[1.75rem] sm:px-1.5 ${
              sizeId === s.id
                ? "bg-teal-deep text-paper"
                : "text-ink-soft hover:bg-paper-deep/70 hover:text-ink"
            }`}
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
            aria-pressed={sizeId === s.id}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
