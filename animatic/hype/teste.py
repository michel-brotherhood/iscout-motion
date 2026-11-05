"""Teste de 10 s na linguagem "hype" (2.39:1, P&B -> verde iSCOUT, cortes rápidos, linha de energia).

Uso: SRCWA=<pasta clipes wa*.mp4> S1=<S1_dominio_1080p_uniforme.mp4> FONTDIR=<ttf> python3 teste.py <saida.mp4>
"""
import math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 804, 24
WA, S1, FONT = os.environ["SRCWA"], os.environ["S1"], os.environ["FONTDIR"]
LIME = np.array([205, 213, 92]); GREEN = np.array([104, 177, 45]); DEEP = np.array([4, 14, 8])
rng = random.Random(7)

def frames(path, start, dur, speed=1.0, y_off=None):
    """Decodifica um trecho já recortado em 2.39:1 (y_off controla o corte vertical)."""
    n = int(round(dur * FPS))
    sh = int(H * 1.0)
    vf = f"setpts={1/speed}*PTS,fps={FPS},scale={W}:-2,crop={W}:{H}:0:{'(ih-oh)/2' if y_off is None else y_off}"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-vf", vf, "-frames:v", str(n),
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    arr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    if len(arr) < n: arr = np.concatenate([arr, np.repeat(arr[-1:], n - len(arr), 0)])
    return [a.astype(np.float32) for a in arr[:n]]

def lum(a): return a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114

def bw(a, contrast=1.6, crush=0.12):
    l = lum(a) / 255
    l = np.clip((l - crush) * contrast, 0, 1) ** 1.15
    return np.repeat(l[..., None] * 255, 3, 2)

def duo(a, mix=1.0):
    """Dois tons com contraste de cinema: pretos fundos, verde iSCOUT nos meios-tons, realces quase brancos."""
    l = np.clip((lum(a) / 255 - 0.08) * 1.25, 0, 1)
    l = l * l * (3 - 2 * l)                                # curva em S
    l = l[..., None]
    mid = GREEN * 0.85
    out = np.where(l < 0.5, mid * np.clip(l / 0.5, 0, 1) ** 1.4, mid + (np.array([236, 244, 214]) - mid) * np.clip((l - 0.5) / 0.5, 0, 1) ** 1.2)
    out = out * 0.82 + bw(a, 1.3, 0.08) * 0.18 * np.array([0.9, 1.0, 0.85])   # um pouco de luminância neutra
    return a * (1 - mix) + out * mix

def finish(a, f):
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a = a * np.clip(vig, 0.25, 1)[..., None]
    grain = np.random.default_rng(f).normal(0, 9, (H, W, 1))
    return np.clip(a + grain, 0, 255).astype(np.uint8)

def glitch(a, k, seed):
    """Fatiamento horizontal: k=intensidade 0..1."""
    if k <= 0: return a
    r = random.Random(seed); out = a.copy()
    for _ in range(int(6 + 18 * k)):
        y = r.randrange(0, H - 20); h = r.randrange(6, int(20 + 80 * k)); dx = int(r.uniform(-1, 1) * 260 * k)
        out[y:y + h] = np.roll(a[y:y + h], dx, axis=1)
    out[..., 0] = np.roll(out[..., 0], int(10 * k), 1)   # leve separação cromática
    return out

def electric(draw, pts, t, width, seed, color=(205, 213, 92)):
    """Linha de energia: percorre pts até a fração t com zigue-zague que muda a cada frame."""
    r = random.Random(seed); segs = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for i in range(12):
            u = i / 12; segs.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u))
    segs = segs[:max(2, int(len(segs) * t))]
    jag = [(x + r.uniform(-7, 7), y + r.uniform(-7, 7)) for x, y in segs]
    draw.line(jag, fill=color + (255,), width=width)

def glow_draw(base, fn, blur=10, strength=2):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fn(ImageDraw.Draw(ov))
    g = ov.filter(ImageFilter.GaussianBlur(blur))
    for _ in range(strength): base.alpha_composite(g)
    base.alpha_composite(ov)

font = lambda s: ImageFont.truetype(os.path.join(FONT, "Sora-700.ttf"), s)

def title(base, txt, size, y, outline=True, a=1.0, color=(255, 255, 255)):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if outline:
        d.text((W / 2, y), txt, font=font(size), anchor="mm", fill=(0, 0, 0, 0), stroke_width=4, stroke_fill=color + (255,))
    else:
        d.text((W / 2, y), txt, font=font(size), anchor="mm", fill=color + (255,))
    if a < 1: ov.putalpha(ov.split()[3].point(lambda v: int(v * a)))
    base.alpha_composite(ov)

