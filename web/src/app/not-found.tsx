import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto flex max-w-xl flex-col items-start px-5 py-24 sm:px-8">
      <h1
        className="text-3xl text-ink"
        style={{ fontFamily: "var(--font-display), Georgia, serif" }}
      >
        Not found
      </h1>
      <p className="mt-3 text-ink-soft">
        That season or prayer is not in the corpus.
      </p>
      <Link href="/browse" className="mt-6 text-teal hover:underline">
        Back to seasons
      </Link>
    </main>
  );
}
