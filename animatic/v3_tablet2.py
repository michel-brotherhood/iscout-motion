"""V3: dashboard do app (vídeo do site) na tela do tablet do técnico (imagem gerada coach_t1.png, tela vazia).

Uso: python3 v3_tablet2.py <assets> <out/v3>
A tela está quase de frente, então a perspectiva fica limpa; polegar e dedos ficam por cima (máscara de pele).
"""
import io, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

A, V3 = sys.argv[1], sys.argv[2]
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "6.2", "-i", f"{A}/footage/mock-coach-tablet.mp4", "-frames:v", "1",
                      "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
src = Image.open(io.BytesIO(raw)).convert("RGB")
SRC = [(497, 224), (768, 247), (728, 493), (430, 458)]
# polegar do vídeo sobre o canto inferior direito da tela: à direita da última barra, cada coluna
# recebe o fundo da tela logo acima (o fundo é liso), com transição suave na borda esquerda
sa = np.asarray(src).astype(np.float32).copy()
for x in range(665, 800):
    w = min(1, (x - 665) / 6)
    sa[386:548, x] = sa[386:548, x] * (1 - w) + sa[383, x] * w
src = Image.fromarray(sa.astype(np.uint8))
im = Image.open(f"{V3}/coach_t1.png").convert("RGB")
DST = [(800, 315), (1003.5, 304.5), (1037, 479), (849.5, 492.5)]

def coeffs(dst, src_):
    m = []
    for (x, y), (u, v) in zip(dst, src_):
        m += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
    return np.linalg.solve(np.array(m, float), np.array([c for p in src_ for c in p], float)).tolist()

warp = src.transform(im.size, Image.PERSPECTIVE, coeffs(DST, SRC), Image.BICUBIC)
quad = Image.new("L", im.size, 0); ImageDraw.Draw(quad).polygon(DST, fill=255)
a = np.asarray(im).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
skin = (r > 90) & (r > g + 8) & (g > b - 5) & (r - b > 25)
yy, xx = np.mgrid[0:im.size[1], 0:im.size[0]]
skin &= ((xx < 880) & (yy > 385)) | (xx > 1025)
mask = (np.asarray(quad) > 0) & ~skin
out = Image.composite(warp, im, Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.7)))
out.save(f"{V3}/coach_dash.png")
