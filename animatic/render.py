"""Animatic iSCOUT — 30 s / 900 frames / 30 fps.

Uso: python3 render.py <h|v> <scale> [--frames a,b,c] [--clean]
  h = 1920x1080, v = 1080x1920; scale 0.5 => animatic em baixa resolução.
  --clean remove o HUD de revisão (usado nos styleframes).
Frames de footage pré-extraídos em $SRC/<clip>/%04d.jpg (30 fps).
"""
import math, os, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "..", "assets")
SRC = os.environ["SRC"]
FONT = os.environ["FONTDIR"]
FPS, TOTAL = 30, 900

# Paleta amostrada dos assets (provisória até o guia de marca oficial)
NAVY = (11, 17, 61); BLUE = (11, 45, 88); CYAN = (68, 196, 200)
LIME = (205, 213, 92); WHITE = (255, 255, 255)


# ---------- utilidades ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(f, a, b): return clamp((f - a) / max(1, b - a))
def ease(t): return 1 - (1 - t) ** 3                     # easeOutCubic
def inout(t): return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t

@lru_cache(64)
def font(size, bold=True):
    return ImageFont.truetype(os.path.join(FONT, "Sora-700.ttf" if bold else "Sora-400.ttf"), size)

@lru_cache(32)
def img(path):
    return Image.open(os.path.join(A, path)).convert("RGBA")

@lru_cache(256)
def clip(name, i):
    n = len(os.listdir(os.path.join(SRC, name)))
    return Image.open(os.path.join(SRC, name, "%04d.jpg" % (int(i) % n + 1))).convert("RGBA")

def cover(im, W, H, zoom=1.0, fx=0.5, fy=0.5):
    """Crop tipo object-fit:cover com zoom e ponto focal (fx,fy em 0..1)."""
    s = max(W / im.width, H / im.height) * zoom
    w, h = im.width * s, im.height * s
    x = clamp(fx * w - W / 2, 0, w - W); y = clamp(fy * h - H / 2, 0, h - H)
    return im.resize((int(w + 1), int(h + 1)), Image.LANCZOS).crop((int(x), int(y), int(x) + W, int(y) + H))

def darken(im, a):
    return Image.blend(im, Image.new("RGBA", im.size, NAVY + (255,)), a)

def text(d, xy, s, size, fill=WHITE, alpha=1.0, anchor="la", bold=True):
    if alpha <= 0: return
    d.text(xy, s, font=font(size, bold), fill=fill + (int(255 * alpha),), anchor=anchor)

def headline(base, s, W, H, a, V, y=None, size=None):
    """Título com entrada vertical curta e véu de contraste por trás."""
    if a <= 0: return
    size = size or int((0.062 if not V else 0.034) * H)
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    y = y if y is not None else (0.80 * H if not V else 0.70 * H)
    dy = (1 - ease(a)) * size * 0.6
    maxw = W * (0.82 if V else 0.9)
    lines = wrap(s, size, maxw)
    for i, ln in enumerate(lines):
        text(d, (W / 2, y + dy + i * size * 1.18), ln, size, alpha=a, anchor="mm")
    sh = ov.filter(ImageFilter.GaussianBlur(size * 0.25))
    sh = Image.merge("RGBA", (*Image.new("RGB", sh.size, NAVY).split(), sh.split()[3].point(lambda v: v * 0.9)))
    base.alpha_composite(sh); base.alpha_composite(ov)

def wrap(s, size, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font(size).getlength(t) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    return lines + [cur]

def polyline(d, pts, color, width, t=1.0):
    """Desenha a fração t de uma polilinha (para traços progressivos). Retorna a ponta."""
    segs = list(zip(pts, pts[1:])); L = [math.dist(a, b) for a, b in segs]; tot = sum(L)
    left = tot * t; head = pts[0]
    for (a, b), l in zip(segs, L):
        if left <= 0: break
        k = min(1, left / l); head = (lerp(a[0], b[0], k), lerp(a[1], b[1], k))
        d.line([a, head], fill=color, width=width); left -= l
    return head

def curve(p0, p1, p2, n=40):
    return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0], (1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in (i/n for i in range(n+1))]

