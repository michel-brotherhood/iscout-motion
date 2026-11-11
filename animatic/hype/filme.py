"""Filme iSCOUT 30 s — linguagem hype, 2.39:1 (1920x804), 24 fps, 720 frames.

Uso: SRCWA=<clipes wa*.mp4> PORT=<pasta p1..p4.png> FONTDIR=<ttf> python3 filme.py <saida.mp4>
Atos: sombra (P&B) -> evidência (verde iSCOUT) -> retratos + montagem rápida -> marca.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from fx import (W, H, FPS, WA, VERT, frames, bw, duo, glitch, electric, glow_draw, title, font)

PORT = os.environ["PORT"]
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
LIME = (205, 213, 92)
YW = 60             # recorte vertical dos clipes (mantém a legenda/marca d'água fora do 2.39:1)

FOCUS = {"c1.png": .70, "c2.png": .28, "c3.png": .72}   # ponto de interesse horizontal no recorte vertical

def img_frames(name, dur):
    im = Image.open(os.path.join(PORT, name)).convert("RGB")
    s = max(W / im.width, H / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    fx = FOCUS.get(name, .5) if VERT else .5
    x, y = int(min(max(0, im.width * fx - W / 2), im.width - W)), (im.height - H) // 2
    a = np.asarray(im.crop((x, y, x + W, y + H))).astype(np.float32)
    return [a] * int(round(dur * FPS))

def src(kind, *p):
    if kind == "img": return img_frames(*p)
    if kind == "ast": return frames(os.path.join(A, "footage", p[0]), p[1], p[2])
    return frames(f"{WA}/{p[0]}", p[1], p[2], y_off=YW)

SCREENS = os.environ.get("SCREENS", "")
PHONE_H = PHONE_Y = None    # V2 sobe e reduz o celular para deixar a faixa de legenda livre

def phone_shot(n, clip_name, start, screen, o, seed):
    """Fundo da família desfocado + celular com a tela real do app (números já desfocados) subindo e rolando."""
    bg = frames(os.path.join(A, "footage", clip_name), start, n / FPS)
    sc = Image.open(os.path.join(SCREENS, screen)).convert("RGB")
    ph_h = int(H * (PHONE_H or (.74 if VERT else .92))); ph_w = int(ph_h * 9 / 19.5); bez = 10
    iw, ih = ph_w - 2 * bez, ph_h - 2 * bez; k = iw / sc.width; vis = int(ih / k)
    out = []
    for i in range(n):
        b = Image.fromarray(np.clip(duo(bg[min(i, len(bg) - 1)]) * .55, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14)).convert("RGBA")
        t = min(1, i / 10); e = 1 - (1 - t) ** 3
        x0 = int(W * .5 - ph_w / 2)
        y0 = int((H * PHONE_Y if PHONE_Y is not None else (H - ph_h) / (2.6 if VERT else 2)) + (1 - e) * H * .5)
        top = int((sc.height - vis) * .28 * min(1, i / n))
        tile = sc.crop((0, top, sc.width, top + vis)).resize((iw, ih), Image.LANCZOS)
        d = ImageDraw.Draw(b)
        d.rounded_rectangle([x0 - 2, y0 - 2, x0 + ph_w + 2, y0 + ph_h + 2], 46, fill=(12, 16, 12, 255), outline=LIME + (255,), width=3)
        m = Image.new("L", (iw, ih), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, iw - 1, ih - 1], 36, fill=255)
        b.paste(tile, (x0 + bez, y0 + bez), m)
        text_opt(b, o, i, n)
        out.append(b)
    return out

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
    (1.4, ("vid", "wa1.mp4", 4.4, 1.4), "duo", dict(txt=("CADA JOGADA", 150, .80, False))),
    (1.0, ("vid", "wa3.mp4", 4.0, 1.0), "duo", dict(gl=3, txt=("CONTA.", 170, .80, False, LIME))),
    (1.2, ("vid", "wa2.mp4", 0.3, 1.2), "duo", dict(push=.04)),
    (1.4, ("vid", "wa2.mp4", 3.0, 1.4), "duo", dict(txt=("UMA TRAJETÓRIA", 140, .80, False))),
    (1.2, ("vid", "wa2.mp4", 7.0, 1.2), "duo", dict(txt=("REVELA MAIS.", 160, .80, False, LIME))),
    (1.25, ("ast", "mock-family-app.mp4", 2.0, 1.25), "duolift", dict(push=.05, txt=("A FAMÍLIA ACOMPANHA.", 130, .86, False))),
    (1.5, ("phone", "mock-family-app.mp4", 3.3, "4.2.0-perfil-atleta.png"), "duo", dict(txt=("A EVOLUÇÃO NO APP.", 120, .88, False, LIME))),
    (1.4, ("vid", "wa4.mp4", 2.0, 1.4), "duo", dict(crop=(1.35, .30, .22), txt=("DECISÃO HUMANA", 140, .80, False))),
    (1.4, ("vid", "wa4.mp4", 4.0, 1.4), "duo", dict(crop=(1.35, .30, .22), txt=("COM EVIDÊNCIA.", 150, .80, False, LIME))),
    (2.0, ("vid", "wa6.mp4", 1.6, 2.0), "duohard", dict(gl=3, push=.05)),
    (0.15, "flash", None, dict(color=LIME)),
    # ATO 4 · RETRATOS + CLÍMAX
    (2.05, ("img", "p1.png"), "duo", dict(push=.07, v=True, txt=("INTELIGÊNCIA PARA DESENVOLVER", 84, .90, False))),
    (0.2, ("vid", "wa3.mp4", 4.9, 0.2), "duo", dict(gl=2)),
    (0.2, ("img", "c1.png"), "duo", dict(gl=2, hud=True)),
    (0.2, ("vid", "wa5.mp4", 6.0, 0.2), "duo", dict(gl=2)),
    (0.2, ("img", "c2.png"), "duo", dict(gl=2, hud=True)),
    (0.8, "black", None, dict(txt=("VISIBILIDADE", 170, .5, True))),
    (2.0, ("img", "p2.png"), "duo", dict(push=.07, v=True, txt=("PARA DESCOBRIR.", 130, .88, False, LIME))),
    (2.0, ("img", "p4.png"), "duo", dict(push=.06, edges=True)),
    (0.35, ("vid", "wa3.mp4", 4.5, 0.35), "duo", dict(gl=2)),
    (0.35, ("img", "c3.png"), "duo", dict(gl=2, hud=True)),
    (0.35, ("vid", "wa1.mp4", 3.3, 0.35), "duo", dict(gl=2)),
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

# cortes: (índices do EDL, frame em que a marca entra = impacto da trilha, total de frames)
CUTS = {
    "full": (None, 963, 1146),
    "30": ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 17, 18, 22, 23, 28, 29, 41], 553, 720),
    "15": ([0, 4, 5, 8, 9, 12, 13, 18, 41], 264, 360),
}
CUT = os.environ.get("CUT", "full")
_sel, BRAND_AT, TOTAL = CUTS[CUT]
if _sel is not None:
    EDL = [EDL[i] for i in _sel]
    used = sum(int(round(d * FPS)) for d, *_ in EDL[:-1])
    EDL[-1] = ((BRAND_AT - used) / FPS,) + tuple(EDL[-1][1:])   # o "converge" fecha a conta exata

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
    if source[0] == "phone":
        return phone_shot(n, source[1], source[2], source[3], o, seed)
    if source[0] == "scan":
        clip = src(*source[1])[:n]
    else:
        clip = (img_frames(source[1], dur) if source[0] == "img" else src(*source))[:n]
    out = []
    for i, fr in enumerate(clip):
        if grade == "bw": a = bw(fr, 1.7, 0.1)
        elif grade == "duo": a = duo(fr)
        elif grade == "nat": a = nat(fr)
        elif grade == "duolift": a = duo(np.clip(fr * 1.35 + 25, 0, 255))   # plano escuro de fim de tarde
        elif grade == "duohard": a = duo(np.clip((fr - 70) * 1.5, 0, 255))   # interfaces claras: desce os realces
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

def brand(n, l1="O talento acontece em campo.", l2="A iSCOUT ajuda a enxergá-lo.", cta=("Conheça a iSCOUT", "iscout.tech"), l2y=None):
    """25–30 s: tudo assentado até 27 s (frame 48 desta cena), depois leitura."""
    icon = Image.open(os.path.join(A, "brand/icone.png")).convert("RGBA")
    logo = Image.open(os.path.join(A, "brand/iscout-logo-branca.png")).convert("RGBA")
    out = []
    for i in range(n):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        e = lambda a, b: max(0, min(1, (i - a) / (b - a)))
        k = 1 - (1 - e(0, 12)) ** 3
        s = int(min(W, H) * (.36 if VERT else .30) * (0.7 + 0.3 * k)) if VERT else int(H * .30 * (0.7 + 0.3 * k))
        ic = icon.resize((s, s), Image.LANCZOS); ic.putalpha(ic.split()[3].point(lambda v: int(v * k)))
        cx = W * .5 - (0 if VERT else (W * .17) * e(14, 26)); cy = H * (.30 if VERT else .36)
        if i < 16:   # anel de energia fechando no ícone
            glow_draw(im, lambda d: d.ellipse([cx - s * .62, cy - s * .62, cx + s * .62, cy + s * .62], outline=LIME + (int(255 * (1 - i / 16)),), width=5), 18, 4)
        im.alpha_composite(ic, (int(cx - s / 2), int(cy - s / 2)))
        la = e(18, 30)
        if la > 0:
            lw = int(W * (.62 if VERT else .32)); lh = int(lw * logo.height / logo.width)
            lg = logo.resize((lw, lh), Image.LANCZOS); lg.putalpha(lg.split()[3].point(lambda v: int(v * la)))
            if VERT: im.alpha_composite(lg, (int(W / 2 - lw / 2), int(cy + s * .65 + (1 - la) * 30)))
            else: im.alpha_composite(lg, (int(W * .5 - W * .03 + (1 - la) * 30), int(cy - lh / 2)))
        title(im, l1, 54 if not VERT else 80, H * (.60 if VERT else .68), outline=False, a=e(28, 36))
        title(im, l2, 54 if not VERT else 80, H * (.66 if VERT else (l2y or .77)), outline=False, a=e(32, 40), color=LIME)
        ca = e(40, 48)
        if ca > 0:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            bw_, by = (720 if not VERT else 900), H * (.76 if VERT else .855)
            d.rounded_rectangle([W / 2 - bw_ / 2, by, W / 2 + bw_ / 2, by + 76], 38, fill=LIME + (255,))
            d.text((W / 2 - 175, by + 38), cta[0], font=font(34), anchor="mm", fill=(8, 12, 8, 255))
            d.text((W / 2 + 195, by + 38), cta[1], font=font(34), anchor="mm", fill=(8, 12, 8, 255))
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
    BUG = Image.open(os.path.join(A, "brand/icone.png")).convert("RGBA").resize((68, 68), Image.LANCZOS)
    BUG.putalpha(BUG.split()[3].point(lambda v: int(v * .85)))
    BRAND_START = BRAND_AT            # o ícone fixo sai quando a assinatura entra
    BUGA = np.asarray(BUG).astype(np.float32)
    BX, BY = W - 68 - 36, H - 68 - 30
    show_bug = [True]
    def emit(im, ev=True):
        global f
        a = np.asarray(im.convert("RGB")).astype(np.float32)
        a = a * VIG if ev else a
        a = a + rng.normal(0, 7, (H, W, 1)).astype(np.float32)
        # ícone fixo no canto inferior direito, do 2º plano até a assinatura; aplicado depois da
        # vinheta/grão para ficar nítido, e oculto nos planos com HUD de gravação (cantoneiras)
        if 38 <= f < BRAND_START and show_bug[0]:
            al = BUGA[..., 3:] / 255
            a[BY:BY + 68, BX:BX + 68] = a[BY:BY + 68, BX:BX + 68] * (1 - al) + BUGA[..., :3] * al
        p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); f += 1
    for dur, source, grade, o in EDL:
        show_bug[0] = not o.get("hud")
        for im in render_shot(dur, source, grade, o, seed): emit(im)
        seed += 37
    for im in brand(TOTAL - f): emit(im, ev=False)
    p.stdin.close(); p.wait()
    print(f, "frames")
