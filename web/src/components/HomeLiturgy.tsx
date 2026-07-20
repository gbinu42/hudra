"use client";

import { useEffect, useState } from "react";
import { CalendarClient } from "@/components/CalendarClient";
import { TodaysPrayers } from "@/components/TodaysPrayers";
import {
  isLiturgicalEvening,
  liturgicalTodayIso,
} from "@/lib/liturgical-calendar";
import type { PrayerSummary } from "@/lib/types";

/** Calendar + day's offices on the homepage, sharing one selected liturgical day. */
export function HomeLiturgy({
  prayers,
  seasonLabels,
}: {
  prayers: PrayerSummary[];
  seasonLabels: Record<string, string>;
}) {
  const [todayIso, setTodayIso] = useState<string | null>(null);
  const [fromEvening, setFromEvening] = useState(false);
  const [iso, setIso] = useState<string | null>(null);

  useEffect(() => {
    const now = new Date();
    const t = liturgicalTodayIso(now);
    setTodayIso(t);
    setIso(t);
    setFromEvening(isLiturgicalEvening(now));
  }, []);

  if (!iso || !todayIso) {
    return (
      <section className="border-t border-line/80">
        <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8">
          <p className="text-sm text-ink-soft">Loading liturgical day…</p>
        </div>
      </section>
    );
  }

  return (
    <>
      <section className="border-t border-line/80 bg-paper/40">
        <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8">
          <CalendarClient
            prayers={prayers}
            seasonLabels={seasonLabels}
            embedded
            selected={iso}
            onSelect={setIso}
          />
        </div>
      </section>

      <TodaysPrayers
        prayers={prayers}
        seasonLabels={seasonLabels}
        iso={iso}
        todayIso={todayIso}
        fromEvening={fromEvening}
        onIsoChange={setIso}
      />
    </>
  );
}