def glow_layer(base, draw_fn, blur):
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(ov))
    base.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur))); base.alpha_composite(ov)

def ring(d, c, r, color, w):
    d.ellipse([c[0]-r, c[1]-r, c[0]+r, c[1]+r], outline=color, width=w)

def card(base, im, box, radius, border=None, bw=2, alpha=1.0):
    x, y, w, h = [int(v) for v in box]
    if w < 4 or h < 4 or alpha <= 0: return
    tile = cover(im, w, h)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w-1, h-1], radius, fill=int(255*alpha))
    base.paste(tile, (x, y), m)
    if border:
        d = ImageDraw.Draw(base); d.rounded_rectangle([x, y, x+w-1, y+h-1], radius, outline=border + (int(255*alpha),), width=bw)

@lru_cache(8)
def screen(name):
    """Tela do app com números já desfocados (gerada por prep_screens.py)."""
    return Image.open(os.path.join(SRC, "screens", name)).convert("RGBA")

def phone(base, name, cx, cy, ph, scroll=0.0, alpha=1.0):
    """Moldura de celular com a tela rolada; scroll 0..1 do conteúdo além da janela."""
    if alpha <= 0: return
    pw = ph * 9 / 19.5; bez = ph * 0.018; r = int(ph * 0.06)
    x0, y0 = cx - pw / 2, cy - ph / 2
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + ph * 0.02, x0 + pw, y0 + ph * 1.02], r, fill=(0, 0, 0, int(160 * alpha)))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(ph * 0.03)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], r, fill=(18, 22, 40, int(255 * alpha)), outline=(90, 100, 130, int(255 * alpha)), width=2)
    iw, ih = int(pw - 2 * bez), int(ph - 2 * bez)
    sc = screen(name); k = iw / sc.width
    vis_h = ih / k; top = clamp(scroll) * max(0, sc.height - vis_h)
    tile = sc.crop((0, int(top), sc.width, int(top + vis_h))).resize((iw, ih), Image.LANCZOS)
    m = Image.new("L", (iw, ih), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, iw - 1, ih - 1], int(r * 0.8), fill=int(255 * alpha))
    base.paste(tile, (int(x0 + bez), int(y0 + bez)), m)

def tag(d, xy, s, size, color=LIME, alpha=1.0, anchor="la"):
    text(d, xy, s.upper(), size, fill=color, alpha=alpha, anchor=anchor)


# ---------- cenas ----------
def s1_jogada(f, W, H, V):
    # Plano IA aprovado (Seedance 2.5 R2-A, upscale 1080p): domínio + mudança de direção.
    t = f / 119
    fx = 0.5 if not V else lerp(0.5, 0.3, inout(prog(f, 40, 119)))   # no 9:16 acompanha o atleta
    bg = cover(clip("s1", f), W, H, lerp(1.0, 1.08, inout(t)), fx, 0.6)
    bg = darken(bg, 0.08)
    # whip-zoom de saída motivado pela bola (f 108-119)
    if f > 108:
        k = prog(f, 108, 119); bg = bg.filter(ImageFilter.GaussianBlur(k * 6))
    # título no alto: a bola e os pés ocupam o terço inferior
    headline(bg, "O talento acontece em campo.", W, H, prog(f, 18, 34) * (1 - prog(f, 104, 116)), V,
             y=(0.14 * H if not V else 0.16 * H))
    return bg, "S1 · Seedance 2.5 R2-A (upscale Precision 1080p)"

PATH_H = [(0.30, 0.86), (0.38, 0.80), (0.46, 0.79), (0.52, 0.76), (0.57, 0.70), (0.64, 0.67)]

def traj_pts(W, H, V, zoom=1.0):
    pts = PATH_H if not V else [(x * 1.0, y * 0.95) for x, y in PATH_H]
    # em vertical o recorte é central: remapeia x para a janela visível
    if V: pts = [(0.5 + (x - 0.47) * 2.6, 0.55 + (y - 0.75) * 1.1) for x, y in pts]
    return [(x * W, y * H) for x, y in pts]

