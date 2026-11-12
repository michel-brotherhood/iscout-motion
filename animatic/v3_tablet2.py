"""V3: dashboard do app (vídeo do site) na tela do tablet do técnico (coach_t1.png, tela vazia), estático ou animado.

Uso (estático): python3 v3_tablet2.py <assets> <out/v3>   -> out/v3/coach_dash.png
Como módulo: Tablet(assets, v3).frame(t) devolve a cena com a tela animada no instante t (s):
cabeçalho e foto entram, os cartões de números aparecem em sequência e as barras do gráfico sobem.
"""
import io, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = [(497, 224), (768, 247), (728, 493), (430, 458)]           # tela no quadro do vídeo do site (TL, TR, BR, BL)
DST = [(800, 315), (1003.5, 304.5), (1037, 479), (849.5, 492.5)]  # tela vazia em coach_t1.png

def _coeffs(dst, src_):
    m = []
    for (x, y), (u, v) in zip(dst, src_):
        m += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
    return np.linalg.solve(np.array(m, float), np.array([c for p in src_ for c in p], float)).tolist()

def ease(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3

class Tablet:
    def __init__(self, A, V3):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "6.2", "-i", f"{A}/footage/mock-coach-tablet.mp4", "-frames:v", "1",
                              "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
        sa = np.asarray(Image.open(io.BytesIO(raw)).convert("RGB")).astype(np.float32).copy()
        # polegar do vídeo no canto inferior direito da tela: cada coluna recebe o fundo liso logo acima
        for x in range(665, 800):
            w = min(1, (x - 665) / 6)
            sa[386:548, x] = sa[386:548, x] * (1 - w) + sa[383, x] * w
        self.dash = sa
        self.bg = np.full_like(sa, sa[300, 470])                         # azul-marinho da tela (amostrado)
        self.im = Image.open(f"{V3}/coach_t1.png").convert("RGB")
        self.co = _coeffs(DST, SRC)
        q = Image.new("L", self.im.size, 0); ImageDraw.Draw(q).polygon(DST, fill=255)
        a = np.asarray(self.im).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
        skin = (r > 90) & (r > g + 8) & (g > b - 5) & (r - b > 25)
        yy, xx = np.mgrid[0:self.im.size[1], 0:self.im.size[0]]
        skin &= ((xx < 880) & (yy > 385)) | (xx > 1025)
        self.mask = Image.fromarray((((np.asarray(q) > 0) & ~skin) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.7))
        h, w = sa.shape[:2]; self.yy, self.xx = np.mgrid[0:h, 0:w]
        mx, mn = sa.max(2), sa.min(2)
        bars = (self.yy >= 375) & (self.yy < 500) & (self.xx > 440) & (self.xx < 690) & (mx - mn > 40) & (mx > 90)
        self.bars = np.asarray(Image.fromarray((bars * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0   # barras + borda
        chart = (self.yy >= 375) & (self.yy < 500) & (self.xx > 440) & (self.xx < 690) & ~self.bars
        self.bg[self.bars] = np.median(sa[chart], 0)                       # fundo do gráfico por trás das barras

    def screen(self, t):
        """Conteúdo da tela no instante t: máscara de revelação por região do dashboard."""
        yy, xx = self.yy, self.xx
        rev = np.zeros(self.dash.shape[:2], np.float32)
        rev[(yy < 255)] = ease(t / .35)                                              # cabeçalho
        rev[(yy >= 255) & (yy < 385) & (xx < 560)] = ease((t - .15) / .4)            # foto do atleta
        for k, (x0, x1) in enumerate(((560, 640), (640, 700), (700, 800))):          # cartões, coluna a coluna
            rev[(yy >= 255) & (yy < 385) & (xx >= x0) & (xx < x1)] = ease((t - .35 - .15 * k) / .35)
        # gráfico: as barras sobem (revelação de baixo para cima)
        top = 490 - (490 - 370) * ease((t - .7) / .9)
        rev[(yy >= 385)] = ease((t - .5) / .25)                                     # fundo e eixos do gráfico
        rev[self.bars] = (yy[self.bars] >= top).astype(np.float32)                   # só as barras crescem
        a = rev[..., None]
        return Image.fromarray((self.dash * a + self.bg * (1 - a)).astype(np.uint8))

    def frame(self, t):
        warp = self.screen(t).transform(self.im.size, Image.PERSPECTIVE, self.co, Image.BICUBIC)
        return Image.composite(warp, self.im, self.mask)

if __name__ == "__main__":
    A, V3 = sys.argv[1], sys.argv[2]
    Tablet(A, V3).frame(10).save(f"{V3}/coach_dash.png")
