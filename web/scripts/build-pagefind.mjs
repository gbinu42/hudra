#!/usr/bin/env node
/**
 * Build a Pagefind index from prayer + psalm JSON (depointed full text).
 * Bodies are fetched client-side on prayer pages, so HTML crawl is not enough.
 *
 * Usage:
 *   node scripts/build-pagefind.mjs           # writes web/out/pagefind
 *   node scripts/build-pagefind.mjs --dev     # writes web/public/pagefind (for next dev)
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import * as pagefind from "pagefind";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.join(__dirname, "..");
const repoRoot = path.join(webRoot, "..");
const catalogPath = path.join(webRoot, "data", "catalog.json");
const prayersDir = path.join(repoRoot, "data", "prayers");
const psalmsDir = path.join(repoRoot, "data", "psalms");

const dev = process.argv.includes("--dev");
const outputPath = path.join(
  webRoot,
  dev ? "public" : "out",
  "pagefind",
);

/** Keep in sync with web/src/lib/depoint-syriac.ts */
function depointSyriac(s) {
  return String(s || "")
    .replace(/[\u0730-\u074A\u0308\u0323\u032E\u0307]/g, "")
    .replace(/[\u200e\u200f\u200c\u200d\ufeff]/g, "");
}

function traditionLabel(t) {
  if (t === "syriac") return "assyrian syriac";
  if (t === "chaldean") return "chaldean";
  return t;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

async function main() {
  if (!fs.existsSync(catalogPath)) {
    console.error("Missing catalog:", catalogPath);
    process.exit(1);
  }
  if (!dev && !fs.existsSync(path.join(webRoot, "out"))) {
    console.error("Missing web/out — run next build first, or use --dev");
    process.exit(1);
  }

  const catalog = readJson(catalogPath);
  const prayers = catalog.prayers || [];
  const psalms = catalog.psalms || [];

  console.log(
    `Indexing ${prayers.length} prayers + ${psalms.length} psalms → ${outputPath}`,
  );

  const { index } = await pagefind.createIndex({
    forceLanguage: "en",
    verbose: false,
  });

  let ok = 0;
  let failed = 0;

  for (let i = 0; i < prayers.length; i++) {
    const summary = prayers[i];
    const file = path.join(prayersDir, `${summary.id}.json`);
    if (!fs.existsSync(file)) {
      failed++;
      continue;
    }
    const record = readJson(file);
    const tradition = (summary.tradition || []).map(traditionLabel).join(" ");
    const metaBits = [
      summary.name,
      summary.holiday,
      summary.holidayEn,
      summary.week,
      summary.day,
      summary.dayEn,
      summary.hour,
      summary.hourEn,
      tradition,
      "prayer",
    ]
      .filter(Boolean)
      .join("\n");

    const content = depointSyriac(`${metaBits}\n${record.text || ""}`);
    const subtitle = [
      summary.holidayEn || summary.holiday,
      summary.hourEn || summary.hour,
      summary.dayEn || summary.day,
      summary.week,
    ]
      .filter(Boolean)
      .join(" · ");

    const { errors } = await index.addCustomRecord({
      url: `/prayer/${summary.id}/`,
      content,
      language: "en",
      meta: {
        title: summary.name || "Prayer",
        kind: "prayer",
        subtitle,
        tradition: (summary.tradition || []).join(","),
      },
      filters: {
        kind: ["prayer"],
        tradition: summary.tradition?.length
          ? summary.tradition
          : ["unspecified"],
      },
    });

    if (errors?.length) {
      failed++;
      if (failed <= 5) console.warn(summary.id, errors);
    } else {
      ok++;
    }

    if ((i + 1) % 500 === 0) {
      console.log(`  …prayers ${i + 1}/${prayers.length}`);
    }
  }

  for (const summary of psalms) {
    const file = path.join(psalmsDir, `${summary.id}.json`);
    if (!fs.existsSync(file)) {
      failed++;
      continue;
    }
    const record = readJson(file);
    const numLabel =
      summary.number > 0
        ? summary.number >= 11801 && summary.number <= 11822
          ? `Psalm 118 ${summary.number - 11800}`
          : `Psalm ${summary.number}`
        : "Psalm opening";
    const content = depointSyriac(
      `${summary.name}\n${numLabel}\npsalm\n${record.text || ""}`,
    );
    const { errors } = await index.addCustomRecord({
      url: `/psalm/${summary.id}/`,
      content,
      language: "en",
      meta: {
        title: summary.name || numLabel,
        kind: "psalm",
        subtitle: numLabel,
        tradition: "",
      },
      filters: {
        kind: ["psalm"],
      },
    });
    if (errors?.length) {
      failed++;
      if (failed <= 5) console.warn(summary.id, errors);
    } else {
      ok++;
    }
  }

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  const { errors: writeErrors } = await index.writeFiles({ outputPath });
  if (writeErrors?.length) {
    console.error("writeFiles errors:", writeErrors);
    process.exit(1);
  }

  await pagefind.close();

  // Size report
  let bytes = 0;
  const walk = (dir) => {
    for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, ent.name);
      if (ent.isDirectory()) walk(p);
      else bytes += fs.statSync(p).size;
    }
  };
  walk(outputPath);

  console.log(
    `Done: ${ok} records indexed (${failed} skipped). Bundle ${(bytes / 1e6).toFixed(2)} MB → ${outputPath}`,
  );
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
