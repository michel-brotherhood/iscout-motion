"""Efeitos compartilhados da linguagem hype (gradação, glitch, linha de energia, tipografia)."""
import math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 804, 24
WA, FONT = os.environ["SRCWA"], os.environ["FONTDIR"]
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
    # sombra difusa para leitura sobre fumaça e realces claros
    sh = ov.split()[3].filter(ImageFilter.GaussianBlur(size * .18)).point(lambda v: int(min(255, v * 1.6)))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); shadow.putalpha(sh)
    base.alpha_composite(shadow); base.alpha_composite(ov)

def shot(clip, fn):
    """fn(frame_array, i, n) -> RGBA Image"""
    return [fn(fr, i, len(clip)) for i, fr in enumerate(clip)]

