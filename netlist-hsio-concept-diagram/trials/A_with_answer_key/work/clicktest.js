const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 1 });
  await p.goto('file://' + process.argv[2]);
  const t = async () => (await p.textContent('#vtitle')) + ' | ' + (await p.textContent('#crumbs'));
  console.log('start:', await t());
  await p.click('g.clk[data-label="X_DFE_EVEN"]'); console.log('click slice:', await t());
  await p.click('g.clk[data-label="X_SUM"]'); console.log('click Σ:', await t());
  await p.click('#crumbs a[data-i="1"]'); console.log('crumb back:', await t());
  await p.click('g.clk[data-label="X_SLICER"]'); await p.click('g.clk[data-label="X_SR"]'); await p.click('g.clk[data-label="X1"]');
  console.log('deep:', await t());
  const vis = async () => p.evaluate(() => [...document.querySelectorAll('#svgwrap text.wl')].filter(e => getComputedStyle(e).display !== 'none').length);
  console.log('wl visible:', await vis()); await p.click('#wl'); console.log('wl after toggle:', await vis());
  const href = await p.getAttribute('#dl', 'href'); console.log('pptx link bytes:', href ? href.length : 0);
  const om = await p.evaluate(() => document.querySelectorAll('table.om tr').length); console.log('omitted rows on this view:', om);
  await b.close();
})();
