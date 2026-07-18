#!/usr/bin/env node
/**
 * Copy corpus data into public/ so the static export can serve prayer JSON
 * under web/out for GitHub Pages.
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.join(__dirname, "..");
const repoRoot = path.join(webRoot, "..");
const publicData = path.join(webRoot, "public", "data");
const prayersSrc = path.join(repoRoot, "data", "prayers");
const catalogSrc = path.join(webRoot, "data", "catalog.json");
const prayersDest = path.join(publicData, "prayers");

fs.mkdirSync(publicData, { recursive: true });

if (!fs.existsSync(catalogSrc)) {
  console.error("Missing", catalogSrc);
  process.exit(1);
}
fs.copyFileSync(catalogSrc, path.join(publicData, "catalog.json"));
console.log("Copied catalog.json");

if (!fs.existsSync(prayersSrc)) {
  console.error("Missing", prayersSrc);
  process.exit(1);
}

fs.rmSync(prayersDest, { recursive: true, force: true });
// Always copy so GitHub Pages artifacts include real files (no broken symlinks).
console.log("Copying prayers (this may take a minute)…");
fs.cpSync(prayersSrc, prayersDest, { recursive: true });
console.log("Copied prayers");

fs.writeFileSync(path.join(webRoot, "public", ".nojekyll"), "");
console.log("Wrote public/.nojekyll");
