"""Filme iSCOUT V4 — feedback do Bernardo (13/11/2026) sobre a V3. Mesmo roteiro, voz, trilha e timeline.

Mudanças:
1. Bloco das 5 dimensões: cada dimensão abre no plano real com o cartão ("01 TÉCNICA"…) e, na palavra-chave
   da locução, corta para uma "janela de análise" com o holograma do vídeo "O lance inteiro" (rastreio +
   cartão de métrica com estrelas). Técnica → domínio, Tática → leitura de jogo, Física → duelo,
   Resiliência → condução sob pressão, Potencial → arrancada (~9 s no total).
   Rótulos do radar ancorados para fora do gráfico (o "POTENCIAL" caía sobre a linha do contorno).
2. Tática: o trecho do wa1 em câmera lenta é cortado antes das "duas bolas que viram uma" (~0:51 da V3).
3. Telas do app sem desfoque: SCREENS deve apontar para a saída de animatic/v4_screens.py.
4. "…atletas … patrocinadores" (1:45): os dois garotos do CT com os uniformes de patrocínio (vídeo novo).
5. Tablet do técnico (1:39): dashboard redesenhado cobrindo o vidro todo (antes sobrava faixa e aparecia um polegar).

Uso: FMT=.. (envs da V3, com SCREENS=<telas v4>) LANCE=<out/lance/clips> python3 filme_v4.py <saida.mp4>
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import filme_v3 as m
import filme_v2
from filme import brand, LIME, A
from filme_v2 import T, shots as _shots, TOTAL
from fx import W, H, FPS

os.environ.setdefault("CLIPS", os.environ.get("LANCE", ""))
import lance_v1 as L          # cartões, estrelas e cantoneiras do vídeo "O lance inteiro"

LANCE = os.environ["LANCE"]
VW, VH = 1080, 1920           # espaço de coordenadas dos overlays do lance (quadro 9:16)

# (clipe, entrada no clipe, velocidade, rastreio (cx0, cy0, cx1, cy1, tam, rótulo), cartões [(cat, métrica, estrelas)])
HOLO = {
    "tec": ("v07", 1.2, 1.0, (620, 1000, 620, 1080, 420, "#8"), [("TÉCNICO", "DOMÍNIO", 4), ("TÉCNICO", "AJUSTE CORPORAL", 4)]),
    "tat": ("v06", 1.8, 1.0, (420, 1050, 520, 1000, 380, "#8"), [("TÁTICO", "LEITURA DE JOGO", 5), ("TÁTICO", "TOMADA DE DECISÃO", 4)]),
    "fis": ("v03", 0.4, 1.0, (560, 1200, 600, 1180, 380, "#8"), [("FÍSICO", "DUELOS", 4), ("FÍSICO", "INTENSIDADE", 5)]),
    "res": ("v08", 0.6, 1.0, (500, 1100, 560, 1100, 460, "#8"), [("RESILIÊNCIA", "SOB PRESSÃO", 5), ("RESILIÊNCIA", "CONSTÂNCIA", 4)]),
    "pot": ("v09", 0.6, 1.0, (680, 1100, 700, 1050, 380, "#8"), [("POTENCIAL", "MARGEM DE EVOLUÇÃO", 5), ("POTENCIAL", "PROJEÇÃO", 4)]),
}

def decode(path, ss, speed, n, w, h, cover):
    sc = f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h}" if cover else f"scale={w}:{h}:flags=lanczos"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", path, "-vf", f"setpts=PTS/{speed},fps={FPS},{sc}",
                          "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    arr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    if len(arr) < n: arr = np.concatenate([arr, np.repeat(arr[-1:], n - len(arr), 0)])
    return arr[:n]

def holo_shot(n, key, dim):
    """Janela de análise: holograma 9:16 nítido no centro, o mesmo clipe desfocado ao fundo, rastreio dentro da
    janela e cartões de métrica à esquerda; mini-radar da dimensão no canto (continuidade com o plano real)."""
    clip, ss, sp, trk, cards = HOLO[key]
    path = os.path.join(LANCE, clip + ".mp4")
    wh = int(H * .84); ww = int(wh * VW / VH) // 2 * 2; wx, wy = int(W * .58 - ww / 2), int(H * .06)
    win = decode(path, ss, sp, n, ww, wh, False)
    bg = decode(path, ss, sp, n, W // 4, H // 4, True)
    k = 1.25 * H / 1080                            # escala dos cartões (16:9 = 1,25; 2.39 ≈ .93)
    out = []
    for i in range(n):
        t = i / FPS; dur = n / FPS
        b = Image.fromarray(bg[i]).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(8))
        im = Image.fromarray((np.asarray(b).astype(np.float32) * .30).astype(np.uint8)).convert("RGBA")
        im.paste(Image.fromarray(win[i]), (wx, wy))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        a_in = L.ease(t / .25)
        d.rectangle([wx - 2, wy - 2, wx + ww + 1, wy + wh + 1], outline=LIME + (int(170 * a_in),), width=2)
        L.spaced(d, (wx, wy - 14 * k), "ANÁLISE iSCOUT", L.F4(int(18 * k)), LIME + (int(230 * a_in),), 4)
        out_a = 1 - L.clamp((t - (dur - .12)) / .12)
        cx0, cy0, cx1, cy1, s, lab = trk; u = L.clamp(t / dur)
        cx = wx + L.lerp(cx0, cx1, u) * ww / VW; cy = wy + L.lerp(cy0, cy1, u) * wh / VH
        L.track_box(d, cx, cy, s * ww / VW, lab, t - .05, out_a)
        # cartões empilhados à esquerda da janela, ligados ao alvo do rastreio
        cw = int(max(L.F7(40).getlength(nm) for _, nm, _ in cards) + 70) * k
        for j, (cat, nm, st) in enumerate(cards):
            t0 = .15 + .45 * j
            x = int(wx - cw - 50 * k); y = int(H * .20 + j * 160 * k)
            L.connector(d, (cx, cy), (x + cw, y + 66 * k), t - t0 - .05, out_a)
            card_scaled(ov, x, y, cat, nm, st, t - t0, out_a, k, cw)
        g = ov.filter(ImageFilter.GaussianBlur(5)); im.alpha_composite(g); im.alpha_composite(ov)
        m.mini_radar(im, dim, min(1, i / 4))
        out.append(im)
    return out

def card_scaled(base, x, y, cat, nm, st, t, out_a, k, cw):
    """L.metric_card desenhado em 1:1 numa camada própria e reduzido por k (cartões menores no 2.39)."""
    if t < 0: return
    ch = 132
    lay = Image.new("RGBA", (int(cw / k) + 4, ch + 4), (0, 0, 0, 0))
    L.metric_card(ImageDraw.Draw(lay), 0, 0, cat, nm, st, t, out_a, w=int(cw / k))
    if k != 1: lay = lay.resize((int(lay.width * k), int(lay.height * k)), Image.LANCZOS)
    base.alpha_composite(lay, (x, int(y)))

# ---------- timeline V4 ----------
def v3img(name): return m.v3(name)

S3 = m.SHOTS
def at(t):            # índice do plano V3 que começa em t (tempo do filme)
    return next(i for i, s in enumerate(S3) if abs(s[0] - t) < 1e-6)

SHOTS = list(S3)
# 1–2 · dimensões: plano real encurtado + janela de análise (inícios em tempo da locução, na palavra-chave)
SPLIT = [(45.88, 47.0, "tec", 0), (48.4, 49.9, "tat", 1), (52.08, 53.6, "fis", 2), (54.9, 57.0, "res", 3), (58.92, 60.0, "pot", 4)]
for t_real, t_holo, key, dim in reversed(SPLIT):
    i = at(T(t_real))
    SHOTS.insert(i + 1, (T(t_holo), ("holo", key), None, dict(dim=dim)))
# 4 · patrocinadores (pedido do Michel, 13/11): os dois garotos do CT (bk1) recriados com os uniformes
#     de patrocínio (bk3_kit.mp4: um de vermelho listrado, outro de azul-marinho); montagem rápida intacta
SHOTS = [(t, ("v3vid", "bk3_kit.mp4") + s[2:], g, o) if isinstance(s, tuple) and s[:2] == ("v3vid", "bk1.mp4") else (t, s, g, o)
         for t, s, g, o in SHOTS]
# 6 · uniformes nas cenas do #8 e nos jogos das dimensões (pedido do Michel, 13/11): o #8 passa a vestir o
#     uniforme azul-marinho (nº 8) e os times do treino, os dois uniformes de patrocínio. Retratos recriados
#     (p_*_kit.png) e trechos do treino regenerados (wa1k.mp4 começa no 0 s do wa1; wa3k no 3,3 s do wa3).
KIT_IMG = {m.v3(n + ".png"): m.v3(n + "_kit.png") for n in ("p_b2", "p_a1", "p_b1", "p_a2")}
KIT_VID = {"wa1.mp4": ("wa1k.mp4", 0.0), "wa3.mp4": ("wa3k.mp4", 3.3)}
def _kit(s):
    if not isinstance(s, tuple): return s
    if s[0] == "img" and s[1] in KIT_IMG: return ("img", KIT_IMG[s[1]]) + s[2:]
    if s[0] in ("vid", "vids") and s[1] in KIT_VID:
        nm, off = KIT_VID[s[1]]; return (s[0], nm, max(0.0, s[2] - off)) + s[3:]
    return s
SHOTS = [(t, _kit(s), g, o) for t, s, g, o in SHOTS]
m.SHOTS[:] = SHOTS                     # filme_v2.SHOTS é a mesma lista

# 5 · tablet do técnico (1:39): dashboard desenhado em código, cobrindo o vidro inteiro (v4_tablet.py)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4_tablet import Tablet as _Tab4
m._TAB = _Tab4(A, m.V3)

_radar3 = m.radar
def radar4(im, cx, cy, R, reveal, grow, pot=0.0, active=None, labels=True, k=1.0):
    _radar3(im, cx, cy, R, reveal, grow, pot=pot, active=active, labels=False, k=k)
    if not labels: return
    import math
    d = ImageDraw.Draw(im); f = m.font(int(30 * k))
    for i in range(5):
        if grow[i] <= 0: continue
        ang = -math.pi / 2 + 2 * math.pi * i / 5; c, s_ = math.cos(ang), math.sin(ang)
        r = R * 1.10; x, y = cx + c * r, cy + s_ * r
        anchor = "mb" if i == 0 else ("lm" if c > .3 else "rm" if c < -.3 else ("mt" if s_ > 0 else "mb"))
        if i in (2, 3): anchor = "lt" if c > 0 else "rt"
        a = int(255 * min(1, grow[i] * 2)); col = (LIME if i == active else (235, 240, 245)) + (a,)
        d.text((x + (12 * k if anchor[0] == "l" else -12 * k if anchor[0] == "r" else 0), y), m.DIMS[i], font=f, anchor=anchor, fill=col)
m.radar = radar4

def render(d, s, g, o, seed, t0):
    n = int(round(d * FPS))
    if s[0] == "holo": return holo_shot(n, s[1], o["dim"])
    return m.render(d, s, g, o, seed, t0)

if __name__ == "__main__":
    yy, xx = np.mgrid[0:H, 0:W]
    VIG = np.clip(1 - 0.22 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2), 0.6, 1)[..., None].astype(np.float32)
    t_a = float(sys.argv[2]) if len(sys.argv) > 2 else 0; t_b = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "20", "-maxrate", "20M", "-bufsize", "40M", "-preset", "medium", "-pix_fmt", "yuv420p", sys.argv[1]],
                         stdin=subprocess.PIPE)
    rng = np.random.default_rng(3); f = 0
    BUG = Image.open(os.path.join(A, "brand/icone.png")).convert("RGBA").resize((68, 68), Image.LANCZOS)
    BUGA = np.asarray(BUG).astype(np.float32); BUGA[..., 3] *= .85
    BX, BY = W - 68 - 36, H - 68 - 30
    BRAND_AT = int(round(SHOTS[-1][0] * FPS))
    for k, (d, s, g, o, t0) in enumerate(_shots()):
        target = int(round((t0 + d) * FPS))
        if (t0 + d) <= t_a or t0 >= t_b: f = target; continue      # render parcial (testes)
        frs = render(target / FPS - f / FPS, s, g, o, 1 + 37 * k, f / FPS) if s[0] != "field" else filme_v2.render(d, s, g, o, 1)
        for im in frs[:target - f] + [frs[-1]] * max(0, target - f - len(frs)):
            im = im.convert("RGBA"); m.caption(im, f / FPS)
            a = np.asarray(im.convert("RGB")).astype(np.float32) * VIG + rng.normal(0, 3, (H, W, 1)).astype(np.float32)
            if 48 <= f < BRAND_AT and not o.get("hud") and s[0] not in ("radar", "holo"):
                al = BUGA[..., 3:] / 255
                a[BY:BY + 68, BX:BX + 68] = a[BY:BY + 68, BX:BX + 68] * (1 - al) + BUGA[..., :3] * al
            p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); f += 1
    if t_b >= SHOTS[-1][0]:
        for im in brand(TOTAL - f, "Transformando o futuro", "do futebol de base.", "Visite iscout.tech", l2y=.735):
            a = np.asarray(im.convert("RGB")).astype(np.float32) + rng.normal(0, 3, (H, W, 1)).astype(np.float32)
            p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); f += 1
    p.stdin.close(); p.wait()
    print(f, "frames")
