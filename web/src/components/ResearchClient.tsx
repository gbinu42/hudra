"use client";

import { useMemo, useState } from "react";
import {
  CMS_LETTER_INDEX,
  CMS_LISTING,
  CMS_RECENT,
  CMS_REGISTER,
  CMS_RELATED,
  CMS_RESEARCH,
  RESEARCH_SECTIONS,
  type ResearchLang,
  type ResearchSection,
} from "@/lib/cms-research";

type LangFilter = "all" | ResearchLang;

function haystack(section: ResearchSection): string {
  const parts = [section.label, ...section.groups.flatMap((g) => [g.title, ...g.items.map((i) => i.title)])];
  return parts.join("\n").toLowerCase();
}

function filterSections(query: string, lang: LangFilter): ResearchSection[] {
  const q = query.trim().toLowerCase();
  return RESEARCH_SECTIONS.filter((s) => (lang === "all" ? true : s.id === lang))
    .map((s) => {
      if (!q) return s;
      if (haystack(s).includes(q)) {
        const groups = s.groups
          .map((g) => {
            const groupHit = g.title.toLowerCase().includes(q);
            const items = groupHit
              ? g.items
              : g.items.filter((i) => i.title.toLowerCase().includes(q));
            if (!groupHit && items.length === 0 && !g.href) return null;
            if (!groupHit && items.length === 0 && g.href && !g.title.toLowerCase().includes(q)) {
              return null;
            }
            return { ...g, items: groupHit ? g.items : items };
          })
          .filter((g) => g !== null);
        return { ...s, groups };
      }
      return { ...s, groups: [] };
    })
    .filter((s) => s.groups.length > 0);
}

function ExtLink({
  href,
  children,
  className,
}: {
  href: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <a href={href} target="_blank" rel="noreferrer" className={className}>
      {children}
    </a>
  );
}

