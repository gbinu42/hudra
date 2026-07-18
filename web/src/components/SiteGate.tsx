"use client";

import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";

const STORAGE_KEY = "hudra.siteUnlocked";
const PASSWORD = "marthoma";

export function SiteGate({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [unlocked, setUnlocked] = useState(false);
  const [value, setValue] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    try {
      setUnlocked(sessionStorage.getItem(STORAGE_KEY) === "1");
    } catch {
      /* ignore */
    }
    setReady(true);
  }, []);

  const unlock = useCallback((password: string) => {
    if (password === PASSWORD) {
      try {
        sessionStorage.setItem(STORAGE_KEY, "1");
      } catch {
        /* ignore */
      }
      setUnlocked(true);
      setError(false);
      return true;
    }
    setError(true);
    return false;
  }, []);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    unlock(value.trim());
  }

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-paper text-ink-soft">
        <p className="text-sm tracking-wide">Loading…</p>
      </div>
    );
  }

  if (!unlocked) {
    return (
      <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-5">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_50%_20%,rgba(26,95,106,0.14),transparent_55%)]" />
        <form
          onSubmit={onSubmit}
          className="relative w-full max-w-sm border border-line bg-paper/80 p-8 backdrop-blur-sm"
        >
          <p
            className="text-xs tracking-[0.22em] text-gold uppercase"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            Hudra
          </p>
          <p className="syr syr-block mt-4 text-4xl leading-none text-teal-deep">
            ܚܘܼܕܪܵܐ
          </p>
          <p className="mt-4 text-sm leading-relaxed text-ink-soft">
            Enter the password to continue.
          </p>
          <label className="mt-6 block">
            <span className="sr-only">Password</span>
            <input
              type="password"
              autoComplete="current-password"
              value={value}
              onChange={(e) => {
                setValue(e.target.value);
                setError(false);
              }}
              className="w-full rounded-sm border border-line bg-paper px-3 py-2.5 text-base text-ink outline-none ring-teal/30 focus:ring-2"
              placeholder="Password"
              autoFocus
            />
          </label>
          {error ? (
            <p className="mt-2 text-sm text-teal-deep">Incorrect password.</p>
          ) : null}
          <button
            type="submit"
            className="mt-5 w-full rounded-sm bg-teal-deep px-4 py-2.5 text-sm tracking-wide text-white transition hover:bg-teal"
            style={{
              fontFamily: "var(--font-display), Georgia, serif",
              color: "#fff",
            }}
          >
            Enter
          </button>
        </form>
      </div>
    );
  }

  return <>{children}</>;
}
