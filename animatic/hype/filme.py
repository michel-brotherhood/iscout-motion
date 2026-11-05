"""Filme iSCOUT 30 s — linguagem hype, 2.39:1 (1920x804), 24 fps, 720 frames.

Uso: SRCWA=<clipes wa*.mp4> PORT=<pasta p1..p4.png> FONTDIR=<ttf> python3 filme.py <saida.mp4>
Atos: sombra (P&B) -> evidência (verde iSCOUT) -> retratos + montagem rápida -> marca.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
from fx import (W, H, FPS, WA, frames, bw, duo, glitch, electric, glow_draw, title, font)

PORT = os.environ["PORT"]
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
LIME = (205, 213, 92)
YW = 100            # recorte vertical dos clipes (mantém a legenda/marca d'água fora do 2.39:1)

def img_frames(name, dur):
    im = Image.open(os.path.join(PORT, name)).convert("RGB")
    s = max(W / im.width, H / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    a = np.asarray(im.crop((x, y, x + W, y + H))).astype(np.float32)
    return [a] * int(round(dur * FPS))

def src(kind, *p):
    return img_frames(*p) if kind == "img" else frames(f"{WA}/{p[0]}", p[1], p[2], y_off=YW)

def zoom(im, z, fx=0.5, fy=0.5):
    if z == 1: return im
    w, h = int(W * z), int(H * z); im = im.resize((w, h), Image.BILINEAR)
    x, y = int((w - W) * fx), int((h - H) * fy); return im.crop((x, y, x + W, y + H))

def energy_v(im, t, seed):
    glow_draw(im, lambda d: (electric(d, [(0, H * .98), (W * .27, H * .62), (W * .40, H * .98)], t, 5, seed),
                             electric(d, [(W, H * .98), (W * .73, H * .62), (W * .60, H * .98)], t, 5, seed + 1)), 16, 4)

def energy_edges(im, t, seed):
    """Raios contornando a silhueta central (aproximação: duas linhas verticais irregulares)."""
    glow_draw(im, lambda d: (electric(d, [(W * .36, 0), (W * .33, H * .5), (W * .37, H)], t, 4, seed),
                             electric(d, [(W * .64, 0), (W * .67, H * .5), (W * .63, H)], t, 4, seed + 7)), 14, 4)

# (duração s, fonte, gradação, opções)
EDL = [
    # ATO 1 · SOMBRA (P&B)
    (1.6, ("img", "p4.png"), "bw", dict(push=.08, flick=True, txt=("O TALENTO", 150, .86, False), edges=True)),
    (0.6, ("vid", "wa3.mp4", 4.6, 0.6), "bw", dict(gl=4)),
    (1.2, ("img", "p3.png"), "bw", dict(push=.05, txt=("ACONTECE EM CAMPO", 110, .86, False), edges=True)),
    (0.15, "flash", None, {}),
    # ATO 2 · CAPTURA (cor natural, HUD de gravação) — "Se grava, a iSCOUT transforma em dado."
    (0.8, "black", None, dict(txt=("SE GRAVA,", 170, .5, True))),
    (1.6, ("img", "c1.png"), "nat", dict(push=.06, hud=True, txt=("CELULAR", 120, .86, False))),
    (1.4, ("img", "c2.png"), "nat", dict(push=.06, hud=True, gl=3, txt=("CÂMERA DE AÇÃO", 110, .86, False))),
    (1.6, ("img", "c3.png"), "nat", dict(push=.05, hud=True, gl=3, txt=("CÂMERA PROFISSIONAL", 100, .86, False))),
    (1.0, "black", None, dict(txt=("VIRA DADO.", 190, .5, False, LIME))),
    (1.8, ("scan", ("vid", "wa1.mp4", 3.0, 1.8)), "scan", dict(txt=("DO VÍDEO BRUTO À EVIDÊNCIA", 92, .86, False))),
    (1.2, ("vid", "wa5.mp4", 3.2, 1.2), "duo", dict(gl=3)),
    # ATO 3 · EVIDÊNCIA (verde iSCOUT)
    (1.2, ("vid", "wa5.mp4", 0.2, 1.2), "duo", dict(push=.04)),
    (1.4, ("vid", "wa1.mp4", 4.4, 1.4), "duo", dict(txt=("CADA JOGADA", 150, .80, True))),
    (1.0, ("vid", "wa3.mp4", 4.0, 1.0), "duo", dict(gl=3, txt=("CONTA.", 170, .80, False, LIME))),
    (1.2, ("vid", "wa2.mp4", 0.3, 1.2), "duo", dict(push=.04)),
    (1.4, ("vid", "wa2.mp4", 3.0, 1.4), "duo", dict(txt=("UMA TRAJETÓRIA", 140, .80, True))),
    (1.2, ("vid", "wa2.mp4", 7.0, 1.2), "duo", dict(txt=("REVELA MAIS.", 160, .80, False, LIME))),
    (1.4, ("vid", "wa4.mp4", 2.0, 1.4), "duo", dict(crop=(1.35, .30, .22), txt=("DECISÃO HUMANA", 140, .80, True))),
    (1.4, ("vid", "wa4.mp4", 4.0, 1.4), "duo", dict(crop=(1.35, .30, .22), txt=("COM EVIDÊNCIA.", 150, .80, False, LIME))),
    (2.0, ("vid", "wa6.mp4", 1.6, 2.0), "duo", dict(gl=3, push=.05)),
    (0.15, "flash", None, dict(color=LIME)),
    # ATO 4 · RETRATOS + CLÍMAX
    (2.05, ("img", "p1.png"), "duo", dict(push=.07, v=True, txt=("INTELIGÊNCIA PARA DESENVOLVER", 84, .90, False))),
    (0.2, ("vid", "wa3.mp4", 6.0, 0.2), "duo", dict(gl=2)),
    (0.2, ("img", "c1.png"), "duo", dict(gl=2, hud=True)),
    (0.2, ("vid", "wa5.mp4", 6.0, 0.2), "duo", dict(gl=2)),
    (0.2, ("img", "c2.png"), "duo", dict(gl=2, hud=True)),
    (0.8, "black", None, dict(txt=("VISIBILIDADE", 170, .5, True))),
    (2.0, ("img", "p2.png"), "duo", dict(push=.07, v=True, txt=("PARA DESCOBRIR.", 130, .88, False, LIME))),
    (2.0, ("img", "p4.png"), "duo", dict(push=.06, edges=True)),
    (0.35, ("vid", "wa3.mp4", 4.5, 0.35), "duo", dict(gl=2)),
    (0.35, ("img", "c3.png"), "duo", dict(gl=2, hud=True)),
    (0.35, ("vid", "wa1.mp4", 3.6, 0.35), "duo", dict(gl=2)),
    (0.35, ("vid", "wa5.mp4", 7.0, 0.35), "duo", dict(gl=2)),
    (0.35, ("img", "c1.png"), "duo", dict(gl=2, hud=True)),
    (0.35, ("vid", "wa2.mp4", 3.8, 0.35), "duo", dict(gl=2)),
    (0.35, ("img", "p3.png"), "duo", dict(gl=2)),
    (0.35, ("vid", "wa6.mp4", 2.5, 0.35), "duo", dict(gl=2)),
    (0.35, ("vid", "wa4.mp4", 4.0, 0.35), "duo", dict(gl=2, crop=(1.35, .30, .22))),
    (0.35, ("img", "p1.png"), "duo", dict(gl=2)),
    (1.0, "converge", None, {}),
]

def hud(im, i, seed):
    """Interface de gravação desenhada por código: REC, timecode, cantoneiras."""
    d = ImageDraw.Draw(im); m = 40; L = 70; c = (255, 255, 255, 220)
    for x, y, sx, sy in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        d.line([(x, y), (x + L * sx, y)], fill=c, width=5); d.line([(x, y), (x, y + L * sy)], fill=c, width=5)
    if (i // 6) % 2 == 0: d.ellipse([m + 30, m + 28, m + 54, m + 52], fill=(230, 40, 40, 255))
    d.text((m + 66, m + 40), "REC", font=font(34), anchor="lm", fill=c, stroke_width=3, stroke_fill=(0, 0, 0, 200))
    fr = (seed * 13 + i) % (FPS * 60)
    d.text((W - m - 30, m + 40), "00:%02d:%02d:%02d" % (fr // (FPS * 60), (fr // FPS) % 60, fr % FPS), font=font(30), anchor="rm", fill=c, stroke_width=3, stroke_fill=(0, 0, 0, 200))

def nat(fr):
    """Cor natural dessaturada: o mundo real antes de virar dado."""
    return fr * 0.55 + bw(fr, 1.25, 0.05) * 0.45

TOTAL = 1080   # 45 s

def text_opt(im, o, i, n):
    if "txt" not in o: return
    t = o["txt"]; s, size, y, outline = t[0], t[1], t[2], t[3]; col = t[4] if len(t) > 4 else (255, 255, 255)
    a = min(1, i / 4) * (1 - max(0, (i - n + 4) / 4)) if n > 10 else 1
    title(im, s, size, H * y, outline=outline, a=a, color=col)

def render_shot(dur, source, grade, o, seed):
    n = int(round(dur * FPS))
    if source == "flash":
        return [Image.new("RGBA", (W, H), o.get("color", (255, 255, 255)) + (255,)) for _ in range(n)]
    if source == "black":
        out = []
        for i in range(n):
            im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); text_opt(im, o, i, n)
            if i < 3: im = Image.fromarray(glitch(np.array(im.convert("RGB")).astype(np.float32), .7, seed + i).astype(np.uint8)).convert("RGBA")
            out.append(im)
        return out
    if source == "converge":
        out = []
        for i in range(n):
            im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); t = i / (n - 1)
            glow_draw(im, lambda d: (electric(d, [(0, H * .5), (W * (.5 * t), H * .5)], 1, 6, seed + i),
                                     electric(d, [(W, H * .5), (W * (1 - .5 * t), H * .5)], 1, 6, seed + i + 50)), 18, 4)
            out.append(im)
        return out
    if source[0] == "scan":
        clip = src(*source[1])[:n]
    else:
        clip = (img_frames(source[1], dur) if source[0] == "img" else src(*source))[:n]
    out = []
    for i, fr in enumerate(clip):
        if grade == "bw": a = bw(fr, 1.7, 0.1)
        elif grade == "duo": a = duo(fr)
        elif grade == "nat": a = nat(fr)
        elif grade == "scan":
            # linha de varredura: à esquerda o vídeo bruto, à direita o dado (verde iSCOUT)
            x = int(W * min(1, i / (n * .7))); a = nat(fr).copy(); a[:, :x] = duo(fr)[:, :x]
        else: k = min(1, i / max(1, n - 1)); a = bw(fr) * (1 - k) + duo(fr) * k
        if o.get("gl") and i < o["gl"]: a = glitch(a, 1 - i / o["gl"], seed + i)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        if "crop" in o:
            z, cx, cy = o["crop"]; im = im.resize((int(W * z), int(H * z))); im = im.crop((int(W * cx), int(H * cy), int(W * cx) + W, int(H * cy) + H))
        if o.get("push"): im = zoom(im, 1 + o["push"] * i / n)
        if o.get("flick") and i % 7 in (0, 1) and i < n * .6:
            im = Image.blend(im, Image.new("RGBA", (W, H), (0, 0, 0, 255)), .55)
        if grade == "scan":
            x = int(W * min(1, i / (n * .7)))
            glow_draw(im, lambda d: d.line([(x, 0), (x, H)], fill=LIME + (255,), width=4), 14, 3)
        if o.get("hud"): hud(im, i, seed)
        if o.get("edges"): energy_edges(im, min(1, i / 8), seed + i)
        if o.get("v"): energy_v(im, min(1, i / 10), seed + i)
        text_opt(im, o, i, n)
        out.append(im)
    return out

def brand(n):
    """25–30 s: tudo assentado até 27 s (frame 48 desta cena), depois leitura."""
    icon = Image.open(os.path.join(A, "brand/icone.png")).convert("RGBA")
    logo = Image.open(os.path.join(A, "brand/iscout-logo-branca.png")).convert("RGBA")
    out = []
    for i in range(n):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        e = lambda a, b: max(0, min(1, (i - a) / (b - a)))
        k = 1 - (1 - e(0, 12)) ** 3
        s = int(H * .30 * (0.7 + 0.3 * k))
        ic = icon.resize((s, s), Image.LANCZOS); ic.putalpha(ic.split()[3].point(lambda v: int(v * k)))
        cx = W * .5 - (W * .17) * e(14, 26); cy = H * .36
        if i < 16:   # anel de energia fechando no ícone
            glow_draw(im, lambda d: d.ellipse([cx - s * .62, cy - s * .62, cx + s * .62, cy + s * .62], outline=LIME + (int(255 * (1 - i / 16)),), width=5), 18, 4)
        im.alpha_composite(ic, (int(cx - s / 2), int(cy - s / 2)))
        la = e(18, 30)
        if la > 0:
            lw = int(W * .32); lh = int(lw * logo.height / logo.width)
            lg = logo.resize((lw, lh), Image.LANCZOS); lg.putalpha(lg.split()[3].point(lambda v: int(v * la)))
            im.alpha_composite(lg, (int(W * .5 - W * .03 + (1 - la) * 30), int(cy - lh / 2)))
        title(im, "O talento acontece em campo.", 54, H * .68, outline=False, a=e(28, 36))
        title(im, "A iSCOUT ajuda a enxergá-lo.", 54, H * .77, outline=False, a=e(32, 40), color=LIME)
        ca = e(40, 48)
        if ca > 0:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            bw_, by = 720, H * .855
            d.rounded_rectangle([W / 2 - bw_ / 2, by, W / 2 + bw_ / 2, by + 76], 38, fill=LIME + (255,))
            d.text((W / 2 - 175, by + 38), "Conheça a iSCOUT", font=font(34), anchor="mm", fill=(8, 12, 8, 255))
            d.text((W / 2 + 195, by + 38), "iscout.tech", font=font(34), anchor="mm", fill=(8, 12, 8, 255))
            d.line([(W / 2 + 48, by + 18), (W / 2 + 48, by + 58)], fill=(8, 12, 8, 160), width=2)
            ov.putalpha(ov.split()[3].point(lambda v: int(v * ca))); im.alpha_composite(ov)
        out.append(im)
    return out

def disclaimer(im):
    d = ImageDraw.Draw(im); d.text((W - 24, H - 18), "Imagens e interfaces ilustrativas", font=font(18), anchor="rd", fill=(255, 255, 255, 150))

if __name__ == "__main__":
    yy, xx = np.mgrid[0:H, 0:W]
    VIG = np.clip(1 - 0.5 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2), 0.3, 1)[..., None].astype(np.float32)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", sys.argv[1]], stdin=subprocess.PIPE)
    f = 0; seed = 1; rng = np.random.default_rng(3)
    def emit(im, ev=True):
        global f
        a = np.asarray(im.convert("RGB")).astype(np.float32)
        a = a * VIG if ev else a
        a = a + rng.normal(0, 7, (H, W, 1)).astype(np.float32)
        p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); f += 1
    for dur, source, grade, o in EDL:
        for im in render_shot(dur, source, grade, o, seed): emit(im)
        seed += 37
    for im in brand(TOTAL - f): emit(im, ev=False)
    p.stdin.close(); p.wait()
    print(f, "frames")