def s2_olhar(f, W, H, V):
    l = f - 120; t = l / 119
    z = lerp(1.6, 1.0, ease(prog(l, 0, 50)))           # ampliar o enquadramento
    bg = cover(clip("v2-panorama-sm", 60 + l), W, H, z if not V else z * 1.0, 0.5, 0.62)
    bg = darken(bg, 0.12)
    pts = traj_pts(W, H, V)
    tr = ease(prog(l, 30, 100))
    def dr(d):
        h = polyline(d, pts, LIME + (255,), max(3, int(H * 0.006)), tr)
        if tr > 0: ring(d, h, H * 0.022, LIME + (255,), max(2, int(H * 0.004)))
        if tr > 0.02: ring(d, pts[0], H * 0.012, CYAN + (220,), max(2, int(H * 0.003)))
    glow_layer(bg, dr, H * 0.008)
    headline(bg, "Cada movimento conta.", W, H, prog(l, 12, 26) * (1 - prog(l, 106, 118)), V,
             y=(0.18 * H if not V else 0.2 * H))
    return bg, "v2-panorama-sm (upscale) + trajetória código"

CARDS = [("footage/v2-panorama-poster.webp", "Jogo"), ("references/youth-soccer-academy.jpg", "Treino"),
         ("references/soccer-training-hero.jpg", "Jogo"), ("footage/mock-family-app-poster.webp", "Treino"),
         ("interfaces/tablet-field.webp", "Jogo")]

def s3_registro(f, W, H, V):
    l = f - 240
    base = cover(img("references/fundo-sem-marca.jpg"), W, H, 1.1); base = darken(base, 0.55)
    d = ImageDraw.Draw(base)
    # 1) o plano vira um registro (card) — f 0-30
    k = inout(prog(l, 0, 30))
    cw, ch = (W * 0.24, W * 0.135) if not V else (W * 0.62, W * 0.35)
    ty = H * 0.42 if not V else H * 0.40
    gap = cw * 1.12
    cx0 = W / 2 - cw / 2 - (prog(l, 40, 120) * gap * 2 if not V else 0)   # timeline desliza
    main_box = (lerp(0, cx0, k), lerp(0, ty - ch / 2, k), lerp(W, cw, k), lerp(H, ch, k))
    # 2) linha do tempo nasce da trajetória (linha lima horizontal)
    ly = ty + ch / 2 + H * 0.05
    lt = ease(prog(l, 18, 55))
    def dr(dd):
        dd.line([(W * 0.5 - W * 0.5 * lt, ly), (W * 0.5 + W * 0.5 * lt, ly)], fill=LIME + (255,), width=max(2, int(H * 0.004)))
    glow_layer(base, dr, H * 0.006)
    # cards vizinhos (outros momentos)
    if not V:
        for i, (p, lab) in enumerate(CARDS):
            a = ease(prog(l, 35 + i * 10, 55 + i * 10))
            x = cx0 + (i + 1) * gap
            if x > W: continue
            card(base, img(p), (x, ty - ch / 2 + (1 - a) * 30, cw, ch), int(H * 0.012), CYAN, 2, a * 0.85)
            d = ImageDraw.Draw(base)
            d.ellipse([x + cw/2 - 6, ly - 6, x + cw/2 + 6, ly + 6], fill=CYAN + (int(255 * a),))
            tag(d, (x + cw / 2, ly + H * 0.03), lab, int(H * 0.022), CYAN, a, "ma")
    else:
        # vertical: pilha de registros acima/abaixo, linha do tempo vertical à esquerda
        for i, (p, lab) in enumerate(CARDS[:3]):
            a = ease(prog(l, 40 + i * 12, 60 + i * 12))
            y = ty - ch / 2 + ch * (-1.25, 1.35, 2.6)[i]
            card(base, img(p), (W / 2 - cw / 2, y, cw, ch), int(H * 0.008), CYAN, 2, a * 0.8)
            tag(ImageDraw.Draw(base), (W / 2 - cw / 2 + 12, y + 10), lab, int(H * 0.014), CYAN, a)
    card(base, clip("v2-panorama-sm", 180 + l), main_box, int(H * 0.012 * k), LIME if k > 0.5 else None, 3)
    d = ImageDraw.Draw(base)
    if k > 0.6 and not V:
        tag(d, (main_box[0] + main_box[2] / 2, ly + H * 0.03), "Jogo", int(H * (0.022 if not V else 0.014)), LIME, prog(l, 25, 35), "ma")
    # os registros "pousam" na galeria real do app
    ga = ease(prog(l, 84, 104))
    if ga > 0:
        if V:
            base.alpha_composite(Image.new("RGBA", base.size, NAVY + (int(200 * ga),)))
            phone(base, "4.2.2-galeria-videos.png", W / 2, H * 0.42 + (1 - ga) * H * 0.1, H * 0.6, 0.15 * prog(l, 100, 149), ga)
        else:
            phone(base, "4.2.2-galeria-videos.png", W * 0.80, H * 0.40 + (1 - ga) * H * 0.1, H * 0.64, 0.15 * prog(l, 100, 149), ga)
    headline(base, "Jogos e treinos. Uma história organizada.", W, H, prog(l, 38, 54) * (1 - prog(l, 136, 149)), V,
             y=(0.80 * H if not V else 0.80 * H))
    return base, "registros: posters/refs (provisório) · galeria 4.2.2 (números desfocados)"

