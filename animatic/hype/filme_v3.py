"""Filme iSCOUT V3 — revisão do feedback de Bernardo Canto (08/11/2026), mesmo roteiro, voz e timeline da V2.

Mudanças em relação à V2 (ver docs/revisao-v3.md):
- cenas em cor natural e vibrante: sem overlay verde/P&B, sem fumaça, halo ou glitch; verde da marca só em
  lettering, cartões, telas do app, radar e linhas de marca;
- ambientes "decrépitos" substituídos por instalações esportivas cuidadas (novas imagens + footage do site);
- radar animado das 5 dimensões (nomenclatura do painel de análise: Técnica, Tática, Físico, Resiliência,
  Potencial), valores ilustrativos;
- trilha nova, mais energética (mix em out/v3/mix3.wav).

Uso: FMT=.. SRCWA=.. PORT=<out/hype> V2=<out/v2> V3=<out/v3> FONTDIR=.. SCREENS=.. DEMO=.. python3 filme_v3.py <saida.mp4>
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import filme, filme_v2
from filme import brand, LIME, A
from filme_v2 import T, card, CAPS, demo_shot, shots as _shots, NARR_IN, TOTAL
from fx import W, H, FPS, VERT, font, lum

V3 = os.environ["V3"]
G = LIME

def vivid(a):
    """Cor natural com um pouco mais de vida: saturação +12 %, contraste suave. Nada de tinta verde."""
    l = lum(a)[..., None]
    out = l + (a - l) * 1.12
    return np.clip((out - 128) * 1.05 + 131, 0, 255)

# todas as gradações herdadas passam a ser naturais
filme.nat = vivid
filme.duo = lambda a, mix=1.0: vivid(a)          # fundo desfocado dos planos de celular

def v3(name): return os.path.relpath(os.path.join(V3, name), os.environ["PORT"])
def ref(name): return os.path.relpath(os.path.join(A, "references", name), os.environ["PORT"])

# ---------- radar das 5 dimensões ----------
DIMS = ["TÉCNICA", "TÁTICA", "FÍSICO", "RESILIÊNCIA", "POTENCIAL"]
VALS = [.74, .68, .63, .70, .66]           # ilustrativos
POT = [.86, .82, .76, .84, .90]            # margem de evolução ilustrativa
AXIS_T = [41.76, 42.46, 43.14, 43.9, 44.82]   # palavra falada (s da locução)
NAVY = None

def navy():
    global NAVY
    if NAVY is None:   # cor de fundo da própria tela do app (não inventada)
        NAVY = Image.open(os.path.join(os.environ["SCREENS"], "4.2.1-interna-performance.png")).convert("RGB").getpixel((30, 420))
    return NAVY

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3

def radar(im, cx, cy, R, reveal, grow, pot=0.0, active=None, labels=True, k=1.0):
    """reveal[i]: eixo i desenhado (0..1); grow[i]: vértice i no valor (0..1); pot: contorno do potencial (0..1)."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    ang = [-math.pi / 2 + 2 * math.pi * i / 5 for i in range(5)]
    P = lambda i, r: (cx + math.cos(ang[i]) * R * r, cy + math.sin(ang[i]) * R * r)
    for ring in (.25, .5, .75, 1):
        pts = [P(i, ring) for i in range(5) if reveal[i] > 0]
        if len(pts) > 1: d.line(pts + ([pts[0]] if len(pts) == 5 else []), fill=(255, 255, 255, 45), width=max(1, int(2 * k)))
    for i in range(5):
        if reveal[i] <= 0: continue
        d.line([P(i, 0), P(i, ease(reveal[i]))], fill=(255, 255, 255, 90), width=max(1, int(2 * k)))
    vs = [P(i, VALS[i] * ease(grow[i])) for i in range(5)]
    if any(g > 0 for g in grow):
        d.polygon(vs, fill=LIME + (70,)); d.line(vs + [vs[0]], fill=LIME + (255,), width=max(2, int(4 * k)))
        for i in range(5):
            if grow[i] > 0:
                r = (9 if i == active else 6) * k
                d.ellipse([vs[i][0] - r, vs[i][1] - r, vs[i][0] + r, vs[i][1] + r], fill=LIME + (255,))
    if pot > 0:   # potencial: contorno tracejado que se abre a partir do polígono atual
        pp = [P(i, VALS[i] + (POT[i] - VALS[i]) * ease(pot)) for i in range(5)] + [None]
        pp[-1] = pp[0]
        for a_, b_ in zip(pp, pp[1:]):
            for s in range(0, 10, 2):
                u0, u1 = s / 10, (s + 1) / 10
                d.line([(a_[0] + (b_[0] - a_[0]) * u0, a_[1] + (b_[1] - a_[1]) * u0), (a_[0] + (b_[0] - a_[0]) * u1, a_[1] + (b_[1] - a_[1]) * u1)],
                       fill=(255, 255, 255, int(230 * min(1, pot * 2))), width=max(2, int(3 * k)))
    if labels:
        f = font(int(30 * k))
        for i in range(5):
            if grow[i] <= 0: continue        # rótulo entra junto com o valor, na palavra falada
            x, y = P(i, 1.18); a = int(255 * min(1, grow[i] * 2))
            col = (LIME if i == active else (235, 240, 245)) + (a,)
            d.text((x, y), DIMS[i], font=f, anchor="mm", fill=col)
    im.alpha_composite(ov)

