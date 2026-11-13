"""iSCOUT — "O lance inteiro" (9:16, 68,8 s, 30 fps, sem áudio e sem legenda).

Mesma minutagem da referência enviada pelo cliente: 14 planos de IA (Kling 2.5, jogadores-holograma em verde
iSCOUT), cartões de métricas com estrelas e marcações de rastreio por cima de cada lance, quadro "ANÁLISE DO LANCE"
desenhado em código, frase final em três tempos e assinatura com "Visite iscout.tech".

Uso: CLIPS=<pasta v01..v14.mp4> FONTDIR=<Sora ttf> python3 lance_v1.py <saida.mp4> [t0 t1]
     (t0/t1 opcionais: renderiza só esse trecho, para testes)
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
TOTAL = 68.8
CLIPS, FONT = os.environ["CLIPS"], os.environ["FONTDIR"]
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
LIME = (205, 213, 92); WHITE = (255, 255, 255); INK = (6, 12, 16)
F7 = lambda s: ImageFont.truetype(os.path.join(FONT, "Sora-700.ttf"), s)
F4 = lambda s: ImageFont.truetype(os.path.join(FONT, "Sora-400.ttf"), s)

def ease(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def clamp(x): return max(0., min(1., x))
def lerp(a, b, u): return a + (b - a) * u

# ---------------------------------------------------------------- elementos gráficos

def spaced(d, xy, txt, font, fill, sp=3, anchor="l"):
    """Texto com espaçamento entre letras (rótulos pequenos). anchor l|m."""
    x, y = xy
    wid = sum(font.getlength(c) + sp for c in txt) - sp
    if anchor == "m": x -= wid / 2
    for c in txt:
        d.text((x, y), c, font=font, fill=fill, anchor="lm"); x += font.getlength(c) + sp
    return wid

def star(d, cx, cy, r, filled, a):
    pts = [(cx + (r if k % 2 == 0 else r * .45) * math.sin(k * math.pi / 5), cy - (r if k % 2 == 0 else r * .45) * math.cos(k * math.pi / 5)) for k in range(10)]
    if filled: d.polygon(pts, fill=LIME + (int(255 * a),))
    else: d.polygon(pts, outline=LIME + (int(150 * a),), width=2)

def stars(d, x, cy, n, r, a, u=1.0):
    """5 estrelas; as n cheias acendem em sequência conforme u (0..1)."""
    for k in range(5):
        on = k < n and u * 5.5 > k + .5
        star(d, x + r + k * r * 2.3, cy, r, on, a)

def metric_card(d, x, y, cat, name, n, t, out=1.0, w=None):
    """Cartão: categoria pequena + nome da métrica + 5 estrelas. t = segundos desde a entrada."""
    if t < 0: return
    a = ease(t / .25) * out
    if a <= 0: return
    fN = F7(40); w = w or max(330, int(fN.getlength(name)) + 60)
    ww = int(w * ease(t / .3))
    d.rectangle([x, y, x + ww, y + 132], fill=INK + (int(205 * a),), outline=LIME + (int(90 * a),), width=1)
    d.rectangle([x, y, x + 6, y + 132], fill=LIME + (int(255 * a),))
    ta = clamp((t - .15) / .25) * out
    if ta > 0:
        spaced(d, (x + 26, y + 30), cat, F4(20), LIME + (int(220 * ta),), 4)
        d.text((x + 26, y + 70), name, font=fN, fill=WHITE + (int(255 * ta),), anchor="lm")
        stars(d, x + 26, y + 108, n, 13, ta, clamp((t - .3) / .6))

def track_box(d, cx, cy, s, label, t, out=1.0):
    """Cantoneiras de rastreio em volta de (cx, cy) + rótulo '#8  TRACKING' + ponto central."""
    if t < 0: return
    a = ease(t / .2) * out
    if a <= 0: return
    s = s * lerp(1.35, 1.0, ease(t / .3)); L = s * .28; c = LIME + (int(235 * a),)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, y0 = cx + sx * s / 2, cy + sy * s / 2
            d.line([(x0, y0), (x0 - sx * L, y0)], fill=c, width=3)
            d.line([(x0, y0), (x0, y0 - sy * L)], fill=c, width=3)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=c, width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=c)
    spaced(d, (cx - s / 2, cy - s / 2 - 22), label + "   TRACKING", F4(18), WHITE + (int(200 * a),), 3)

def connector(d, p, q, t, out=1.0):
    a = clamp(t / .3) * out
    if a <= 0: return
    u = ease(t / .35)
    d.line([p, (lerp(p[0], q[0], u), lerp(p[1], q[1], u))], fill=LIME + (int(160 * a),), width=2)

# ---------------------------------------------------------------- planos de IA

# (início, fim, chave do overlay, clipe, segundo de entrada no clipe, velocidade)
# Entradas escolhidas para fugir de defeitos da IA: v03 dissolve no fim, v08 tem um raio a partir de ~3,4 s,
# v11 mostra um rosto realista em ~1,5 s (usamos só o close da camisa e o lance a partir de 2,3 s), v12 vira fumaça.
SHOTS = [
    (0.0, 4.6, "v01", "v01", 0.2, 1.0),
    (4.6, 10.9, "v02", "v02", 0.0, 0.79),
    (10.9, 13.1, "v03", "v03", 0.3, 1.0),
    (13.1, 15.5, "v04", "v04", 0.2, 1.0),
    (15.5, 20.9, "v05", "v05", 0.0, 0.92),
    (20.9, 25.7, "v06", "v06", 0.1, 1.0),
    (25.7, 28.0, "v07", "v07", 1.2, 1.0),
    (28.0, 30.2, "v08", "v08", 0.6, 1.0),
    (30.2, 33.4, "v09", "v09", 0.6, 1.0),
    (33.4, 36.6, "v10", "v10", 0.8, 1.0),
    (36.6, 38.6, "v11a", "v11", 0.0, 0.5),
    (38.6, 42.6, "v11b", "v11", 2.3, 0.75),
    (42.6, 45.0, "v12", "v12", 0.2, 1.0),
    (45.0, 49.0, "v13", "v13", 0.2, 0.8),
    (52.5, 55.7, "v14", "v14", 0.6, 1.0),
]
BOARD = [(49.0, 52.5, 0.0), (55.7, 57.2, 9.0)]          # (início, fim, tempo interno inicial)

# Overlays por plano: lista de (tipo, aparece_em_s_relativo, args). Posições em px do quadro 1080x1920.
# track: (cx0, cy0, cx1, cy1, tamanho, rótulo) — o alvo desliza de (cx0,cy0) a (cx1,cy1) ao longo do plano.
# card: (x, y, categoria, métrica, estrelas)
OVER = {
    "v03": [("track", .15, (560, 1200, 600, 1180, 360, "#10")), ("card", .35, (60, 300, "TÁTICO", "DUELO 1X1", 4))],
    "v04": [("track", .1, (520, 560, 520, 540, 300, "#4")), ("card", .3, (600, 1150, "TÁTICO", "INTERCEPTAÇÕES", 3)),
            ("card", .9, (600, 1310, "FÍSICO", "DUELOS AÉREOS", 4))],
    "v05": [("track", .2, (700, 1150, 620, 1250, 340, "#10")), ("card", .5, (60, 380, "TÁTICO", "DESARME", 5)),
            ("card", 2.6, (60, 540, "RESILIÊNCIA", "RECUPERAÇÃO", 4))],
    "v06": [("track", .2, (420, 1050, 520, 1000, 380, "#8")), ("card", .5, (560, 380, "TÁTICO", "LEITURA DE JOGO", 5)),
            ("card", 2.6, (560, 540, "TÉCNICO", "PASSE LONGO", 4))],
    "v07": [("track", .1, (620, 1050, 620, 1080, 440, "#11")), ("card", .25, (40, 200, "TÉCNICO", "DOMÍNIO", 4)),
            ("card", .8, (40, 360, "TÉCNICO", "AJUSTE CORPORAL", 3))],
    "v08": [("track", .1, (500, 1100, 560, 1100, 460, "#11")), ("card", .25, (600, 180, "TÉCNICO", "CONDUÇÃO", 4)),
            ("card", .8, (600, 340, "FÍSICO", "FORÇA", 3))],
    "v09": [("track", .1, (680, 1100, 700, 1050, 380, "#11")), ("card", .3, (50, 260, "FÍSICO", "MUDANÇA DE RITMO", 5)),
            ("card", 1.1, (50, 420, "FÍSICO", "VELOCIDADE", 5))],
    "v10": [("track", .2, (530, 1000, 530, 950, 300, "#10")), ("card", .4, (50, 400, "RESILIÊNCIA", "RESISTÊNCIA FÍSICA", 5))],
    "v11b": [("track", .1, (620, 1050, 640, 1050, 480, "#9")), ("card", .3, (540, 180, "TÁTICO", "ATIVIDADE SEM BOLA", 4)),
             ("card", 1.0, (540, 340, "TÁTICO", "MOBILIDADE", 3)), ("card", 1.7, (540, 500, "TÉCNICO", "PASSE CURTO", 4))],
    "v12": [("track", .1, (700, 800, 720, 780, 280, "#9")), ("card", .3, (60, 220, "FÍSICO", "JOGO AÉREO", 4))],
    "v13": [("track", .2, (480, 900, 520, 900, 420, "#10")), ("card", .5, (60, 260, "TÉCNICO", "FINALIZAÇÃO", 5))],
}

class Clip:
    """Decodifica um plano em fluxo (um quadro por vez), em cover 1080x1920, com velocidade e corte de entrada."""
    def __init__(self, name, ss, speed, n):
        vf = f"setpts=PTS/{speed},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", os.path.join(CLIPS, name + ".mp4"),
                                   "-vf", vf, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.last = None
    def next(self):
        b = self.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3: self.last = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        return self.last          # se o clipe acabar antes, congela o último quadro

def grade(a):
    """Pretos mais fundos e verde levemente puxado para o LIME da marca."""
    f = a.astype(np.float32) / 255
    f = np.clip((f - .03) * 1.08, 0, 1) ** 1.05
    f = f * np.array([.97, 1.0, .9], np.float32)
    return f * 255

yy, xx = np.mgrid[0:H, 0:W]
VIG = np.clip(1 - .45 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2), .35, 1)[..., None].astype(np.float32)

def overlay_for(name, t, dur):
    """Camada RGBA de cartões/rastreio para o plano `name` em t segundos (relativo ao início do plano)."""
    items = OVER.get(name)
    if not items: return None
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    out = 1 - clamp((t - (dur - .18)) / .18)
    track_pt = None
    for kind, t0, args in items:
        if kind == "track":
            cx0, cy0, cx1, cy1, s, lab = args; u = clamp((t - t0) / max(.1, dur - t0))
            track_pt = (lerp(cx0, cx1, u), lerp(cy0, cy1, u))
            track_box(d, *track_pt, s, lab, t - t0, out)
    for kind, t0, args in items:
        if kind == "card":
            x, y, cat, nm, n = args
            if track_pt:
                edge = (x + 6, y + 132) if x > W / 2 else (x + max(330, int(F7(40).getlength(nm)) + 60), y + 132)
                connector(d, track_pt, edge, t - t0 - .05, out)
            metric_card(d, x, y, cat, nm, n, t - t0, out)
    g = ov.filter(ImageFilter.GaussianBlur(6))
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0)); base.alpha_composite(g); base.alpha_composite(ov)
    return base

# ---------------------------------------------------------------- quadro "ANÁLISE DO LANCE"

PX0, PY0, PX1, PY1 = 190, 300, 890, 1700            # campo vertical
PLAYERS = {"#4": (420, 620), "#8": (540, 930), "#10": (620, 1450), "#9": (560, 520), "#11": (760, 1110)}
LEFT = [("CAMISA 4", 70, "#4", [("INTERCEPTAÇÕES", 3), ("DUELOS AÉREOS", 4)]),
        ("CAMISA 8", 87, "#8", [("PRESSÃO", 4), ("LEITURA DE JOGO", 5), ("PASSE LONGO", 4)]),
        ("CAMISA 10", 92, "#10", [("DUELO 1X1", 4), ("DESARME", 5), ("ENTREGA", 4), ("RECUPERAÇÃO", 4), ("RESISTÊNCIA FÍSICA", 5), ("FINALIZAÇÃO", 5)])]
RIGHT = [("CAMISA 9", 75, "#9", [("ATIVIDADE SEM BOLA", 4), ("MOBILIDADE", 3), ("PASSE CURTO", 4), ("JOGO AÉREO", 4)]),
         ("CAMISA 11", 82, "#11", [("AJUSTE CORPORAL", 3), ("DOMÍNIO", 4), ("CONDUÇÃO", 4), ("FORÇA", 3), ("MUDANÇA DE RITMO", 5), ("VELOCIDADE", 5), ("DRIBLE", 4)])]

def pitch_layer():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = LIME + (200,)
    # entorno: arquibancadas em anéis e quarteirões apagados
    for k, a in enumerate((40, 26, 16)):
        m = 50 + k * 45
        d.rounded_rectangle([PX0 - m, PY0 - m, PX1 + m, PY1 + m], 60 + k * 30, outline=LIME + (a,), width=2)
    for i in range(14):
        for j in range(3):
            for side in (0, 1):
                x = 20 + j * 40 if side == 0 else W - 60 - j * 40
                d.rectangle([x, 120 + i * 120, x + 28, 200 + i * 120], outline=LIME + (14,), width=1)
    cx, cy = (PX0 + PX1) / 2, (PY0 + PY1) / 2; pw = PX1 - PX0
    # faixas de grama (antes das linhas: o fill do PIL sobrescreve o alfa)
    for i in range(10):
        if i % 2: d.rectangle([PX0 + 2, PY0 + i * (PY1 - PY0) / 10, PX1 - 2, PY0 + (i + 1) * (PY1 - PY0) / 10], fill=LIME + (10,))
    d.rectangle([PX0, PY0, PX1, PY1], outline=c, width=3)
    d.line([(PX0, cy), (PX1, cy)], fill=c, width=3)
    d.ellipse([cx - 95, cy - 95, cx + 95, cy + 95], outline=c, width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=c)
    for top in (True, False):
        y0 = PY0 if top else PY1; s = 1 if top else -1
        bw, bh, gw, gh = pw * .6, 230, pw * .28, 85
        d.rectangle([cx - bw / 2, min(y0, y0 + s * bh), cx + bw / 2, max(y0, y0 + s * bh)], outline=c, width=3)
        d.rectangle([cx - gw / 2, min(y0, y0 + s * gh), cx + gw / 2, max(y0, y0 + s * gh)], outline=c, width=3)
        d.arc([cx - 90, y0 + s * bh - 90, cx + 90, y0 + s * bh + 90], 0 if top else 180, 180 if top else 360, fill=c, width=3)
        d.rectangle([cx - 45, min(y0, y0 - s * 22), cx + 45, max(y0, y0 - s * 22)], outline=c, width=3)
    return im

PITCH = None

def panel(d, x, y, w, title, score, rows, t, a):
    """Painel de um jogador: cabeçalho (CAMISA n · iSCOUT SCORE nn) + linhas métrica/estrelas que entram em sequência."""
    h = 52 + len(rows) * 36 + 12
    wa = ease(t / .3)
    d.rectangle([x, y, x + w * wa, y + h], fill=INK + (int(215 * a),), outline=LIME + (int(110 * a),), width=1)
    ta = clamp((t - .15) / .25) * a
    if ta <= 0: return h
    d.text((x + 18, y + 27), title, font=F7(26), fill=WHITE + (int(255 * ta),), anchor="lm")
    spaced(d, (x + w - 210, y + 28), "iSCOUT SCORE", F4(13), LIME + (int(200 * ta),), 2)
    sc = int(round(score * ease((t - .2) / .8)))
    d.text((x + w - 18, y + 27), str(sc), font=F7(28), fill=LIME + (int(255 * ta),), anchor="rm")
    d.line([(x + 14, y + 50), (x + w - 14, y + 50)], fill=LIME + (int(60 * ta),), width=1)
    for k, (nm, n) in enumerate(rows):
        ra = clamp((t - .3 - k * .09) / .2) * a
        if ra <= 0: continue
        yy_ = y + 52 + 18 + k * 36
        d.text((x + 18, yy_), nm, font=F4(21), fill=WHITE + (int(225 * ra),), anchor="lm")
        stars(d, x + w - 150, yy_, n, 11, ra, clamp((t - .4 - k * .09) / .4))
    return h

def board(t, dim=1.0):
    global PITCH
    if PITCH is None: PITCH = pitch_layer()
    im = Image.new("RGBA", (W, H), (3, 8, 12, 255))
    # campo: desenha de cima para baixo (revelação) e com leve zoom lento
    pr = ease(t / .7)
    p = PITCH.copy()
    if pr < 1:
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([0, 0, W, int(H * pr)], fill=255)
        p.putalpha(Image.composite(p.split()[3], Image.new("L", (W, H), 0), m))
    g = p.filter(ImageFilter.GaussianBlur(8)); im.alpha_composite(g); im.alpha_composite(p)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    ta = clamp(t / .4)
    spaced(d, (W / 2, 190), "ANÁLISE DO LANCE", F4(30), WHITE + (int(255 * ta),), 8, "m")
    d.line([(W / 2 - 200 * ease(t / .6), 222), (W / 2 + 200 * ease(t / .6), 222)], fill=LIME + (int(255 * ta),), width=3)
    # jogadores
    for k, (lab, (px, py)) in enumerate(PLAYERS.items()):
        pa = ease((t - .5 - k * .08) / .25)
        if pa <= 0: continue
        r = 16 * (2 - pa)
        d.ellipse([px - r, py - r, px + r, py + r], outline=LIME + (int(255 * pa),), width=3)
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=WHITE + (int(255 * pa),))
        d.text((px + 22, py - 18), lab, font=F4(20), fill=WHITE + (int(230 * pa),), anchor="lm")
    # painéis e conectores
    for side, plist in (("L", LEFT), ("R", RIGHT)):
        x = 26 if side == "L" else W - 26 - 470; y = 640 if side == "L" else 700
        for k, (title, score, lab, rows) in enumerate(plist):
            tt = t - .9 - k * .35 - (.15 if side == "R" else 0)
            h = 52 + len(rows) * 36 + 12
            if tt > 0:
                px, py = PLAYERS[lab]; ex = x + 470 if side == "L" else x
                connector(d, (px, py), (ex, y + 26), tt)
                panel(d, x, y, 470, title, score, rows, tt, 1.0)
            y += h + 14
    im.alpha_composite(ov)
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    return a * dim

# ---------------------------------------------------------------- final: frase em três tempos + assinatura

WORDS = ["TODO", "MUNDO", "VIU", "O", "GOL."]

def ending(T):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    if 57.2 <= T < 59.5:                                     # "TODO MUNDO VIU O GOL." palavra por palavra
        f = F4(54); sp = 22
        ws = [f.getlength(w) for w in WORDS]; x = W / 2 - (sum(ws) + sp * (len(WORDS) - 1)) / 2
        for k, w in enumerate(WORDS):
            a = ease((T - 57.35 - k * .3) / .25)
            if a > 0: d.text((x, H / 2 + (1 - a) * 18), w, font=f, fill=WHITE + (int(255 * a),), anchor="lm")
            x += ws[k] + sp
    elif 60.7 <= T < 64.4:
        def line(txt, y, size, a, col=WHITE, rise=16):
            if a > 0: d.text((W / 2, y + (1 - a) * rise), txt, font=F7(size), fill=col + (int(255 * a),), anchor="mm")
        line("O iSCOUT", 640, 92, ease((T - 60.75) / .3))
        line("ANALISOU", 750, 92, ease((T - 61.75) / .3))
        a = ease((T - 62.75) / .25)
        if a > 0:
            s = lerp(1.15, 1.0, a)
            line("O LANCE", 960, int(230 * s), a, LIME, 0)
            line("INTEIRO", 1190, int(230 * s), a, LIME, 0)
            u = ease((T - 63.0) / .5)
            d.line([(W / 2 - 420 * u, 1335), (W / 2 + 420 * u, 1335)], fill=WHITE + (255,), width=5)
        g = im.filter(ImageFilter.GaussianBlur(14)); im2 = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        im2.alpha_composite(g); im2.alpha_composite(im); im = im2
    elif T >= 64.4:
        im = brand_end(T - 64.4)
    return np.asarray(im.convert("RGB")).astype(np.float32)

ICON = LOGO = None

def brand_end(t):
    global ICON, LOGO
    if ICON is None:
        ICON = Image.open(os.path.join(A, "brand/icone.png")).convert("RGBA")
        LOGO = Image.open(os.path.join(A, "brand/iscout-logo-branca.png")).convert("RGBA")
    im = Image.new("RGBA", (W, H), (3, 8, 12, 255))
    k = ease(t / .45); s = int(300 * (.7 + .3 * k)); cx, cy = W / 2, H * .36
    if t < .55:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); r = s * (.62 + .5 * (1 - t / .55))
        ImageDraw.Draw(ov).ellipse([cx - r, cy - r, cx + r, cy + r], outline=LIME + (int(255 * (1 - t / .55)),), width=6)
        im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(10))); im.alpha_composite(ov)
    ic = ICON.resize((s, s), Image.LANCZOS); ic.putalpha(ic.split()[3].point(lambda v: int(v * k)))
    im.alpha_composite(ic, (int(cx - s / 2), int(cy - s / 2)))
    la = ease((t - .5) / .4)
    if la > 0:
        lw = 640; lh = int(lw * LOGO.height / LOGO.width)
        lg = LOGO.resize((lw, lh), Image.LANCZOS); lg.putalpha(lg.split()[3].point(lambda v: int(v * la)))
        im.alpha_composite(lg, (int(W / 2 - lw / 2), int(cy + 210 + (1 - la) * 30)))
    ca = ease((t - 1.2) / .4)
    if ca > 0:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        txt = "Visite iscout.tech"; f = F7(44); bw = int(f.getlength(txt)) + 140; by = H * .64
        d.rounded_rectangle([W / 2 - bw / 2, by, W / 2 + bw / 2, by + 96], 48, fill=LIME + (255,))
        d.text((W / 2, by + 48), txt, font=f, anchor="mm", fill=(8, 12, 8, 255))
        ov.putalpha(ov.split()[3].point(lambda v: int(v * ca))); im.alpha_composite(ov)
    return im

# ---------------------------------------------------------------- render

def main():
    out = sys.argv[1]
    t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    t1 = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
    nfr = int(round(TOTAL * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE)
    rng = np.random.default_rng(5); cur = None
    for f in range(int(round(t0 * FPS)), min(nfr, int(round(t1 * FPS)))):
        T = f / FPS
        sh = next((s for s in SHOTS if s[0] <= T < s[1]), None)
        bd = next((b for b in BOARD if b[0] <= T < b[1]), None)
        if sh:
            st, en, key, name, ss, sp = sh
            if cur is None or cur[0] != key:
                skip = T - st                               # começo no meio do plano (render parcial)
                cur = (key, Clip(name, ss + skip * sp, sp, int(round((en - T) * FPS)) + 2))
            a = grade(cur[1].next())
            ov = overlay_for(key, T - st, en - st)
            if ov is not None:
                o = np.asarray(ov).astype(np.float32); al = o[..., 3:] / 255
                a = a * (1 - al) + o[..., :3] * al
            a = a * VIG
        elif bd:
            cur = None
            a = board(T - bd[0] + bd[2], 1.0 if bd[2] == 0 else .85) * VIG
        else:
            cur = None
            a = ending(T)
        a = a + rng.normal(0, 3.5, (H, W, 1)).astype(np.float32)
        p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main()
