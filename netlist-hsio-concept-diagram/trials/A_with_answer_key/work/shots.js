// screenshot every view of concept.html + browser-measured text overlap
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [html, outdir, report] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1500, height: 1000 }, deviceScaleFactor: 1 });
  const url = 'file://' + html;
  await page.goto(url);
  const ids = await page.evaluate(() => window.__views);
  const res = {};
  for (const id of ids) {
    await page.goto(url + '#v=' + id); await page.reload();
    await page.addStyleTag({ content: 'header{position:static !important}' });
    await page.waitForTimeout(150);
    const m = await page.evaluate(() => {
      const ts = [...document.querySelectorAll('#svgwrap svg text')].filter(t => getComputedStyle(t).display !== 'none' && t.textContent.trim());
      const bb = ts.map(t => { const b = t.getBBox(); return [b.x, b.y, b.x + b.width, b.y + b.height, t.textContent]; });
      const ov = [];
      for (let i = 0; i < bb.length; i++) for (let j = i + 1; j < bb.length; j++) {
        const a = bb[i], b = bb[j];
        if (Math.min(a[2], b[2]) - Math.max(a[0], b[0]) > 0.5 && Math.min(a[3], b[3]) - Math.max(a[1], b[1]) > 1.5) ov.push([a[4], b[4]]);
      }
      return { overlaps: ov, n: ts.length, sw: document.querySelector('#svgwrap svg').getBoundingClientRect().width };
    });
    res[id] = m;
    const el = await page.$('#stage');
    await el.screenshot({ path: `${outdir}/${id}.png` });
  }
  // mobile check on the top view
  const mp = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  await mp.goto(url); await mp.waitForTimeout(150);
  res.__mobile = await mp.evaluate(() => ({ docW: document.documentElement.scrollWidth, winW: innerWidth }));
  await mp.screenshot({ path: process.cwd() + "/mobile_check.png", fullPage: false });
  fs.writeFileSync(report, JSON.stringify(res, null, 1));
  await browser.close();
  for (const [k, v] of Object.entries(res)) console.log(k, JSON.stringify(v.overlaps ? { n: v.n, overlaps: v.overlaps.length } : v));
})();