def radar_shot(n, t0, mode):
    """mode 'build': eixos e valores entram no tempo de cada palavra; 'pot': polígono + potencial se abrindo."""
    out = []
    k = H / 804; cx, cy, R = W / 2, H * .50, H * .30
    for i in range(n):
        tn = t0 + i / FPS - NARR_IN
        im = Image.new("RGBA", (W, H), navy() + (255,))
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # brilho suave de marca atrás do radar
        ImageDraw.Draw(g).ellipse([cx - R * 1.3, cy - R * 1.3, cx + R * 1.3, cy + R * 1.3], fill=LIME + (22,))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(R * .4)))
        if mode == "build":
            reveal = [ease((tn - (AXIS_T[0] - 1.5) - .12 * j) / .6) for j in range(5)]   # grade surge em "cinco dimensões"
            grow = [ease((tn - AXIS_T[j]) / .45) for j in range(5)]
            act = max([j for j in range(5) if tn >= AXIS_T[j] - .1], default=None)
            radar(im, cx, cy, R, reveal, grow, active=act, k=k)
            title_txt = ("5 DIMENSÕES", min(1, i / 8))
        else:
            radar(im, cx, cy, R, [1] * 5, [1] * 5, pot=ease((tn - 61.84) / 2.2), active=4, k=k)
            title_txt = ("EVOLUÇÃO", min(1, i / 8))
            # legenda do gráfico
            d = ImageDraw.Draw(im); f = font(int(26 * k)); lx, ly = W * .78, H * .40
            d.rectangle([lx, ly, lx + 34 * k, ly + 8 * k], fill=LIME + (255,)); d.text((lx + 46 * k, ly + 4 * k), "atual", font=f, anchor="lm", fill=(235, 240, 245))
            for s in range(3): d.rectangle([lx + s * 12 * k, ly + 44 * k, lx + s * 12 * k + 7 * k, ly + 50 * k], fill=(255, 255, 255))
            d.text((lx + 46 * k, ly + 47 * k), "potencial", font=f, anchor="lm", fill=(235, 240, 245))
        d = ImageDraw.Draw(im)
        d.text((W * .06, H * .10), title_txt[0], font=font(int(56 * k)), anchor="lm", fill=LIME + (int(255 * title_txt[1]),))
        d.text((W * .06, H * .92), "Valores ilustrativos", font=font(int(22 * k)), anchor="lm", fill=(200, 208, 220, 200))
        out.append(im)
    return out

def mini_radar(im, active, a):
    """Radar pequeno no canto durante os cartões: mostra qual dimensão está em foco."""
    if a <= 0: return
    k = H / 804; R = 92 * k; cx, cy = W - R * 1.9, R * 1.75
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle([cx - R * 1.7, cy - R * 1.55, cx + R * 1.7, cy + R * 1.6], int(20 * k), fill=navy() + (int(215 * a),))
    im.alpha_composite(bg)
    radar(im, cx, cy, R, [a] * 5, [a] * 5, active=active, labels=False, k=k * .6)