def s4_evolucao(f, W, H, V):
    l = f - 390
    base = cover(img("references/fundo-sem-marca.jpg"), W, H, 1.1); base = darken(base, 0.6)
    split = 1 - inout(prog(l, 88, 112))                    # comparação -> perfil
    # comparação: mesmo lance, dois momentos. Trajetória A (hesitante) x B (mais direta)
    if split > 0:
        pw, ph = ((W * 0.43, H * 0.5) if not V else (W * 0.84, H * 0.25))
        boxes = ([(W * 0.05, H * 0.17), (W * 0.52, H * 0.17)] if not V else [(W * 0.08, H * 0.18), (W * 0.08, H * 0.48)])
        for i, (bx, by) in enumerate(boxes):
            a = ease(prog(l, i * 8, 18 + i * 8)) * split
            card(base, img("references/soccer-training-hero.jpg") if i == 0 else img("references/youth-soccer-academy.jpg"),
                 (bx, by, pw, ph), int(H * 0.012), LIME if i else CYAN, 3, a)
            d = ImageDraw.Draw(base)
            tag(d, (bx + 14, by - H * 0.035), ("Momento A · Treino" if i == 0 else "Momento B · Jogo"), int(H * (0.024 if not V else 0.014)), LIME if i else CYAN, a)
            p0 = (bx + pw * 0.2, by + ph * 0.85); p2 = (bx + pw * 0.8, by + ph * 0.35)
            pts = (curve(p0, (bx + pw * 0.25, by + ph * 0.2), p2) if i == 0
                   else curve(p0, (bx + pw * 0.55, by + ph * 0.8), p2))
            tr = ease(prog(l, 20 + i * 6, 60 + i * 6))
            col = (LIME if i else CYAN) + (int(255 * a),)
            glow_layer(base, lambda dd: (polyline(dd, pts, col, max(3, int(H * 0.005)), tr), ring(dd, p2, H * 0.015, col, 2) if tr > .98 else None), H * 0.006)
    # perfil real do app (4.2.0), rolando até "Evolução na temporada"
    pa = ease(prog(l, 100, 122))
    if pa > 0:
        if V: phone(base, "4.2.0-perfil-atleta.png", W / 2, H * 0.40 + (1 - pa) * 40, H * 0.6, 0.28 * inout(prog(l, 118, 170)), pa)
        else: phone(base, "4.2.0-perfil-atleta.png", W / 2, H * 0.43 + (1 - pa) * 40, H * 0.74, 0.28 * inout(prog(l, 118, 170)), pa)
    headline(base, "Mais contexto para entender.", W, H, prog(l, 10, 24) * (1 - prog(l, 80, 92)), V, y=(0.82 * H if not V else 0.80 * H))
    headline(base, "Mais clareza para desenvolver.", W, H, prog(l, 104, 118) * (1 - prog(l, 168, 179)), V, y=(0.86 * H if not V else 0.80 * H))
    return base, "comparação: placeholders (gerar 2 momentos do MESMO atleta) · perfil 4.2.0"

