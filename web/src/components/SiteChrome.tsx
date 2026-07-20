import Link from "next/link";
import { HudraMark } from "@/components/HudraMark";
import { SyriacPrefsControls } from "@/components/SyriacPrefs";

const links: { href: string; label: string; short?: string }[] = [
  { href: "/browse", label: "Seasons" },
  { href: "/calendar", label: "Calendar" },
  { href: "/psalms", label: "Psalms" },
  { href: "/commemorations", label: "Commemorations", short: "Feasts" },
  { href: "/search", label: "Search" },
];

export function SiteHeader() {
  return (
    <header className="border-b border-line/80 bg-paper/55 backdrop-blur-md">
      <div className="mx-auto flex w-full max-w-6xl min-w-0 flex-col gap-3 px-4 py-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between sm:gap-x-4 sm:gap-y-3 sm:px-8 sm:py-4">
        <Link
          href="/"
          className="group flex min-w-0 items-center gap-2 sm:gap-3"
        >
          <HudraMark className="h-7 w-auto shrink-0 text-teal-deep transition group-hover:text-teal sm:h-9" />
          <span className="syr syr-inline shrink-0 text-xl leading-none text-teal-deep transition group-hover:text-teal sm:text-3xl">
            ܚܘܼܕܪܵܐ
          </span>
          <span
            className="hidden font-[family-name:var(--font-display)] text-sm tracking-[0.22em] text-gold uppercase transition group-hover:text-gold-soft sm:inline"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            Hudra
          </span>
        </Link>

        <div className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-2 sm:gap-4">
          <nav className="flex min-w-0 flex-wrap items-center gap-0.5 sm:gap-2">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className="rounded-sm px-1.5 py-1 text-xs text-ink-soft transition hover:bg-paper-deep/70 hover:text-ink sm:px-3 sm:py-1.5 sm:text-sm"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                {l.short ? (
                  <>
                    <span className="sm:hidden">{l.short}</span>
                    <span className="hidden sm:inline">{l.label}</span>
                  </>
                ) : (
                  l.label
                )}
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
        <p>Syriac text of the East Syriac Hudra</p>
      </div>
    </footer>
  );
}
