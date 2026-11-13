"""V4: tela do tablet do técnico (coach_t1.png) com dashboard desenhado em código, preenchendo o vidro inteiro.

Na V3 a tela vinha de um quadro do vídeo do site (v3_tablet2.py): o conteúdo não cobria o vidro (faixa vazia
embaixo e à direita) e o polegar daquele vídeo aparecia por transparência. Aqui o dashboard é desenhado em
1024x768 e projetado nos quatro cantos do vidro medidos em coach_t1.png; dedos continuam por cima (máscara de pele).

Como módulo: Tablet(A, V3).frame(t) -> cena com a tela animada no instante t (s).
Uso (estático): python3 v4_tablet.py <assets> <out/v3> <fontdir>  -> out/v3/coach_dash_v4.png
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SW, SH = 1024, 768
GLASS = [(801, 315), (1006.5, 305), (1036.5, 480), (837, 501)]      # TL, TR, BR, BL do vidro em coach_t1.png
NAVY = (17, 29, 52); CARD = (27, 44, 74); LIME = (205, 213, 92); CYAN = (64, 190, 222); TXT = (225, 232, 242); MUTED = (140, 156, 182)
CARDS = [("Jogos", 18, "{:d}"), ("Gols", 11, "{:d}"), ("Assistências", 6, "{:d}"),
         ("Precisão de passe", 86, "{:d}%"), ("Vel. máx (km/h)", 28.4, "{:.1f}"), ("Nota média", 8.4, "{:.1f}")]
BARS = [(.42, LIME), (.55, CYAN), (.50, LIME), (.68, CYAN), (.63, LIME), (.80, CYAN), (.74, LIME), (.92, CYAN)]
MONTHS = ["abr", "mai", "jun", "jul", "ago", "set", "out", "nov"]

def ease(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3

def _coeffs(dst, src_):
    m = []
    for (x, y), (u, v) in zip(dst, src_):
        m += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
    return np.linalg.solve(np.array(m, float), np.array([c for p in src_ for c in p], float)).tolist()

class Tablet:
    def __init__(self, A, V3, fontdir=None):
        fd = fontdir or os.environ["FONTDIR"]
        self.f7 = lambda s: ImageFont.truetype(os.path.join(fd, "Sora-700.ttf"), s)
        self.f4 = lambda s: ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", s)
        self.im = Image.open(os.path.join(V3, "coach_t1.png")).convert("RGB")
        pr = Image.open(os.path.join(V3, "p_a1.png")).convert("RGB")          # retrato do #8 (mesmo do filme)
        s = int(pr.height * .5); cx = pr.width // 2
        self.face = pr.crop((cx - s // 2, int(pr.height * .04), cx + s // 2, int(pr.height * .04) + s)).resize((200, 200), Image.LANCZOS)
        self.co = _coeffs(GLASS, [(0, 0), (SW, 0), (SW, SH), (0, SH)])
        q = Image.new("L", self.im.size, 0); ImageDraw.Draw(q).polygon(GLASS, fill=255)
        a = np.asarray(self.im).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
        skin = (r > 90) & (r > g + 8) & (g > b - 5) & (r - b > 25)
        yy, xx = np.mgrid[0:self.im.size[1], 0:self.im.size[0]]
        skin &= ((xx < 880) & (yy > 385)) | (xx > 1025)
        self.mask = Image.fromarray((((np.asarray(q) > 0) & ~skin) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.7))
        # reflexo leve na diagonal (o vidro não é uma tela chapada)
        gy, gx = np.mgrid[0:SH, 0:SW]
        self.glare = np.clip(1 - np.abs((gx / SW + gy / SH) - .55) / .35, 0, 1)[..., None] * 14

    def screen(self, t):
        im = Image.new("RGB", (SW, SH), NAVY); d = ImageDraw.Draw(im)
        a = ease(t / .35)
        col = lambda c, k: tuple(int(NAVY[i] + (c[i] - NAVY[i]) * k) for i in range(3))
        # cabeçalho
        d.text((40, 44), "‹", font=self.f7(40), fill=col(TXT, a), anchor="lm")
        d.text((SW / 2, 44), "Dashboard do atleta", font=self.f7(28), fill=col(TXT, a), anchor="mm")
        for k in range(2): d.ellipse([SW - 110 + k * 46, 32, SW - 86 + k * 46, 56], outline=col(MUTED, a), width=3)
        # foto + nome
        k = ease((t - .15) / .4)
        if k > 0:
            m = Image.new("L", (200, 200), 0); ImageDraw.Draw(m).ellipse([0, 0, 199, 199], fill=int(255 * k))
            im.paste(self.face, (50, 110), m)
            d.ellipse([46, 106, 254, 314], outline=col(LIME, k), width=4)
            d.text((150, 350), "Atleta #8", font=self.f7(32), fill=col(TXT, k), anchor="mm")
            d.text((150, 388), "Atacante · Sub-15", font=self.f4(22), fill=col(MUTED, k), anchor="mm")
        # cartões de números
        for j, (lab, val, fmt) in enumerate(CARDS):
            k = ease((t - .35 - .1 * j) / .35)
            if k <= 0: continue
            x = 300 + (j % 3) * 236; y = 100 + (j // 3) * 150
            d.rounded_rectangle([x, y, x + 220, y + 136], 16, fill=col(CARD, k))
            d.text((x + 18, y + 30), lab, font=self.f4(20), fill=col(MUTED, k), anchor="lm")
            v = val * ease((t - .45 - .1 * j) / .8)
            d.text((x + 18, y + 88), fmt.format(int(round(v)) if isinstance(val, int) else v), font=self.f7(52), fill=col(LIME, k), anchor="lm")
        # gráfico: barras sobem
        k = ease((t - .6) / .3)
        if k > 0:
            d.rounded_rectangle([40, 430, SW - 40, SH - 30], 18, fill=col(CARD, k))
            d.text((70, 466), "Evolução na temporada", font=self.f7(24), fill=col(TXT, k), anchor="lm")
            for i, (h, c) in enumerate(BARS):
                hh = h * 200 * ease((t - .8 - .07 * i) / .8)
                x = 90 + i * 108; yb = SH - 80
                if hh > 1: d.rounded_rectangle([x, yb - hh, x + 62, yb], 6, fill=col(c, k))
                d.text((x + 31, yb + 24), MONTHS[i], font=self.f4(18), fill=col(MUTED, k), anchor="mm")
        a_ = np.asarray(im).astype(np.float32) * .93 + self.glare            # brilho de tela real, sem estourar
        return Image.fromarray(np.clip(a_, 0, 255).astype(np.uint8))

    def frame(self, t):
        warp = self.screen(t).transform(self.im.size, Image.PERSPECTIVE, self.co, Image.BICUBIC)
        return Image.composite(warp, self.im, self.mask)

if __name__ == "__main__":
    A, V3, FD = sys.argv[1], sys.argv[2], sys.argv[3]
    Tablet(A, V3, FD).frame(10).save(os.path.join(V3, "coach_dash_v4.png"))
