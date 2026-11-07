#!/usr/bin/env node
// usage: node screenshot.js schematic.html OUTDIR [--scale 1|2] [--width 1400] [--height 900]
// Renders every cell view of the schematic to OUTDIR/<cell>.png for visual review.
const path = require("path");
const fs = require("fs");
let pw;
try { pw = require("playwright"); } catch (e) { console.error("playwright not available"); process.exit(2); }

(async () => {
  const args = process.argv.slice(2);
  const html = path.resolve(args[0]);
  const out = path.resolve(args[1] || "shots");
  const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? Number(args[i + 1]) : d; };
  fs.mkdirSync(out, { recursive: true });
  const browser = await pw.chromium.launch();
  const page = await browser.newPage({
    viewport: { width: opt("--width", 1400), height: opt("--height", 900) },
    deviceScaleFactor: opt("--scale", 1),
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto("file://" + html);
  const cells = await page.evaluate(() => window.HSCH.cells());
  for (const c of cells) {
    await page.evaluate((cell) => window.HSCH.show(cell), c);
    await page.waitForTimeout(50);
    const file = path.join(out, c + ".png");
    await page.locator("#canvas").screenshot({ path: file });
    console.log(file);
  }
  await browser.close();
  if (errors.length) { console.error("page errors:\n" + errors.join("\n")); process.exit(1); }
})();