def s5_decisao(f, W, H, V):
    l = f - 570
    if l < 95:
        bg = cover(clip("mock-coach-tablet", 10 + l), W, H, 1.05 + l * 0.0008, 0.45 if not V else 0.42, 0.5)
        bg = darken(bg, 0.1)
        # insert: o que o treinador consulta — player com lances e comentários (4.2.9)
        ia = ease(prog(l, 34, 50))
        if ia > 0:
            bg = Image.blend(bg, darken(bg.filter(ImageFilter.GaussianBlur(H * 0.012)), 0.35), ia)
            sc = 0.45 + 0.55 * inout(prog(l, 50, 92))
            if V: phone(bg, "4.2.9-player-video.png", W / 2, H * 0.58 + (1 - ia) * 60, H * 0.62, sc, ia)
            else: phone(bg, "4.2.9-player-video.png", W * 0.70, H * 0.55 + (1 - ia) * 60, H * 0.78, sc, ia)
        headline(bg, "Inteligência para desenvolver.", W, H, prog(l, 10, 24) * (1 - prog(l, 82, 94)), V, y=(0.16 * H if not V else 0.2 * H))
        note = "mock-coach-tablet (tela do tablet a cobrir) · insert player 4.2.9"
    else:
        k = l - 95
        bg = cover(clip("v2-panorama-sm", 400 + k), W, H, lerp(1.35, 1.2, k / 85), 0.5, 0.6)
        bg = darken(bg, 0.12)
        headline(bg, "Visibilidade para descobrir.", W, H, prog(k, 6, 20) * (1 - prog(k, 72, 84)), V, y=(0.16 * H if not V else 0.2 * H))
        note = "PLACEHOLDER · retomada do treino (gerar plano dedicado)"
    # transição de saída: wipe pela linha de campo (f 160-179)
    w = inout(prog(l, 165, 179))
    if w > 0:
        d = ImageDraw.Draw(bg); x = W * w
        d.rectangle([0, 0, x, H], fill=NAVY + (255,)); d.line([(x, 0), (x, H)], fill=WHITE + (230,), width=max(2, int(H * 0.004)))
    return bg, note

def s6_marca(f, W, H, V):
    l = f - 750
    base = cover(img("references/fundo.jpg"), W, H, 1.05 + l * 0.0003); base = darken(base, 0.72)
    d = ImageDraw.Draw(base)
    # todas as entradas concluídas até f 810 (27 s)
    ia = ease(prog(l, 0, 22)); la = ease(prog(l, 12, 32)); t1 = ease(prog(l, 26, 42)); t2 = ease(prog(l, 34, 50))
    ca = ease(prog(l, 44, 58)); ua = ease(prog(l, 50, 60))
    lw = W * (0.34 if not V else 0.62)
    logo = img("brand/iscout-logo-branca.png"); lh = lw * logo.height / logo.width
    cy = H * (0.36 if not V else 0.38)
    icon_s = lh * 1.05
    ic = img("brand/icone.png").resize((max(1, int(icon_s * (0.85 + 0.15 * ia))),) * 2, Image.LANCZOS)
    if not V:
        gx = W / 2 - (icon_s + W * 0.02 + lw) / 2
        ic_xy = (gx + (icon_s - ic.width) / 2, cy - ic.height / 2); lg_xy = (gx + icon_s + W * 0.02, cy - lh / 2)
    else:
        ic_xy = (W / 2 - ic.width / 2, cy - icon_s * 1.25 - ic.height / 2 + icon_s * 0.5); lg_xy = (W / 2 - lw / 2, cy + icon_s * 0.15)
    ic.putalpha(ic.split()[3].point(lambda v: v * ia)); base.alpha_composite(ic, (int(ic_xy[0]), int(ic_xy[1])))
    lg = logo.resize((int(lw), int(lh)), Image.LANCZOS); lg.putalpha(lg.split()[3].point(lambda v: v * la))
    base.alpha_composite(lg, (int(lg_xy[0] + (1 - la) * 20), int(lg_xy[1])))
    s = int(H * (0.05 if not V else 0.03)); y0 = H * (0.58 if not V else 0.57)
    d = ImageDraw.Draw(base)
    text(d, (W / 2, y0 + (1 - t1) * 15), "O talento acontece em campo.", s, alpha=t1, anchor="mm")
    text(d, (W / 2, y0 + s * 1.3 + (1 - t2) * 15), "A iSCOUT ajuda a enxergá-lo.", s, fill=LIME, alpha=t2, anchor="mm")
    bs = int(s * 0.62); bw = font(bs).getlength("CONHEÇA A ISCOUT") + bs * 2.4; by = y0 + s * 3.0
    d.rounded_rectangle([W / 2 - bw / 2, by, W / 2 + bw / 2, by + bs * 2.4], int(bs * 1.2), fill=LIME + (int(255 * ca),))
    text(d, (W / 2, by + bs * 1.2), "Conheça a iSCOUT", bs, fill=NAVY, alpha=ca, anchor="mm")
    text(d, (W / 2, by + bs * 3.6), "iscout.tech", int(bs * 0.95), fill=WHITE, alpha=ua, anchor="mm", bold=False)
    return base, "logo/ícone oficiais (bitmap) · leitura livre a partir de 27 s"

