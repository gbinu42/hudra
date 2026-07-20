"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";

/** Reset window scroll on client navigations (e.g. psalm prev/next). */
export function ScrollToTop() {
  const pathname = usePathname();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}