export function ResearchClient() {
  const [query, setQuery] = useState("");
  const [lang, setLang] = useState<LangFilter>("all");

  const sections = useMemo(() => filterSections(query, lang), [query, lang]);
  const langs: { id: LangFilter; label: string }[] = [
    { id: "all", label: "All" },
    { id: "syriac", label: "Syriac" },
    { id: "malayalam", label: "Malayalam" },
    { id: "english", label: "English" },
  ];

  return (
    <div>
      <div className="mt-10 border border-line bg-paper/70 p-4 sm:p-5">
        <label className="block">
          <span
            className="mb-2 block text-xs tracking-[0.18em] text-gold uppercase"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            Filter the catalog
          </span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Grammar, Hudra, Qurbana, തക്സ…"
            className="w-full rounded-sm border border-line bg-paper/80 px-4 py-3 text-base text-ink outline-none ring-teal/30 placeholder:text-ink-soft/50 focus:ring-2"
          />
        </label>
        <div className="mt-4 flex flex-wrap gap-1.5" role="group" aria-label="Language">
          {langs.map((opt) => {
            const active = lang === opt.id;
            return (
              <button
                key={opt.id}
                type="button"
                aria-pressed={active}
                onClick={() => setLang(opt.id)}
                className={`rounded-sm border px-2.5 py-1.5 text-sm transition ${
                  active
                    ? "border-teal/50 bg-teal-deep text-white"
                    : "border-line bg-paper/80 text-ink-soft hover:border-teal/40 hover:text-ink"
                }`}
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      </div>

      {sections.length === 0 ? (
        <p className="mt-10 text-sm text-ink-soft">No matching categories.</p>
      ) : (
        <div className="mt-10 space-y-12">
          {sections.map((section) => (
            <section key={section.id}>
              <h2
                className="text-lg text-ink"
                style={{ fontFamily: "var(--font-display), Georgia, serif" }}
              >
                {section.label}
              </h2>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {section.groups.map((group) => (
                  <article
                    key={group.title}
                    className="rounded-sm border border-line bg-paper/70 px-5 py-5"
                  >
                    {group.href ? (
                      <h3
                        className="text-base text-teal-deep"
                        style={{
                          fontFamily: "var(--font-display), Georgia, serif",
                        }}
                      >
                        <ExtLink href={group.href} className="hover:text-teal">
                          {group.title}
                        </ExtLink>
                      </h3>
                    ) : (
                      <h3
                        className="text-base text-ink"
                        style={{
                          fontFamily: "var(--font-display), Georgia, serif",
                        }}
                      >
                        {group.title}
                      </h3>
                    )}
                    {group.items.length > 0 ? (
                      <ul className="mt-3 divide-y divide-line/80">
                        {group.items.map((item) => (
                          <li key={item.title}>
                            {item.href ? (
                              <ExtLink
                                href={item.href}
                                className="flex items-baseline justify-between gap-3 py-2 text-sm text-ink transition hover:text-teal-deep"
                              >
                                <span>{item.title}</span>
                                <span className="shrink-0 text-xs text-ink-soft">
                                  Open
                                </span>
                              </ExtLink>
                            ) : (
                              <span className="flex py-2 text-sm text-ink-soft/70">
                                {item.title}
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    ) : !group.href ? (
                      <p className="mt-2 text-sm text-ink-soft/60">—</p>
                    ) : null}
                  </article>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}

      <section className="mt-14">
        <h2
          className="text-lg text-ink"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          By title
        </h2>
        <p className="mt-2 max-w-xl text-sm text-ink-soft">
          The same A–Z index as the CMS catalog, without the duplicate yellow
          bars.
        </p>
        <div className="mt-4 flex flex-wrap gap-1">
          {CMS_LETTER_INDEX.map(({ letter, href }) => (
            <ExtLink
              key={letter}
              href={href}
              className="flex h-8 w-8 items-center justify-center rounded-sm border border-line bg-paper/80 text-sm text-ink-soft transition hover:border-teal/40 hover:text-ink"
            >
              {letter}
            </ExtLink>
          ))}
        </div>
      </section>

      <section className="mt-14 grid gap-4 sm:grid-cols-2">
        <article className="rounded-sm border border-line bg-paper/70 px-5 py-5">
          <p className="text-[11px] tracking-[0.14em] text-gold uppercase">
            {CMS_RECENT.range} · {CMS_RECENT.date}
          </p>
          <h3
            className="mt-2 text-base text-ink"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            Recently added
          </h3>
          <ExtLink
            href={CMS_RECENT.href}
            className="mt-3 block text-sm text-teal-deep hover:text-teal"
          >
            {CMS_RECENT.title}
          </ExtLink>
          <p className="mt-2 text-xs text-ink-soft">
            CMS marks this entry for registered users.
          </p>
        </article>
        <article className="rounded-sm border border-line bg-paper/70 px-5 py-5">
          <p className="text-[11px] tracking-[0.14em] text-gold uppercase">
            RR 1500–001
          </p>
          <h3
            className="mt-2 text-base text-ink"
            style={{ fontFamily: "var(--font-display), Georgia, serif" }}
          >
            Numbered catalog
          </h3>
          <p className="mt-3 text-sm leading-relaxed text-ink-soft">
            The full RR list lives on CMS India. Many scans require an account.
          </p>
          <div className="mt-4 flex flex-wrap gap-3 text-sm">
            <ExtLink href={CMS_LISTING} className="text-teal-deep hover:text-teal">
              Resources for Researchers List
            </ExtLink>
            <ExtLink href={CMS_REGISTER} className="text-ink-soft hover:text-ink">
              Create an account
            </ExtLink>
          </div>
        </article>
      </section>

      <section className="mt-14">
        <h2
          className="text-lg text-ink"
          style={{ fontFamily: "var(--font-display), Georgia, serif" }}
        >
          Also on CMS India
        </h2>
        <ul className="mt-4 divide-y divide-line border border-line bg-paper/60">
          {CMS_RELATED.map((item) => (
            <li key={item.href}>
              <ExtLink
                href={item.href}
                className="flex items-baseline justify-between gap-3 px-4 py-3 text-sm text-ink transition hover:bg-paper-deep/50 hover:text-teal-deep"
              >
                <span
                  style={{ fontFamily: "var(--font-display), Georgia, serif" }}
                >
                  {item.title}
                </span>
                <span className="shrink-0 text-xs text-ink-soft">Open</span>
              </ExtLink>
            </li>
          ))}
        </ul>
        <p className="mt-4 text-xs text-ink-soft">
          Source:{" "}
          <ExtLink href={CMS_RESEARCH} className="text-teal-deep hover:underline">
            thecmsindia.org/resources/resources-for-researchers
          </ExtLink>
        </p>
      </section>
    </div>
  );
}
