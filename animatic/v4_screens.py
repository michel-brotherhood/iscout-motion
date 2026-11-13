"""V4: telas do app SEM desfoque nos números (feedback do Bernardo, 13/11/2026).

Os números de demonstração das telas originais (assets/interfaces/redesign) são fictícios e coerentes entre si
(ex.: 24,1 km/h, 86 % de passe, 5 jogos, 4 gols, 38,2 km). Até a V3 eles eram desfocados por
prep_screens.py ("números neutralizados até aprovação"); o cliente aprovou mostrar valores fictícios.

Parte das telas já tratadas da V3 (foto e nome do Atleta #8) e devolve os pixels originais fora das áreas
editadas; depois reescreve as linhas que ainda traziam o nome de demonstração (Lucas Pereira / Camisa 9).

Uso: python3 v4_screens.py <telas V3 (com desfoque)> <saída>
"""
import glob, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "interfaces", "redesign")
INTER = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
# áreas editadas na V3 (avatar e nome do #8): ficam como estão; o resto volta ao original
EDIT = {"2.4.1-atleta-dados-pessoais": [(308, 386, 472, 550), (55, 720, 600, 776), (55, 1105, 200, 1160)],
        "4.3.0-relatorio": [(30, 215, 162, 347), (180, 262, 660, 318)],
        "4.2.2-galeria-videos": [(30, 215, 162, 347), (180, 262, 660, 318)],
        "C3.0-perfil-atleta-clube": [(70, 251, 190, 371), (212, 272, 434, 320), (126, 470, 722, 556)],
        "4.2.0-perfil-atleta": [(0, 214, 780, 706)]}
# linhas reescritas (caixa x0,y0,x1,y1 na tela de 780 px; cor e fundo amostrados do original)
LINES = {"4.2.9-player-video": [((32, 776, 700, 806), "Atleta #8 · 19 out 2026 · Jogo vs. Academia FC")],
         "4.3.0-relatorio": [((183, 320, 520, 350), "Atacante · Sub-15 · Camisa 8"), ((512, 1077, 590, 1105), "#8")],
         "4.2.2-galeria-videos": [((183, 320, 520, 350), "Atacante · Sub-15 · Camisa 8")]}

def main(v3dir, out):
    os.makedirs(out, exist_ok=True)
    for p in sorted(glob.glob(os.path.join(v3dir, "*.png"))):
        n = os.path.splitext(os.path.basename(p))[0]
        orig = Image.open(glob.glob(os.path.join(ROOT, "*", n + ".png"))[0]).convert("RGB")
        a = np.asarray(orig).copy(); b = np.asarray(Image.open(p).convert("RGB"))
        for x0, y0, x1, y1 in EDIT.get(n, []): a[y0:y1, x0:x1] = b[y0:y1, x0:x1]
        im = Image.fromarray(a); d = ImageDraw.Draw(im)
        for box, txt in LINES.get(n, []):
            px = np.asarray(orig.crop(box)).reshape(-1, 3)
            col = tuple(int(v) for v in px[px.sum(1).argmax()])          # cor do texto = pixel mais claro da linha
            d.rectangle(box, fill=orig.getpixel((box[0] - 6, box[1] + 3)))
            d.text((box[0], (box[1] + box[3]) / 2), txt, font=ImageFont.truetype(INTER, 22), anchor="lm", fill=col)
        im.save(os.path.join(out, n + ".png"))
        print(n)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
