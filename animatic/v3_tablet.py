"""V3: põe o dashboard do app (do vídeo do site, mock-coach-tablet) na tela do tablet de youth-soccer-academy.jpg.

Uso: python3 v3_tablet.py <assets> <saida.png>
Cantos medidos à mão nas duas imagens; dedos sobre a tela são preservados por máscara de pele.
"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

A, OUT = sys.argv[1], sys.argv[2]
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "6.2", "-i", f"{A}/footage/mock-coach-tablet.mp4", "-frames:v", "1",
                      "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
import io
src = Image.open(io.BytesIO(raw)).convert("RGB")
SRC = [(497, 224), (768, 247), (728, 493), (430, 458)]          # tela no quadro do vídeo do site (TL, TR, BR, BL)
d = ImageDraw.Draw(src)                                          # polegar no canto inferior direito -> fundo da tela
d.polygon([(672, 384), (780, 384), (780, 548), (628, 548)], fill=src.getpixel((452, 436)))
im = Image.open(f"{A}/references/youth-soccer-academy.jpg").convert("RGB")
DST = [(709, 587), (812, 561), (887, 655), (786, 683)]

def coeffs(dst, src_):   # transformação perspectiva: pontos de saída -> pontos de origem
    m = []
    for (x, y), (u, v) in zip(dst, src_):
        m += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
    return np.linalg.solve(np.array(m, float), np.array([c for p in src_ for c in p], float)).tolist()

warp = src.transform(im.size, Image.PERSPECTIVE, coeffs(DST, SRC), Image.BICUBIC)
quad = Image.new("L", im.size, 0); ImageDraw.Draw(quad).polygon(DST, fill=255)
a = np.asarray(im).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
skin = (r > 95) & (r > g + 10) & (g > b) & (r - b > 35)          # dedos por cima da tela
yy, xx = np.mgrid[0:im.size[1], 0:im.size[0]]
skin &= ((xx < 810) & (yy > 645)) | ((xx > 805) & (yy < 607))   # só nas zonas do polegar e do indicador
mask = (np.asarray(quad) > 0) & ~skin
mimg = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.8))
out = Image.composite(warp, im, mimg)
out.save(OUT)
