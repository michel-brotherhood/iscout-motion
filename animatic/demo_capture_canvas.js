// Captura a demo "iScout Pro" (canvas, demo_interativa_iscout.html) quadro a quadro, 24 fps, página inteira em 1920x1080.
// Pausa o relógio interno e avança currentStep em passos inteiros (como o scrub do HTML): contorna o bug do HTML em
// drawTrails (FRAMES[s] com índice fracionário faz a pintura parar antes dos atletas). Uso: node demo_capture_canvas.js <html> <pasta> <seg> [passo_ini]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [html, out, secs, s0] = [process.argv[2], process.argv[3], +process.argv[4], +(process.argv[5] || 0)];
  const b = await chromium.launch();
  const VW = 1810, VH = 1018;   // página inteira (1018 px) em 16:9 -> 1920x1080
  const p = await b.newPage({ viewport: { width: VW, height: VH }, deviceScaleFactor: 1920 / VW });
  await p.goto('file://' + html, { waitUntil: 'networkidle', timeout: 120000 });
  await p.waitForTimeout(1500);
  await p.evaluate(() => {
    window.requestAnimationFrame = () => 0; cancelAnimationFrame(animId);       // relógio interno parado
    document.getElementById('playIcon').classList.add('hidden');                // demo "tocando"
    document.getElementById('pauseIcon').classList.remove('hidden');
    window.__set = (st) => {
      currentStep = st;
      document.getElementById('timelineSlider').value = st;
      const secTotal = 120 + st * 0.08, m = Math.floor(secTotal / 60), s = (secTotal % 60).toFixed(1);
      document.getElementById('timeDisplay').innerText = `${String(m).padStart(2, '0')}:${s.padStart(4, '0')}`;
      renderPitch();
      return (FRAMES[st] || []).length;
    };
  });
  const n = Math.round(secs * 24), counts = [];
  for (let i = 0; i < n; i++) {
    const st = s0 + Math.round(i / 24 / 0.08);
    counts.push(await p.evaluate((x) => window.__set(x), st));
    await p.screenshot({ path: `${out}/f${String(i).padStart(5, '0')}.png` });
  }
  console.log(n, 'quadros; atletas por quadro min/max', Math.min(...counts), Math.max(...counts));
  await b.close();
})();
