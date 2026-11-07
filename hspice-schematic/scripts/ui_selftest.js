#!/usr/bin/env node
// Viewer self-test: presses every control on desktop and on an emulated phone (real touch
// events) and asserts what must hold afterwards: the drawing stays on screen, pans 1:1 with
// the pointer, toggles change only labels, navigation lands on the right cell, no tooltip is
// left behind, no JS errors.
// usage: node ui_selftest.js schematic.html      (exit code 1 on any failure)
const path = require("path");
const pw = require("playwright");

const html = "file://" + path.resolve(process.argv[2]);
let fails = 0, passes = 0;
function check(name, ok, detail) {
  if (ok) passes++; else fails++;
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${ok || !detail ? "" : "  -> " + detail}`);
}

async function probe(p) {
  return p.evaluate(() => {
    const v = document.querySelector(".view:not([hidden])");
    const svg = v.querySelector("svg");
    const c = document.getElementById("canvas").getBoundingClientRect();
    const g = v.querySelector(".layer-syms").getBoundingClientRect();
    const pin = v.querySelector("circle.pin").getBoundingClientRect();   // never hidden by toggles
    const ix = Math.max(0, Math.min(g.right, c.right) - Math.max(g.left, c.left));
    const iy = Math.max(0, Math.min(g.bottom, c.bottom) - Math.max(g.top, c.top));
    const vis = (ix * iy) / Math.max(1, Math.min(g.width * g.height, c.width * c.height));
    return {
      cell: v.dataset.cell, vb: svg.getAttribute("viewBox").split(" ").map(Number),
      bounds: svg.getAttribute("data-bounds").split(",").map(Number),
      gx: pin.x, gy: pin.y, gw: g.width, vis,
      tip: !document.getElementById("tip").hidden,
      crumbs: document.querySelectorAll("#crumbs a").length,
      hl: v.querySelectorAll(".hl").length,
      body: document.body.className,
    };
  });
}
const near = (a, b, tol = 2) => Math.abs(a - b) <= tol;
const sameVB = (a, b) => a.vb.every((x, i) => near(x, b.vb[i], 0.01));
const fitted = (s) => near(s.vb[0], s.bounds[0], 0.01) && near(s.vb[2], s.bounds[2] - s.bounds[0], 0.01);
const TOG = { wl: ".lbl-wl", val: ".lbl-val", name: ".lbl-name", net: ".lbl-net" };

async function toggleChecks(p, label, tapFn) {
  for (const [t, sel] of Object.entries(TOG)) {
    const before = await probe(p);
    const disp0 = await p.evaluate((s) => { const e = document.querySelector(".view:not([hidden]) " + s); return e ? getComputedStyle(e).display : null; }, sel);
    await tapFn(`[data-toggle="${t}"]`);
    const after = await probe(p);
    const disp1 = await p.evaluate((s) => { const e = document.querySelector(".view:not([hidden]) " + s); return e ? getComputedStyle(e).display : null; }, sel);
    check(`${label}: toggle ${t} keeps the drawing in place`, sameVB(before, after) && near(before.gx, after.gx) && near(before.gy, after.gy),
          `vb ${before.vb} -> ${after.vb}, content (${before.gx|0},${before.gy|0}) -> (${after.gx|0},${after.gy|0})`);
    if (disp0 !== null) check(`${label}: toggle ${t} switches its labels`, disp0 !== disp1, `${disp0} -> ${disp1}`);
    await tapFn(`[data-toggle="${t}"]`);
    const back = await probe(p);
    check(`${label}: toggle ${t} twice restores`, sameVB(before, back) && back.body === before.body,
          `vb ${before.vb} -> ${back.vb}, body '${before.body}' -> '${back.body}'`);
  }
}

async function desktop(b) {
  const p = await b.newPage({ viewport: { width: 1300, height: 850 } });
  const errs = [];
  p.on("pageerror", (e) => errs.push(String(e)));
  p.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  await p.goto(html);
  await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await p.reload();
  let s = await probe(p);
  const top = s.cell;
  check("desktop: opens on the top cell, fitted, visible", fitted(s) && s.vis > 0.9 && !s.tip);
  await toggleChecks(p, "desktop", (sel) => p.click(sel));

  // mouse drag pans 1:1
  const c = await p.locator("#canvas").boundingBox();
  const cx = c.x + c.width / 2, cy = c.y + c.height / 2;
  s = await probe(p);
  await p.mouse.move(cx + 200, cy + 150); await p.mouse.down();
  await p.mouse.move(cx + 260, cy + 180, { steps: 6 }); await p.mouse.move(cx + 300, cy + 200, { steps: 6 });
  await p.mouse.up();
  let s2 = await probe(p);
  check("desktop: drag pans 1:1", near(s2.gx - s.gx, 100) && near(s2.gy - s.gy, 50), `moved (${(s2.gx - s.gx).toFixed(1)},${(s2.gy - s.gy).toFixed(1)}) expected (100,50)`);
  check("desktop: drag does not navigate", s2.cell === top);
  await toggleChecks(p, "desktop after pan", (sel) => p.click(sel));

  // wheel zoom + clamp
  s = await probe(p);
  await p.mouse.move(cx, cy); await p.mouse.wheel(0, -400); await p.waitForTimeout(50);
  s2 = await probe(p);
  check("desktop: wheel zooms in", s2.vb[2] < s.vb[2] && s2.vis > 0.05);
  for (let i = 0; i < 40; i++) await p.mouse.wheel(0, 2000);
  s2 = await probe(p);
  check("desktop: zoom-out is clamped", s2.vb[2] <= (s2.bounds[2] - s2.bounds[0]) * 20 + 1 && s2.vis > 0);
  await p.click("#btn-fit");
  check("desktop: 맞춤 restores the full view", fitted(await probe(p)));
  await p.mouse.wheel(0, -500); await p.mouse.dblclick(c.x + 30, c.y + 30);
  check("desktop: double-click fits", fitted(await probe(p)));

  // hover tooltip
  const dev = p.locator('.view:not([hidden]) .symg[data-inst="X_CTLE"] .hit, .view:not([hidden]) .symg .hit').first();
  await dev.hover({ force: true });
  check("desktop: hover on a block shows a tooltip", (await probe(p)).tip);
  await p.mouse.move(c.x + 5, c.y + 5);
  check("desktop: moving away hides it", !(await probe(p)).tip);

  // navigation by click, breadcrumb, 상위, keys
  const blocks = await p.$$eval(".view:not([hidden]) .symg.clickable", (els) => els.map((e) => [e.dataset.inst, e.dataset.ref]));
  for (const [inst, ref] of blocks) {
    await p.locator(`.view:not([hidden]) .symg[data-inst="${inst}"] .hit`).click({ force: true });
    s = await probe(p);
    check(`desktop: click ${inst} opens ${ref}`, s.cell === ref && s.crumbs === 2 && !s.tip && s.vis > 0.9 && fitted(s), JSON.stringify(s));
    await p.click("#btn-up");
    check(`desktop: 상위 returns from ${ref}`, (await probe(p)).cell === top);
  }
  // deepest path, breadcrumb jump, Esc / Backspace / F
  async function deepest() {
    for (let d = 0; d < 8; d++) {
      const all = await p.$$(".view:not([hidden]) .symg.clickable .hit");
      if (!all.length) break;
      await all[all.length - 1].click({ force: true });   // last block = deepest path here
    }
  }
  await deepest();
  s = await probe(p);
  check("desktop: can descend to a transistor-level cell", s.crumbs >= 2 && !(await p.$(".view:not([hidden]) .symg.clickable")));
  const depth = s.crumbs;
  await p.keyboard.press("Escape");
  check("desktop: Esc goes up one level", (await probe(p)).crumbs === depth - 1);
  await p.keyboard.press("Backspace");
  check("desktop: Backspace goes up one level", (await probe(p)).crumbs === depth - 2 || depth - 2 < 1);
  await deepest();
  await p.locator("#crumbs a").first().click();
  s = await probe(p);
  check("desktop: breadcrumb root returns to top", s.cell === top && s.crumbs === 1);
  await p.click("#btn-up");
  check("desktop: 상위 at the top does nothing", (await probe(p)).cell === top);
  await p.mouse.wheel(0, -300); await p.keyboard.press("f");
  check("desktop: F fits", fitted(await probe(p)));
  // checkbox focus must not swallow Esc
  await deepest(); const d0 = (await probe(p)).crumbs;
  await p.click('[data-toggle="wl"]'); await p.click('[data-toggle="wl"]');
  await p.keyboard.press("Escape");
  check("desktop: Esc works after clicking a toggle", (await probe(p)).crumbs === d0 - 1);

  // cell selector
  const opts = await p.$$eval("#cell-jump option", (os) => os.map((o) => o.value));
  for (const o of opts) {
    await p.selectOption("#cell-jump", o);
    s = await probe(p);
    check(`desktop: selector opens ${o}`, s.cell === o && s.crumbs === 1 && s.vis > 0.9);
  }
  await p.selectOption("#cell-jump", top);

  // net highlight: click sticks, second click clears, side-panel hover highlights
  const wire = p.locator(".view:not([hidden]) line.wire").first();
  await wire.click({ force: true });
  check("desktop: clicking a net highlights it", (await probe(p)).hl > 0);
  await wire.click({ force: true });
  await p.mouse.move(c.x + 5, c.y + 5);
  check("desktop: clicking it again clears the highlight", (await probe(p)).hl === 0);
  const link = p.locator("#side .netlink").first();
  if (await link.count()) { await link.hover(); check("desktop: side-panel net hover highlights", (await probe(p)).hl > 0); }

  // persistence + resize
  await p.click('[data-toggle="wl"]');
  await p.reload();
  check("desktop: toggle state survives reload", !(await p.isChecked('[data-toggle="wl"]')) && (await probe(p)).body.includes("hide-wl"));
  await p.click('[data-toggle="wl"]');
  await p.setViewportSize({ width: 700, height: 900 });
  check("desktop: drawing visible after resize", (await probe(p)).vis > 0.9);
  check("desktop: no JS errors", errs.length === 0, errs.join(" | "));
  await p.close();
}

async function mobile(b) {
  const ctx = await b.newContext({ ...pw.devices["Pixel 7"] });
  const p = await ctx.newPage();
  const errs = [];
  p.on("pageerror", (e) => errs.push(String(e)));
  await p.goto(html);
  await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await p.reload();
  await p.evaluate(() => { window.__cancel = 0; window.addEventListener("pointercancel", () => window.__cancel++, true); });
  const cdp = await ctx.newCDPSession(p);
  const touch = (type, pts) => cdp.send("Input.dispatchTouchEvent", { type, touchPoints: pts.map(([x, y], i) => ({ x, y, id: i })) });
  async function finger(x0, y0, x1, y1, steps = 10) {
    await touch("touchStart", [[x0, y0]]);
    for (let i = 1; i <= steps; i++) await touch("touchMove", [[x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps]]);
    await touch("touchEnd", []);
  }
  async function thumbTap(sel) {          // a real thumb tap wiggles a few px
    const bb = await p.locator(sel).first().boundingBox();
    const x = bb.x + bb.width / 2, y = bb.y + bb.height / 2;
    await touch("touchStart", [[x, y]]); await touch("touchMove", [[x + 2, y + 3]]); await touch("touchMove", [[x + 3, y + 4]]);
    await touch("touchEnd", []);
    await p.waitForTimeout(30);
  }
  const c = await p.locator("#canvas").boundingBox();
  const cx = c.x + c.width / 2, cy = c.y + c.height / 2;
  let s = await probe(p);
  const top = s.cell;
  check("phone: opens fitted and visible", fitted(s) && s.vis > 0.9);
  await finger(cx - 40, cy - 30, cx + 40, cy + 20);
  let s2 = await probe(p);
  check("phone: one-finger pan is 1:1", near(s2.gx - s.gx, 80, 3) && near(s2.gy - s.gy, 50, 3), `moved (${(s2.gx - s.gx).toFixed(1)},${(s2.gy - s.gy).toFixed(1)}) expected (80,50)`);
  check("phone: the browser does not cancel the pan", (await p.evaluate(() => window.__cancel)) === 0);
  await toggleChecks(p, "phone after pan", thumbTap);
  // pinch
  s = await probe(p);
  await touch("touchStart", [[cx - 30, cy], [cx + 30, cy]]);
  for (let i = 1; i <= 8; i++) await touch("touchMove", [[cx - 30 - i * 12, cy], [cx + 30 + i * 12, cy]]);
  await touch("touchEnd", []);
  s2 = await probe(p);
  check("phone: pinch-out zooms in", s2.vb[2] < s.vb[2] * 0.6 && s2.vis > 0.05, `vb width ${s.vb[2]} -> ${s2.vb[2]}`);
  await touch("touchStart", [[cx - 120, cy], [cx + 120, cy]]);
  for (let i = 1; i <= 8; i++) await touch("touchMove", [[cx - 120 + i * 12, cy], [cx + 120 - i * 12, cy]]);
  await touch("touchEnd", []);
  check("phone: pinch-in zooms out again", (await probe(p)).vb[2] > s2.vb[2]);
  await toggleChecks(p, "phone after pinch", thumbTap);
  await thumbTap("#btn-fit");
  check("phone: 맞춤 restores the view", fitted(await probe(p)));
  // tap a block right after a pinch must still navigate
  await touch("touchStart", [[cx - 30, cy], [cx + 30, cy]]); await touch("touchMove", [[cx - 50, cy], [cx + 50, cy]]); await touch("touchEnd", []);
  await thumbTap("#btn-fit");
  const blk = await p.$eval(".view:not([hidden]) .symg.clickable", (e) => [e.dataset.inst, e.dataset.ref]);
  await p.locator(`.view:not([hidden]) .symg[data-inst="${blk[0]}"] .hit`).hover({ force: true });
  await thumbTap(`.view:not([hidden]) .symg[data-inst="${blk[0]}"] .hit`);
  s = await probe(p);
  check(`phone: tap ${blk[0]} opens ${blk[1]} with no tooltip left`, s.cell === blk[1] && !s.tip && s.vis > 0.9, JSON.stringify(s));
  await toggleChecks(p, "phone inside a block", thumbTap);
  // transistor-level view: tap a device -> tooltip, tap empty paper -> gone
  const devSel = ".view:not([hidden]) .symg.dev";
  if (await p.$(devSel)) {
    await thumbTap(devSel);
    check("phone: tapping a device shows its tooltip", (await probe(p)).tip);
    await thumbTap("#canvas .view:not([hidden]) svg");   // centre of the paper
    const c2 = await p.locator("#canvas").boundingBox();
    await touch("touchStart", [[c2.x + 6, c2.y + 6]]); await touch("touchEnd", []); await p.waitForTimeout(30);
    check("phone: tapping empty paper hides it", !(await probe(p)).tip);
  }
  await thumbTap("#btn-up");
  check("phone: 상위 returns", (await probe(p)).cell === top);
  // tap a block immediately after a pan (browser would normally swallow this click)
  await finger(cx - 30, cy, cx + 30, cy, 4);
  await thumbTap("#btn-fit");
  await finger(cx - 20, cy - 10, cx + 20, cy + 10, 4);
  const blk2 = await p.$eval(".view:not([hidden]) .symg.clickable", (e) => [e.dataset.inst, e.dataset.ref]);
  await thumbTap(`.view:not([hidden]) .symg[data-inst="${blk2[0]}"] .hit`);
  s = await probe(p);
  check("phone: tap on a block right after a pan still opens it", s.cell === blk2[1] && !s.tip, JSON.stringify(s));
  await thumbTap("#crumbs a");
  check("phone: breadcrumb tap returns to top", (await probe(p)).cell === top);
  await p.setViewportSize({ width: 915, height: 412 });
  check("phone: landscape keeps the drawing visible", (await probe(p)).vis > 0.9);
  check("phone: no JS errors", errs.length === 0, errs.join(" | "));
  await ctx.close();
}

(async () => {
  const b = await pw.chromium.launch();
  try { await desktop(b); await mobile(b); }
  catch (e) { fails++; console.log("FAIL  harness error: " + e.stack); }
  await b.close();
  console.log(`\n${passes} passed, ${fails} failed`);
  process.exit(fails ? 1 : 0);
})();