# ---------- timeline (mesmos tempos da V2; trocas de imagem e gradação) ----------
FAST = [("vid", "wa3.mp4", 4.9, .4), ("img", v3("kids.png")), ("vid", "wa5.mp4", 6.0, .4), ("ast", "v2-panorama-sm.mp4", 2.0, .4),
        ("vid", "wa1.mp4", 3.3, .4), ("img", v3("club.png")), ("vid", "wa2.mp4", 3.8, .4), ("img", v3("p_b1.png")),
        ("ast", "mock-coach-tablet.mp4", 3.0, .4), ("img", v3("p_a1.png"))]

SHOTS = [
    # 1 · ABERTURA — campo com IA (pedido da V2) mantido; daqui em diante cor natural
    (0.0, ("field", 10.8), "none", {}),
    (T(10.0), ("img", v3("p_b2.png")), "nat", dict(push=.05)),
    (T(12.44), ("img", v3("p_a1.png")), "nat", dict(push=.06)),
    (T(14.92), ("img", v3("kids.png")), "nat", dict(push=.05)),
    (T(18.6), ("img", ref("soccer-training-hero.jpg")), "nat", dict(push=.05)),
    # 2 · ENTRADA NO APP — telas reais sobre a família em cor natural
    (T(20.08), ("phone", "mock-family-app.mp4", 1.0, "2.4.1-atleta-dados-pessoais.png"), None, {}),
    (T(24.12), ("phone", "mock-family-app.mp4", 2.5, "2.4.2-atleta-dados-tecnicos.png"), None, {}),
    (T(27.8), ("phone", "mock-family-app.mp4", 3.5, "2.4.3-atleta-videos.png"), None, {}),
    (T(30.8), ("phone", "mock-family-app.mp4", 4.5, "4.2.0-perfil-atleta.png"), None, {}),
    # 3 · CINCO DIMENSÕES — radar animado + cartões sobre lances reais
    (T(34.4), ("ast", "mock-family-app.mp4", 2.0, 1.6), "nat", dict(push=.05)),
    (T(36.0), ("phone", "mock-family-app.mp4", 5.0, "4.2.1-interna-performance.png"), None, {}),
    (T(40.12), ("radar", "build"), None, {}),
    (T(45.88), ("vid", "wa1.mp4", 4.4, 2.6), "nat", dict(card=("01", "TÉCNICA", "domínio · passe · drible · finalização"), dim=0)),
    (T(48.4), ("vid", "wa1.mp4", 3.0, 3.7), "nat", dict(card=("02", "TÁTICA", "leitura de jogo · tomada de decisão"), dim=1)),
    (T(52.08), ("vid", "wa3.mp4", 4.3, 3.3), "nat", dict(card=("03", "FÍSICO", "duelos · disputas · intensidade"), dim=2)),
    (T(54.9), ("vid", "wa5.mp4", 0.2, 4.1), "nat", dict(card=("04", "RESILIÊNCIA", "constância · mesmo sob pressão"), dim=3)),
    (T(58.92), ("img", v3("p_a2.png")), "nat", dict(push=.06, card=("05", "POTENCIAL", "margem de evolução"), dim=4)),
    (T(61.84), ("radar", "pot"), None, {}),
    # 4 · VÍDEOS E REGISTROS — captação em ambientes cuidados -> análise real
    (T(65.68), ("vid", "wa2.mp4", 3.0, 1.62), "nat", dict(push=.05)),
    (T(67.3), ("ast", "v2-panorama-sm.mp4", 1.0, .7), "nat", dict(hud=True)),
    (T(68.0), ("ast", "v2-panorama-sm.mp4", 3.0, 2.16), "nat", dict(push=.04, hud=True)),
    (T(70.16), ("demo", 1.0), None, {}),
    (T(75.8), ("phone", "mock-family-app.mp4", 3.0, "4.2.9-player-video.png"), None, {}),
    # 5 · ACOMPANHAMENTO
    (T(79.56), ("vid", "wa4.mp4", 2.0, 5.4), "nat", dict(crop=(1.35, .30, .22))),
    (T(84.88), ("ast", "mock-coach-tablet.mp4", 1.0, 4.9), "nat", dict(push=.05)),
    (T(89.74), ("phone", "mock-family-app.mp4", 5.0, "4.3.0-relatorio.png"), None, {}),
    # 6 · ESCOLINHAS, CLUBES E MARCAS
    (T(93.16), ("img", v3("club.png")), "nat", dict(push=.05)),
    (T(97.68), ("img", ref("youth-soccer-academy.jpg")), "nat", dict(push=.05)),
    (T(101.02), ("phone", "mock-family-app.mp4", 0.5, "C3.0-perfil-atleta-clube.png"), None, {}),
    # 7 · FECHAMENTO
    (T(104.38), ("img", v3("p_b2.png")), "nat", dict(push=.07)),
    *[(T(107.6 + .4 * k), s, "nat", dict(hud=s[1] == "v2-panorama-sm.mp4")) for k, s in enumerate(FAST)],
    (T(111.56), ("img", v3("p_a1.png")), "nat", dict(push=.06)),
    (T(113.76), ("img", v3("p_b1.png")), "nat", dict(push=.06)),
    (T(116.18), ("img", v3("p_a2.png")), "nat", dict(push=.06)),
    (T(118.6) - 0.8, "converge", None, {}),
    (T(118.6), "brand", None, {}),
]
filme_v2.SHOTS = SHOTS