def shot(clip, fn):
    """fn(frame_array, i, n) -> RGBA Image"""
    return [fn(fr, i, len(clip)) for i, fr in enumerate(clip)]

out = []
# A · 0,0–0,8 s: escuro, a linha de energia nasce
for i in range(19):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    t = i / 18
    glow_draw(im, lambda d: electric(d, [(0, H * .55), (W * .35, H * .5), (W * .6, H * .58), (W, H * .52)], t, 6, i), 18, 4)
    out.append(im)

# B · 0,8–2,2 s: nosso atleta em P&B, câmera lenta, push-in
clip = frames(S1, 1.0, 1.4, speed=0.6)
def fb(fr, i, n):
    im = Image.fromarray(bw(fr).astype(np.uint8)).convert("RGBA")
    z = 1 + 0.06 * i / n; im = im.resize((int(W * z), int(H * z))).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2), int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H))
    if i < 3: im = Image.fromarray(glitch(np.array(im.convert("RGB")), 1 - i / 3, i)).convert("RGBA")
    title(im, "O TALENTO", 170, H * .5, outline=True, a=min(1, i / 6) * (1 - max(0, (i - n + 6) / 6)))
    return im
out += shot(clip, fb)

# C · 2,2–2,7 s: chute do #8, P&B, glitch de entrada
clip = frames(f"{WA}/wa3.mp4", 4.6, 0.5, y_off=100)
out += shot(clip, lambda fr, i, n: Image.fromarray(glitch(bw(fr, 1.8), max(0, 1 - i / 4), 50 + i).astype(np.uint8)).convert("RGBA"))

# D · flash branco
for i in range(4): out.append(Image.new("RGBA", (W, H), (255, 255, 255, 255)) if i < 2 else Image.new("RGBA", (W, H), (205, 213, 92, 255)))

# E · 2,85–4,2 s: leitura da jogada (círculos) em dois tons verdes
clip = frames(f"{WA}/wa1.mp4", 3.0, 1.35, y_off=100)
def fe(fr, i, n):
    im = Image.fromarray(duo(fr).astype(np.uint8)).convert("RGBA")
    title(im, "ACONTECE EM CAMPO", 96, H * .82, outline=False, a=min(1, i / 5), color=(255, 255, 255))
    return im
out += shot(clip, fe)

# F · 4,2–5,4 s: o atleta revê o lance no celular
clip = frames(f"{WA}/wa2.mp4", 3.0, 1.2, y_off=60)
out += shot(clip, lambda fr, i, n: Image.fromarray(glitch(duo(fr, .9), max(0, 1 - i / 3), 80 + i).astype(np.uint8)).convert("RGBA"))

# G · 5,4–6,4 s: treinador analisa no monitor (recorte evita a legenda gravada)
raw = frames(f"{WA}/wa4.mp4", 2.0, 1.0, y_off=60)
def fg(fr, i, n):
    im = Image.fromarray(duo(fr).astype(np.uint8)).resize((int(W * 1.35), int(H * 1.35)))
    im = im.crop((int(W * .30), int(H * .22), int(W * .30) + W, int(H * .22) + H)).convert("RGBA")
    return im
out += shot(raw, fg)

# H · 6,4–7,6 s: retrato do #8 com linhas de energia em V (estilo "media day")
clip = frames(f"{WA}/wa6.mp4", 1.3, 1.2, y_off=40)
def fh(fr, i, n):
    im = Image.fromarray(duo(fr, .95).astype(np.uint8)).convert("RGBA")
    t = min(1, i / 10)
    glow_draw(im, lambda d: (electric(d, [(0, H * .95), (W * .28, H * .7), (W * .42, H * .9)], t, 5, 200 + i),
                             electric(d, [(W, H * .95), (W * .72, H * .7), (W * .58, H * .9)], t, 5, 300 + i)), 16, 4)
    return im
out += shot(clip, fh)

# I · 7,6–10 s: tipografia gigante + glitch
for i in range(58):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    title(im, "CADA JOGADA", 190, H * .42, outline=True, a=min(1, i / 4), color=(255, 255, 255))
    if i > 12: title(im, "CONTA.", 190, H * .66, outline=False, a=min(1, (i - 12) / 3), color=(205, 213, 92))
    if i in (12, 13, 14): im = Image.fromarray(glitch(np.array(im.convert("RGB")).astype(np.float32), .8, i).astype(np.uint8)).convert("RGBA")
    out.append(im)

dst = sys.argv[1]
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
for f, im in enumerate(out):
    p.stdin.write(finish(np.array(im.convert("RGB")).astype(np.float32), f).tobytes())
p.stdin.close(); p.wait()
print(len(out), "frames")
