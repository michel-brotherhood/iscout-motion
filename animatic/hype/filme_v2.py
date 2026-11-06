"""Filme iSCOUT V2 — 2:07 narrado (roteiro docs/roteiro-v2.md), 24 fps, FMT=239 ou 169.

Uso: FMT=.. SRCWA=<clipes wa*.mp4> PORT=<out/hype> V2=<out/v2> FONTDIR=<ttf> SCREENS=<telas> python3 filme_v2.py <saida.mp4>
Os tempos de cada plano vêm da transcrição da locução (atempo 1,12, entra em NARR_IN s), então
cada corte cai no início da frase correspondente.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
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

# (início no filme, fonte, gradação, opções)
SHOTS = [
    # 1 · ABERTURA — o campo nasce com IA
    (0.0, ("field", 10.8), "none", dict(txt=("TODO TALENTO COMEÇA EM ALGUM LUGAR.", 74, .86, False), tin=1.0, tout=4.6)),
    (T(4.6), None, None, dict(txt=("SORTE. INDICAÇÃO. VISIBILIDADE LOCAL.", 74, .86, False))),   # texto sobre o mesmo plano
    (T(10.0), ("vid", "wa6.mp4", 1.6, 2.4), "bwduo", dict(gl=4, txt=("DEMOCRATIZAR O CAMINHO", 120, .82, False))),
    (T(12.4), ("img", "p4.png"), "duo", dict(push=.06, edges=True, txt=("DESDE CEDO.", 150, .82, False, LIME))),
    (T(14.92), ("img", v2("coach2.png")), "duo", dict(push=.05, txt=("O MELHOR ENSINO DE BASE DO MUNDO", 84, .86, False))),
    (T(17.6), ("img", v2("coach1.png")), "duo", dict(push=.05, txt=("PARA TODOS.", 150, .84, False, LIME))),
    (T(20.08), "flash", None, dict(color=LIME)),
    # 2 · ENTRADA NO APP — cadastro real
    (T(20.2), ("phone", "mock-family-app.mp4", 1.0, "2.4.1-atleta-dados-pessoais.png"), None, dict(txt=("PERFIL EM POUCOS PASSOS", 96, .9, False))),
    (T(24.12), ("phone", "mock-family-app.mp4", 2.5, "2.4.2-atleta-dados-tecnicos.png"), None, dict(txt=("NOME · IDADE · POSIÇÃO · ESCOLA · CIDADE", 70, .9, False))),
    (T(27.8), ("phone", "mock-family-app.mp4", 3.5, "2.4.3-atleta-videos.png"), None, dict(txt=("UM REGISTRO PRÓPRIO", 96, .9, False, LIME))),
    (T(30.8), ("phone", "mock-family-app.mp4", 4.5, "4.2.0-perfil-atleta.png"), None, dict(txt=("DADOS · VÍDEOS · EVOLUÇÃO", 90, .9, False))),
    # 3 · CINCO DIMENSÕES
    (T(34.4), ("ast", "mock-family-app.mp4", 2.0, 2.2), "duolift", dict(push=.05, txt=("A FAMÍLIA ACOMPANHA", 110, .86, False))),
    (T(36.6), ("phone", "mock-family-app.mp4", 5.0, "4.2.1-interna-performance.png"), None, dict(txt=("HISTÓRICO · AVALIAÇÕES · PROGRESSO", 76, .9, False, LIME))),
    (T(40.12), "black", None, dict(txt=("5 DIMENSÕES", 190, .5, False, LIME))),
    (T(41.72), "black", None, dict(txt=("TÉCNICA", 170, .5, True))),
    (T(42.55), "black", None, dict(txt=("TÁTICA", 170, .5, True))),
    (T(43.38), "black", None, dict(txt=("FÍSICA", 170, .5, True))),
    (T(44.21), "black", None, dict(txt=("RESILIÊNCIA", 170, .5, True))),
    (T(45.04), "black", None, dict(txt=("POTENCIAL", 170, .5, False, LIME))),
    (T(45.88), ("vid", "wa1.mp4", 4.4, 2.6), "duo", dict(gl=3, card=("01", "TÉCNICA", "domínio · passe · drible · finalização"))),
    (T(48.4), ("scan", ("vid", "wa1.mp4", 3.0, 3.7)), "scan", dict(card=("02", "TÁTICA", "leitura de jogo · tomada de decisão"))),
    (T(52.08), ("vid", "wa3.mp4", 4.3, 3.3), "duo", dict(gl=3, card=("03", "FÍSICA", "duelos · disputas · intensidade"))),
    (T(55.36), ("vid", "wa5.mp4", 0.2, 3.6), "duo", dict(gl=3, card=("04", "RESILIÊNCIA", "constância · mesmo sob pressão"))),
    (T(58.92), ("img", "p1.png"), "duo", dict(push=.07, v=True, card=("05", "POTENCIAL", "margem de evolução · sem prometer carreira"))),
    # 4 · VÍDEOS E REGISTROS — captura
    (T(65.68), ("img", "c1.png"), "nat", dict(push=.06, hud=True, txt=("TREINOS", 120, .86, False))),
    (T(67.2), ("img", "c2.png"), "nat", dict(push=.06, hud=True, gl=3, txt=("JOGOS", 120, .86, False))),
    (T(68.7), ("img", "c3.png"), "nat", dict(push=.05, hud=True, gl=3, txt=("MOMENTOS IMPORTANTES", 100, .86, False))),
    (T(70.16), ("phone", "mock-family-app.mp4", 1.5, "4.2.2-galeria-videos.png"), None, dict(txt=("TÉCNICA · COMPORTAMENTO · INTENSIDADE · CONSISTÊNCIA", 62, .9, False))),
    (T(75.76), ("phone", "mock-family-app.mp4", 3.0, "4.2.9-player-video.png"), None, dict(txt=("A EVOLUÇÃO FICA CLARA.", 96, .9, False, LIME))),
    # 5 · ACOMPANHAMENTO
    (T(79.96), ("vid", "wa4.mp4", 2.0, 5.0), "duo", dict(crop=(1.35, .30, .22), txt=("FAMÍLIAS · PROFESSORES · PARCEIROS", 80, .84, False))),
    (T(84.92), ("ast", "mock-coach-tablet.mp4", 1.0, 4.8), "duolift", dict(push=.05, txt=("AVALIAÇÕES · INDICADORES · REGISTROS", 76, .86, False))),
    (T(89.72), ("phone", "mock-family-app.mp4", 6.0, "4.3.0-relatorio.png"), None, dict(txt=("PRÓXIMOS PASSOS COM CLAREZA", 86, .9, False, LIME))),
    # 6 · ESCOLINHAS, CLUBES E MARCAS
    (T(93.16), ("img", v2("club1.png")), "duo", dict(push=.05, gl=3, txt=("ESCOLINHAS · CLUBES · MARCAS", 92, .86, False))),
    (T(97.64), ("img", v2("coach1.png")), "duo", dict(push=.05, txt=("MAPEAR TALENTOS · DESENVOLVER COMUNIDADES", 72, .86, False))),
    (T(101.3), ("img", v2("club2.png")), "duo", dict(push=.05, txt=("DADOS · SEGURANÇA · IMPACTO", 96, .86, False, LIME))),
    # 7 · FECHAMENTO — ecossistema + retratos
    (T(104.84), ("img", "p2.png"), "duo", dict(push=.07, v=True, txt=("UM SÓ ECOSSISTEMA", 120, .88, False))),
    *[(T(107.6 + .4 * k), s, "duo", dict(gl=2, hud=s[1] in ("c1.png", "c3.png"))) for k, s in enumerate(FAST)],
    (T(111.6), ("img", "p4.png"), "duo", dict(push=.06, edges=True, txt=("MAIS VISIBILIDADE", 130, .84, False))),
    (T(114.0), ("img", "p3.png"), "duo", dict(push=.06, txt=("MAIS INFORMAÇÃO", 130, .84, False))),
    (T(116.08), ("img", "p1.png"), "duo", dict(push=.06, v=True, txt=("MAIS TRANSPARÊNCIA", 130, .84, False, LIME))),
    (T(118.6) - 0.8, "converge", None, {}),
    (T(118.6), "brand", None, {}),
]

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
            if tin <= t < tout: text_at(im, o["txt"], int((t - tin) * FPS), int((tout - tin) * FPS))
            for e0, ed, tx in o.get("extra", []):
                if e0 <= t < e0 + ed: text_at(im, tx, int((t - e0) * FPS), int(ed * FPS))
            out.append(im)
        return out
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
