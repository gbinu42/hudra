import Link from "next/link";
import { SyriacPrefsControls } from "@/components/SyriacPrefs";

const links = [
  { href: "/browse", label: "Seasons" },
  { href: "/calendar", label: "Calendar" },
  { href: "/commemorations", label: "Commemorations" },
  { href: "/search", label: "Search" },
];

export function SiteHeader() {
  return (
    <header className="border-b border-line/80 bg-paper/55 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-4 gap-y-3 px-5 py-4 sm:px-8">
        <Link href="/" className="group flex items-baseline gap-3">
          <span className="syr syr-inline text-2xl leading-none text-teal-deep transition group-hover:text-teal sm:text-3xl">
            ܚܘܼܕܪܵܐ
          </span>
          <span
            className="font-[family-name:var(--font-display)] text-sm tracking-[0.22em] text-ink-soft uppercase"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            Hudra
          </span>
        </Link>
        <div className="flex flex-wrap items-center gap-3 sm:gap-4">
          <nav className="flex items-center gap-1 sm:gap-2">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className="rounded-sm px-2.5 py-1.5 text-sm text-ink-soft transition hover:bg-paper-deep/70 hover:text-ink sm:px-3"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                {l.label}
              </Link>
            ))}
          </nav>
          <SyriacPrefsControls />
        </div>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-line/80">
      <div className="mx-auto flex max-w-6xl flex-col gap-2 px-5 py-8 text-sm text-ink-soft sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <p>
          Syriac text of the East Syriac Hudra · sourced from{" "}
          <a
            href="https://hudra.org"
            className="text-teal underline-offset-2 hover:underline"
            target="_blank"
            rel="noreferrer"
          >
            hudra.org
          </a>
        </p>
      </div>
    </footer>
  );
}
