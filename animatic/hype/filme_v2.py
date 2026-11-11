"""Filme iSCOUT V2 — 2:07 narrado (roteiro docs/roteiro-v2.md), 24 fps, FMT=239 ou 169.

Uso: FMT=.. SRCWA=<clipes wa*.mp4> PORT=<out/hype> V2=<out/v2> FONTDIR=<ttf> SCREENS=<telas> python3 filme_v2.py <saida.mp4>
Os tempos de cada plano vêm da transcrição da locução (atempo 1,12, entra em NARR_IN s), então
cada corte cai no início da frase correspondente.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import filme
from filme import render_shot, brand, LIME, A
from fx import W, H, FPS, VERT, title, font

V2 = os.environ["V2"]
NARR_IN = 0.8
TOTAL = int(round(127.5 * FPS))
_src = filme.src

def cover(path, start, dur, speed=1.0):
    """Decodifica preenchendo o quadro (scale cover + recorte central), para qualquer FMT."""
    n = int(round(dur * FPS))
    vf = f"setpts={1/speed}*PTS,fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-vf", vf, "-frames:v", str(n),
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    arr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    if len(arr) < n: arr = np.concatenate([arr, np.repeat(arr[-1:], n - len(arr), 0)])
    return [a.astype(np.float32) for a in arr[:n]]

def src(kind, *p):
    if kind == "field": return cover(os.path.join(V2, "field.mp4"), 0, p[0], speed=10.08 / p[0])
    if kind == "ast": return cover(os.path.join(A, "footage", p[0]), p[1], p[2])
    return _src(kind, *p)
filme.src = src

def v2(name): return os.path.relpath(os.path.join(V2, name), os.environ["PORT"])

def card(im, num, label, sub, a):
    """Cartão de dimensão: número + nome + exemplos, alinhado à esquerda no terço inferior."""
    if a <= 0: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    x = int(W * .06); y = int(H * .58); k = H / 804
    d.rectangle([0, y - int(30 * k), int(W * .62), H], fill=(0, 0, 0, 120))
    d.text((x, y), num, font=font(int(56 * k)), anchor="lt", fill=LIME + (255,))
    d.text((x, y + int(64 * k)), label, font=font(int(120 * k)), anchor="lt", fill=(255, 255, 255, 255))
    d.rectangle([x, y + int(205 * k), x + int(160 * k), y + int(211 * k)], fill=LIME + (255,))
    d.text((x, y + int(232 * k)), sub, font=font(int(36 * k)), anchor="lt", fill=(225, 232, 215, 255))
    ov.putalpha(ov.split()[3].point(lambda v: int(v * a))); im.alpha_composite(ov)

T = lambda t: t + NARR_IN      # tempo da locução -> tempo do filme
FAST = [("vid", "wa3.mp4", 4.9, .4), ("img", "c1.png"), ("vid", "wa5.mp4", 6.0, .4), ("img", v2("coach2.png")),
        ("vid", "wa1.mp4", 3.3, .4), ("img", "c3.png"), ("vid", "wa2.mp4", 3.8, .4), ("img", v2("club1.png")),
        ("vid", "wa6.mp4", 2.5, .4), ("img", "p3.png")]

# (início no filme, fonte, gradação, opções) — só imagem; o texto falado vem da trilha de legendas CAPS
SHOTS = [
    # 1 · ABERTURA — o campo nasce com IA
    (0.0, ("field", 10.8), "none", {}),
    (T(10.0), ("vid", "wa6.mp4", 1.6, 2.44), "bwduo", dict(gl=4)),
    (T(12.44), ("img", "p4.png"), "duo", dict(push=.06, edges=True)),
    (T(14.92), ("img", v2("coach2.png")), "duo", dict(push=.05)),
    (T(18.6), ("img", v2("coach1.png")), "duo", dict(push=.05)),
    (T(20.08), "flash", None, dict(color=LIME)),
    # 2 · ENTRADA NO APP — cadastro real
    (T(20.2), ("phone", "mock-family-app.mp4", 1.0, "2.4.1-atleta-dados-pessoais.png"), None, {}),
    (T(24.12), ("phone", "mock-family-app.mp4", 2.5, "2.4.2-atleta-dados-tecnicos.png"), None, {}),
    (T(27.8), ("phone", "mock-family-app.mp4", 3.5, "2.4.3-atleta-videos.png"), None, {}),
    (T(30.8), ("phone", "mock-family-app.mp4", 4.5, "4.2.0-perfil-atleta.png"), None, {}),
    # 3 · CINCO DIMENSÕES
    (T(34.4), ("ast", "mock-family-app.mp4", 2.0, 1.6), "duolift", dict(push=.05)),
    (T(36.0), ("phone", "mock-family-app.mp4", 5.0, "4.2.1-interna-performance.png"), None, {}),
    (T(40.12), "black", None, dict(txt=("5 DIMENSÕES", 160, .5, False, LIME))),
    (T(41.72), "black", None, dict(txt=("TÉCNICA", 140, .5, True))),
    (T(42.42), "black", None, dict(txt=("TÁTICA", 140, .5, True))),
    (T(43.1), "black", None, dict(txt=("FÍSICA", 140, .5, True))),
    (T(43.86), "black", None, dict(txt=("RESILIÊNCIA", 140, .5, True))),
    (T(44.78), "black", None, dict(txt=("POTENCIAL", 140, .5, False, LIME))),
    (T(45.88), ("vid", "wa1.mp4", 4.4, 2.6), "duo", dict(gl=3, card=("01", "TÉCNICA", "domínio · passe · drible · finalização"))),
    (T(48.4), ("scan", ("vid", "wa1.mp4", 3.0, 3.7)), "scan", dict(card=("02", "TÁTICA", "leitura de jogo · tomada de decisão"))),
    (T(52.08), ("vid", "wa3.mp4", 4.3, 3.3), "duo", dict(gl=3, card=("03", "FÍSICA", "duelos · disputas · intensidade"))),
    (T(54.9), ("vid", "wa5.mp4", 0.2, 4.1), "duo", dict(gl=3, card=("04", "RESILIÊNCIA", "constância · mesmo sob pressão"))),
    (T(58.92), ("img", "p1.png"), "duo", dict(push=.07, v=True, card=("05", "POTENCIAL", "margem de evolução · sem prometer carreira"))),
    # 4 · VÍDEOS E REGISTROS — captura -> análise real (demo iSCOUT)
    (T(65.68), ("img", "c1.png"), "nat", dict(push=.06, hud=True)),
    (T(67.3), ("img", "c2.png"), "nat", dict(push=.06, hud=True, gl=3)),
    (T(68.0), ("img", "c3.png"), "nat", dict(push=.05, hud=True, gl=3)),
    (T(70.16), ("demo", 1.0), None, {}),
    (T(75.8), ("phone", "mock-family-app.mp4", 3.0, "4.2.9-player-video.png"), None, {}),
    # 5 · ACOMPANHAMENTO
    (T(79.56), ("vid", "wa4.mp4", 2.0, 5.4), "duo", dict(crop=(1.35, .30, .22))),
    (T(84.88), ("ast", "mock-coach-tablet.mp4", 1.0, 4.9), "duolift", dict(push=.05)),
    (T(89.74), ("phone", "mock-family-app.mp4", 5.0, "4.3.0-relatorio.png"), None, {}),
    # 6 · ESCOLINHAS, CLUBES E MARCAS
    (T(93.16), ("img", v2("club1.png")), "duo", dict(push=.05, gl=3)),
    (T(97.68), ("img", v2("coach1.png")), "duo", dict(push=.05)),
    (T(101.02), ("phone", "mock-family-app.mp4", 0.5, "C3.0-perfil-atleta-clube.png"), None, {}),   # área do clube no app
    # 7 · FECHAMENTO — ecossistema + retratos
    (T(104.38), ("img", "p2.png"), "duo", dict(push=.07, v=True)),
    *[(T(107.6 + .4 * k), s, "duo", dict(gl=2, hud=s[1] in ("c1.png", "c3.png"))) for k, s in enumerate(FAST)],
    (T(111.56), ("img", "p4.png"), "duo", dict(push=.06, edges=True)),
    (T(113.76), ("img", "p3.png"), "duo", dict(push=.06)),
    (T(116.18), ("img", "p1.png"), "duo", dict(push=.06, v=True)),
    (T(118.6) - 0.8, "converge", None, {}),
    (T(118.6), "brand", None, {}),
]

# Legendas sincronizadas com a locução: cada trecho entra no instante em que a palavra é falada
# (tempos da transcrição palavra a palavra, em s da locução). (fim, separador, [(t, trecho, verde?)])
G = LIME
CAPS = [
    (2.3, " ", [(0.0, "TODO TALENTO"), (0.82, "COMEÇA EM ALGUM LUGAR.")], dict(band=True)),   # sobre as linhas do campo
    (9.9, " ", [(5.76, "SORTE."), (6.48, "INDICAÇÃO."), (7.44, "VISIBILIDADE LOCAL.")]),
    (12.3, " ", [(10.16, "O iSCOUT EXISTE"), (11.36, "PARA MUDAR ISSO.")]),
    (14.8, " ", [(12.44, "DEMOCRATIZAR O CAMINHO"), (13.64, "DESDE CEDO.", G)]),
    (18.6, " ", [(16.28, "O MELHOR ENSINO"), (17.24, "DE FUTEBOL DE BASE"), (18.08, "DO MUNDO")]),
    (20.0, " ", [(18.7, "PARA TODOS.", G)]),
    (24.0, " ", [(21.94, "PERFIL EM"), (22.92, "POUCOS PASSOS")]),
    (27.7, " · ", [(24.14, "NOME"), (24.78, "IDADE"), (25.44, "POSIÇÃO"), (26.24, "ESCOLA"), (27.04, "CIDADE")]),
    (30.7, " ", [(29.48, "UM REGISTRO PRÓPRIO", G)]),
    (34.3, " · ", [(30.88, "DADOS"), (31.68, "VÍDEOS"), (32.24, "EVOLUÇÃO", G)]),
    (36.0, " ", [(35.34, "A FAMÍLIA ACOMPANHA")]),
    (40.0, " · ", [(36.12, "POSIÇÃO"), (36.98, "HISTÓRICO"), (37.82, "VÍDEOS"), (38.4, "AVALIAÇÕES"), (39.32, "PROGRESSO", G)]),
    (70.0, " · ", [(67.3, "TREINOS"), (68.0, "JOGOS"), (68.68, "MOMENTOS IMPORTANTES")]),
    (75.7, " · ", [(71.72, "TÉCNICA"), (72.62, "COMPORTAMENTO"), (73.62, "INTENSIDADE"), (74.54, "CONSISTÊNCIA")]),
    (79.4, " ", [(76.06, "COM O TEMPO,"), (78.26, "A EVOLUÇÃO FICA CLARA.", G)]),
    (84.7, " · ", [(79.56, "FAMÍLIAS"), (80.72, "PROFESSORES"), (81.4, "PARCEIROS")]),
    (89.6, " · ", [(84.88, "AVALIAÇÕES"), (85.92, "INDICADORES"), (86.7, "REGISTROS")]),
    (93.0, " · ", [(89.74, "FACILITAM CONVERSAS"), (91.18, "ORIENTAM PRÓXIMOS PASSOS", G)]),
    (97.5, " · ", [(93.34, "ESCOLINHAS"), (94.24, "CLUBES"), (94.7, "MARCAS")]),
    (100.9, " · ", [(98.2, "MAPEAR TALENTOS"), (99.42, "DESENVOLVER COMUNIDADES")]),
    (102.3, " ", [(101.02, "VIABILIZAR PROJETOS")]),
    (104.3, " · ", [(102.4, "DADOS"), (103.2, "SEGURANÇA"), (103.96, "IMPACTO", G)]),
    (105.9, " ", [(104.98, "O iSCOUT CONECTA")]),
    (109.9, " · ", [(106.0, "ATLETAS"), (106.84, "FAMÍLIAS"), (107.56, "ESCOLINHAS"), (108.4, "CLUBES"), (108.9, "PATROCINADORES")]),
    (111.4, " ", [(110.06, "UM SÓ ECOSSISTEMA", G)]),
    (113.7, " ", [(111.56, "MAIS VISIBILIDADE"), (112.62, "PARA QUEM JOGA")]),
    (116.1, " ", [(113.76, "MAIS INFORMAÇÃO"), (114.48, "PARA QUEM ACOMPANHA")]),
    (118.5, " ", [(116.18, "MAIS TRANSPARÊNCIA"), (117.2, "PARA QUEM INVESTE", G)], dict(band=True)),   # sobre as linhas de energia
]
CAP_SIZE = int(50 * H / 804) if not VERT else 48
filme.PHONE_H, filme.PHONE_Y = .76, .03

def caption(im, tf):
    """Desenha o grupo de legenda ativo no tempo de filme tf; layout fixo, cada trecho surge na sua palavra."""
    tn = tf - NARR_IN
    for end, sep, parts, *opt in CAPS:
        if not (parts[0][0] - .05 <= tn < end): continue
        f = font(CAP_SIZE); maxw = W * .86; lines = [[]]; wcur = 0
        for p in parts:   # quebra de linha estável (calculada com todos os trechos)
            txt = p[1]; w = f.getlength(txt); sw = f.getlength(sep) if lines[-1] else 0
            if lines[-1] and wcur + sw + w > maxw: lines.append([]); wcur = 0; sw = 0
            lines[-1].append(p); wcur += sw + w
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        lh = CAP_SIZE * 1.15; y0 = H * .86 - (len(lines) - 1) * lh / 2
        for k, ln in enumerate(lines):
            tot = sum(f.getlength(p[1]) for p in ln) + f.getlength(sep) * (len(ln) - 1); x = W / 2 - tot / 2
            for j, p in enumerate(ln):
                a = min(1, max(0, (tn - p[0]) / .12)) * min(1, max(0, (end - tn) / .2))
                col = (p[2] if len(p) > 2 else (255, 255, 255)) + (int(255 * a),)
                if j: d.text((x, y0 + k * lh), sep, font=f, anchor="lm", fill=(255, 255, 255, int(170 * a))); x += f.getlength(sep)
                d.text((x, y0 + k * lh), p[1], font=f, anchor="lm", fill=col); x += f.getlength(p[1])
        if opt and opt[0].get("band"):
            # faixa escura difusa atrás do texto: contraste sobre fundos claros/verdes
            ga = min(1, max(0, (tn - parts[0][0]) / .12)) * min(1, max(0, (end - tn) / .2))
            # a faixa cresce com o texto: cobre só até o fim do trecho já falado (suave, pela opacidade do trecho)
            xa, xb, rows = W, 0, []
            for k, ln in enumerate(lines):
                tot = sum(f.getlength(p[1]) for p in ln) + f.getlength(sep) * (len(ln) - 1); x = W / 2 - tot / 2; x0, x1 = x, None
                for j, p in enumerate(ln):
                    if j: x += f.getlength(sep)
                    w_ = f.getlength(p[1]); pa = min(1, max(0, (tn - p[0]) / .25))
                    if pa > 0: x1 = x + w_ * (1 - (1 - pa) ** 3) if x1 is None or pa < 1 else x + w_
                    x += w_
                if x1 is not None: xa, xb = min(xa, x0), max(xb, x1); rows.append(k)
            bd = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            if rows:
                ImageDraw.Draw(bd).rounded_rectangle([xa - CAP_SIZE * .7, y0 + rows[0] * lh - lh * .75, xb + CAP_SIZE * .7, y0 + rows[-1] * lh + lh * .75],
                                                     CAP_SIZE // 2, fill=(0, 0, 0, int(225 * ga)))
            im.alpha_composite(bd.filter(ImageFilter.GaussianBlur(CAP_SIZE * .3)))
        sh = ov.split()[3].filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * .5))   # sombra discreta, colada à letra
        im.alpha_composite(Image.merge("RGBA", (*[Image.new("L", (W, H), 0)] * 3, sh))); im.alpha_composite(ov)
        return

DEMO = os.environ.get("DEMO", "")

def demo_shot(n, start, seed):
    """Vídeo real de análise do iSCOUT num quadro de monitor sobre fundo desfocado."""
    fh = int(H * (.66 if not VERT else .30)); fw = int(fh * 16 / 9); x0 = (W - fw) // 2; y0 = int(H * .07)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", DEMO, "-vf", f"fps={FPS},scale={fw}:{fh}",
                          "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, fh, fw, 3)
    bg = [Image.fromarray(np.clip(f.astype(np.float32) * .35, 0, 255).astype(np.uint8)).resize((W, H)).filter(ImageFilter.GaussianBlur(24)) for f in fr[::12]]
    m = Image.new("L", (fw, fh)); ImageDraw.Draw(m).rounded_rectangle([0, 0, fw - 1, fh - 1], 18, fill=255)
    out = []
    for i in range(n):
        f = fr[min(i, len(fr) - 1)]; e = 1 - (1 - min(1, i / 10)) ** 3
        b = bg[min(i // 12, len(bg) - 1)].convert("RGBA"); d = ImageDraw.Draw(b)
        yy = int(y0 + (1 - e) * H * .25)
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).rounded_rectangle([x0 - 4, yy - 4, x0 + fw + 4, yy + fh + 4], 22, outline=LIME + (255,), width=4)
        b.alpha_composite(glow.filter(ImageFilter.GaussianBlur(12))); b.alpha_composite(glow)
        b.paste(Image.fromarray(f), (x0, yy), m)
        out.append(b)
    return out

def shots():
    """Resolve durações pelos inícios; um plano com fonte None só troca o texto do plano anterior."""
    out = []
    for k, (t0, s, g, o) in enumerate(SHOTS[:-1]):
        d = SHOTS[k + 1][0] - t0
        if s is None: out[-1][3].setdefault("extra", []).append((t0 - out[-1][4], d, o["txt"])); out[-1][0] += d; continue
        out.append([d, s, g, o, t0])
    return out

def text_at(im, txt, i, n):
    s, size, y, outline = txt[:4]; col = txt[4] if len(txt) > 4 else (255, 255, 255)
    a = min(1, i / 6) * (1 - max(0, (i - n + 6) / 6))
    title(im, s, size, H * y, outline=outline, a=a, color=col)

def render(d, s, g, o, seed):
    n = int(round(d * FPS))
    if s[0] == "field":   # plano do campo: sem gradação (as cores já são da marca); textos com janela própria
        frs = src("field", d)[:n]; out = []
        tin, tout = o.get("tin", 0), o.get("tout", d)
        for i, fr in enumerate(frs):
            im = Image.fromarray(fr.astype(np.uint8)).convert("RGBA"); im = filme.zoom(im, 1 + .04 * i / n)
            t = i / FPS
            if "txt" in o and tin <= t < tout: text_at(im, o["txt"], int((t - tin) * FPS), int((tout - tin) * FPS))
            for e0, ed, tx in o.get("extra", []):
                if e0 <= t < e0 + ed: text_at(im, tx, int((t - e0) * FPS), int(ed * FPS))
            out.append(im)
        return out
    if s[0] == "demo": return demo_shot(n, s[1], seed)
    if g == "bwduo": g = "mix"
    o2 = {k: v for k, v in o.items() if k != "card"}
    frs = render_shot(d, s, g or "duo", o2, seed)
    if "card" in o:
        for i, im in enumerate(frs): card(im, *o["card"], min(1, i / 6) * (1 - max(0, (i - n + 5) / 5)))
    return frs

if __name__ == "__main__":
    yy, xx = np.mgrid[0:H, 0:W]
    VIG = np.clip(1 - 0.5 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2), 0.3, 1)[..., None].astype(np.float32)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "20", "-maxrate", "20M", "-bufsize", "40M", "-preset", "medium", "-pix_fmt", "yuv420p", sys.argv[1]],
                         stdin=subprocess.PIPE)
    rng = np.random.default_rng(3); f = 0
    BUG = Image.open(os.path.join(A, "brand/icone.png")).convert("RGBA").resize((68, 68), Image.LANCZOS)
    BUGA = np.asarray(BUG).astype(np.float32); BUGA[..., 3] *= .85
    BX, BY = W - 68 - 36, H - 68 - 30
    BRAND_AT = int(round(SHOTS[-1][0] * FPS))
    for k, (d, s, g, o, t0) in enumerate(shots()):
        target = int(round((t0 + d) * FPS))          # fecha a conta em frames absolutos (sem deriva)
        frs = render(target / FPS - f / FPS, s, g, o, 1 + 37 * k) if s[0] != "field" else render(d, s, g, o, 1)
        for im in frs[:target - f] + [frs[-1]] * max(0, target - f - len(frs)):
            im = im.convert("RGBA"); caption(im, f / FPS)
            a = np.asarray(im.convert("RGB")).astype(np.float32) * VIG + rng.normal(0, 6, (H, W, 1)).astype(np.float32)
            if 48 <= f < BRAND_AT and not o.get("hud"):
                al = BUGA[..., 3:] / 255
                a[BY:BY + 68, BX:BX + 68] = a[BY:BY + 68, BX:BX + 68] * (1 - al) + BUGA[..., :3] * al
            p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); f += 1
    for im in brand(TOTAL - f, "Transformando o futuro", "do futebol de base.", ("Explore nosso app", "iscout.tech")):
        a = np.asarray(im.convert("RGB")).astype(np.float32) + rng.normal(0, 6, (H, W, 1)).astype(np.float32)
        p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); f += 1
    p.stdin.close(); p.wait()
    print(f, "frames")