SCENES = [(0, 120, "1 · A jogada", "SFX: toque de bola, chuteira na grama; trilha entra seca", s1_jogada),
          (120, 240, "2 · O olhar", "SFX: whoosh na abertura; trilha ganha pulso", s2_olhar),
          (240, 390, "3 · O registro", "SFX: clique suave a cada registro", s3_registro),
          (390, 570, "4 · A evolução", "Pausa curta na comparação; 'sweep' no perfil", s4_evolucao),
          (570, 750, "5 · A decisão humana", "Ambiente de treino, apito na retomada", s5_decisao),
          (750, 900, "6 · Marca", "Hit de marca em 25,5 s; cauda até 30 s", s6_marca)]

DISCLAIMER = "Imagens e interfaces ilustrativas"

def render(f, W, H, hud=True):
    V = H > W
    for a, b, name, audio, fn in SCENES:
        if a <= f < b: break
    im, note = fn(f, W, H, V)
    d = ImageDraw.Draw(im)
    if 240 <= f < 750:  # identificação discreta, mas legível
        text(d, (W - H * 0.02 if not V else W / 2, H - H * 0.025), DISCLAIMER, int(H * (0.018 if not V else 0.011)),
             fill=WHITE, alpha=0.7, anchor=("rd" if not V else "md"), bold=False)
    if hud:
        hs = max(11, int(min(W, H) * 0.022))
        d.rectangle([0, 0, W, hs * 3.4], fill=(0, 0, 0, 170))
        text(d, (8, 4), "%s   %05.2fs  f%03d" % (name, f / FPS, f), hs, fill=WHITE)
        text(d, (8, 4 + hs * 1.15), "♪ " + audio, int(hs * 0.85), fill=CYAN, bold=False)
        text(d, (8, 4 + hs * 2.2), "▣ " + note, int(hs * 0.85), fill=LIME, bold=False)
        d.rectangle([0, H - 4, W * f / TOTAL, H], fill=LIME + (255,))
    return im.convert("RGB")

if __name__ == "__main__":
    fmt, scale = sys.argv[1], float(sys.argv[2])
    W, H = (1920, 1080) if fmt == "h" else (1080, 1920)
    W, H = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
    out = os.environ.get("OUT", os.path.join(ROOT, "out"))
    os.makedirs(out, exist_ok=True)
    if "--frames" in sys.argv:
        for fr in sys.argv[sys.argv.index("--frames") + 1].split(","):
            render(int(fr), W, H, "--clean" not in sys.argv).save(os.path.join(out, "frame_%s_%s.png" % (fmt, fr)))
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "23", "-preset", "fast", "-pix_fmt", "yuv420p",
                          os.path.join(out, "animatic_%s.mp4" % ("16x9" if fmt == "h" else "9x16"))], stdin=subprocess.PIPE)
    for f in range(TOTAL):
        p.stdin.write(render(f, W, H).tobytes())
    p.stdin.close(); p.wait()