# legenda extra para o bloco do potencial (o cartão já não traz "sem prometer carreira")
CAPS.append((65.5, " · ", [(61.84, "SEM PROMETER CARREIRA"), (63.26, "ESPAÇO REAL DE CRESCIMENTO", G)]))
CAPS.sort(key=lambda c: c[2][0][0])
# cenas claras e naturais: em vez de faixa atrás do texto, um degradê suave na base do quadro (terço inferior,
# até ~70 % de escuro) que entra e sai junto com a legenda — legível sem "tarja" sobre a imagem
CAPS[:] = [tuple(c[:3]) for c in CAPS]
_SCRIM = None

def caption(im, tf):
    global _SCRIM
    tn = tf - NARR_IN
    for end, sep, parts in CAPS:
        if parts[0][0] - .3 <= tn < end + .3:
            a = min(1, max(0, (tn - parts[0][0] + .3) / .3)) * min(1, max(0, (end + .3 - tn) / .3))
            if _SCRIM is None:
                y0 = int(H * .62); r = np.clip((np.arange(H) - y0) / (H - y0), 0, 1) ** 1.4 * .72
                _SCRIM = np.repeat((r * 255)[:, None], W, 1).astype(np.float32)
            m = Image.fromarray((_SCRIM * a).astype(np.uint8))
            im.alpha_composite(Image.merge("RGBA", (*[Image.new("L", (W, H), 0)] * 3, m)))
            break
    filme_v2.caption(im, tf)

def render(d, s, g, o, seed, t0):
    n = int(round(d * FPS))
    if s[0] == "radar": return radar_shot(n, t0, s[1])
    o2 = {k: v for k, v in o.items() if k != "dim"}
    frs = filme_v2.render(d, s, g, o2, seed)
    if "dim" in o:
        for i, im in enumerate(frs): mini_radar(im, o["dim"], min(1, i / 6) * (1 - max(0, (i - n + 5) / 5)))
    return frs

if __name__ == "__main__":
    yy, xx = np.mgrid[0:H, 0:W]
    VIG = np.clip(1 - 0.22 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2), 0.6, 1)[..., None].astype(np.float32)
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
        frs = render(target / FPS - f / FPS, s, g, o, 1 + 37 * k, f / FPS) if s[0] != "field" else render(d, s, g, o, 1, 0)
        for im in frs[:target - f] + [frs[-1]] * max(0, target - f - len(frs)):
            im = im.convert("RGBA"); caption(im, f / FPS)
            a = np.asarray(im.convert("RGB")).astype(np.float32) * VIG + rng.normal(0, 3, (H, W, 1)).astype(np.float32)
            if 48 <= f < BRAND_AT and not o.get("hud") and s[0] != "radar":
                al = BUGA[..., 3:] / 255
                a[BY:BY + 68, BX:BX + 68] = a[BY:BY + 68, BX:BX + 68] * (1 - al) + BUGA[..., :3] * al
            p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); f += 1
    for im in brand(TOTAL - f, "Transformando o futuro", "do futebol de base.", ("Explore nosso app", "iscout.tech")):
        a = np.asarray(im.convert("RGB")).astype(np.float32) + rng.normal(0, 3, (H, W, 1)).astype(np.float32)
        p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); f += 1
    p.stdin.close(); p.wait()
    print(f, "frames")
