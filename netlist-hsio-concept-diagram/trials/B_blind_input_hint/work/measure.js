// measure text boxes of every view (for the overlap checker) and take one screenshot per view
// usage: node measure.js <concept.html> <texts.json> <screenshot dir> [mobile]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [file, outJson, shotDir, mobile] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: mobile ? { width: 390, height: 844 } : { width: 1820, height: 1000 }, deviceScaleFactor: 1 });
  await page.goto('file://' + file);
  const ids = await page.evaluate(() => DATA.views.map(v => v.id));
  const res = {};
  for (const id of ids) {
    await page.evaluate(i => { location.hash = i; }, id);
    await page.waitForTimeout(120);
    res[id] = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('#stage svg text').forEach(t => {
        const b = t.getBBox();
        out.push({ tid: t.getAttribute('data-tid'), s: t.textContent, x0: b.x, y0: b.y, x1: b.x + b.width, y1: b.y + b.height, cls: t.getAttribute('class') });
      });
      return out;
    });
    if (mobile) { const ov = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth); if (ov > 0) console.log('OVERFLOW', id, ov); }
    if (shotDir) await page.screenshot({ path: `${shotDir}/${id}${mobile ? '_mobile' : ''}.png`, fullPage: true });
  }
  if (outJson) fs.writeFileSync(outJson, JSON.stringify(res));
  // functional check: clicking a hotspot navigates down one level
  await page.evaluate(() => { location.hash = 'b_top'; });
  await page.waitForTimeout(100);
  const before = await page.evaluate(() => location.hash);
  const hot = await page.$('#stage svg rect.hot');
  if (hot) { await hot.click(); await page.waitForTimeout(100); }
  const after = await page.evaluate(() => location.hash);
  await page.evaluate(() => { document.getElementById('wl').click(); });
  const hidden = await page.evaluate(() => getComputedStyle(document.querySelector('#stage svg text.size') || document.body).display);
  const sw = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  console.log(JSON.stringify({ click_from: before, click_to: after, size_text_display_after_toggle: hidden, horizontal_overflow_px: sw }));
  await browser.close();
})();
