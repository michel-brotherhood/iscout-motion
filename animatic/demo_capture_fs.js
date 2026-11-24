// Captura a demo "iScout Ao Vivo" v2 (com modo tela cheia): clica "Iniciar demo" e "Tela cheia" (layout body.fs),
// esconde o botão de sair e grava a 0,25x com o currentTime do vídeo. Uso: node demo_capture_fs.js <html> <pasta> <seg> [escala]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [html, out, wall] = [process.argv[2], process.argv[3], +process.argv[4]];
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: +(process.argv[5]||1.2) });
  await p.goto('file://' + html, { waitUntil: 'load', timeout: 120000 });
  await p.waitForTimeout(2500);
  await p.click('text=Iniciar demo'); await p.click('#fsbtn'); await p.addStyleTag({ content: '#fsbtn{visibility:hidden !important}' }); await p.waitForTimeout(400);
  await p.evaluate(() => { const v = document.getElementById('vid'); v.muted = true; v.playbackRate = 0.25;
    v.addEventListener('ratechange', () => { if (v.playbackRate !== 0.25) v.playbackRate = 0.25; }); });
  const log = []; const t0 = Date.now(); let k = 0;
  while (Date.now() - t0 < wall * 1000) {
    const ct = await p.evaluate(() => document.getElementById('vid').currentTime);
    const f = `${out}/f${String(k).padStart(5, '0')}.jpg`;
    await p.screenshot({ path: f, type: 'jpeg', quality: 92 });
    const ct2 = await p.evaluate(() => document.getElementById('vid').currentTime);
    log.push([k, (ct + ct2) / 2]); k++;
  }
  fs.writeFileSync(out + '/log.json', JSON.stringify(log));
  console.log(k, 'frames', log[0], log[log.length - 1]);
  await b.close();
})();
