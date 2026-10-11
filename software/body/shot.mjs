import { chromium } from 'playwright-core';
const views = process.argv.slice(2);
const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const p = await b.newPage({viewport: {width: 900, height: 1400}});
p.on('console', m => console.log('console:', m.text()));
p.on('pageerror', e => console.log('err:', e.message));
for (const v of views) {
  const [view, w, h, layers, data, extra] = v.split(':');
  await p.setViewportSize({width: +w, height: +h});
  await p.goto(`http://127.0.0.1:8765/view.html?view=${view}&w=${w}&h=${h}` + (layers ? `&layers=${layers}` : '') + (data ? `&data=${data}` : '') + (extra ? `&${extra}` : ''));
  await p.waitForFunction(() => document.title === 'done', null, {timeout: 120000});
  await p.screenshot({path: `out/${view}${layers ? '-' + layers.replace(/,/g, '+') : ''}.png`});
  console.log('ok', v);
}
await b.close();
