// usage: node shot.js <dir with *.svg> [scale]  -> writes <name>.png next to each svg
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
(async () => {
  const dir = process.argv[2], scale = parseFloat(process.argv[3] || '1');
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: scale });
  for (const f of files) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    const m = svg.match(/width="(\d+)" height="(\d+)"/);
    await page.setViewportSize({ width: parseInt(m[1]), height: parseInt(m[2]) });
    await page.setContent('<html><body style="margin:0">' + svg + '</body></html>');
    await page.screenshot({ path: path.join(dir, f.replace(/\.svg$/, '.png')) });
  }
  await browser.close();
})();
