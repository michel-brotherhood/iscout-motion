"""V2: troca o nome de demonstração (Lucas Pereira / camisa 9) pelo protagonista Atleta #8.

Uso: PORTRAIT=<retrato> FONTDIR=<ttf> python3 v2_screens.py <pasta de telas já desfocadas>
Coordenadas em px da tela de 780 de largura.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

D, POR, FD = sys.argv[1], os.environ["PORTRAIT"], os.environ["FONTDIR"]
f7 = lambda s: ImageFont.truetype(os.path.join(FD, "Sora-700.ttf"), s)
f4 = lambda s: ImageFont.truetype(os.path.join(FD, "Sora-400.ttf"), s)

def face(r):
    pr = Image.open(POR).convert("RGB"); h = int(pr.height * .55); cx = pr.width // 2
    return pr.crop((cx - h // 2, int(pr.height * .02), cx + h // 2, int(pr.height * .02) + h)).resize((2 * r, 2 * r), Image.LANCZOS)

def avatar(im, cx, cy, r):
    m = Image.new("L", (2 * r, 2 * r)); ImageDraw.Draw(m).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    im.paste(face(r), (cx - r, cy - r), m)

def retext(im, box, txt, font, anchor_xy, fill):
    d = ImageDraw.Draw(im); bg = im.getpixel((box[0] + 4, box[1] + 4))
    d.rectangle(box, fill=bg); d.text(anchor_xy, txt, font=font, anchor="lm", fill=fill)

p = os.path.join(D, "2.4.1-atleta-dados-pessoais.png"); im = Image.open(p).convert("RGB")
avatar(im, 390, 468, 82)
retext(im, (55, 720, 600, 776), "Atleta #8", f4(30), (65, 748), (235, 238, 245))
retext(im, (55, 1105, 200, 1160), "8", f4(30), (65, 1132), (235, 238, 245))
im.save(p)

for name in ("4.3.0-relatorio.png", "4.2.2-galeria-videos.png"):   # mesmo cabeçalho de perfil
    p = os.path.join(D, name); im = Image.open(p).convert("RGB")
    avatar(im, 96, 281, 66)
    retext(im, (180, 262, 660, 318), "Atleta #8", f7(44), (184, 291), (255, 255, 255))
    im.save(p)

# área do clube (C3.0): cartão do atleta + aviso de compartilhamento sem nomes de exemplo
p = os.path.join(D, "C3.0-perfil-atleta-clube.png")
if os.path.exists(p):
    im = Image.open(p).convert("RGB")
    avatar(im, 130, 311, 60)
    retext(im, (212, 272, 434, 320), "Atleta #8", f7(34), (218, 296), (255, 255, 255))
    retext(im, (126, 470, 722, 556), "Dados compartilhados pelo responsável", f7(25), (130, 494), (255, 255, 255))
    im.save(p)
