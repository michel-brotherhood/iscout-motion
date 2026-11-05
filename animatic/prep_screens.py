"""Prepara telas do app para o animatic: desfoca todo token com dígitos (OCR).

Uso: python3 prep_screens.py <saida>
Os originais em assets/interfaces/redesign/ não são alterados.
"""
import csv, io, os, re, subprocess, sys
from PIL import Image, ImageFilter, ImageOps

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "interfaces", "redesign")
SCREENS = ["04-Area-do-Atleta/4.2.2-galeria-videos.png", "04-Area-do-Atleta/4.2.9-player-video.png",
           "04-Area-do-Atleta/4.2.0-perfil-atleta.png", "06-Area-do-Clube/C3.0-perfil-atleta-clube.png"]
DIGIT = re.compile(r"\d")
# números que o OCR não detecta (texto grande/estilizado): caixas em px da tela original
MANUAL = {"4.2.9-player-video.png": [(425, 1395, 160, 80)],
          "4.2.2-galeria-videos.png": [(650, 870, 90, 60)],
          "4.2.0-perfil-atleta.png": [(610, 1705, 110, 55), (530, 2085, 70, 60), (240, 920, 70, 70)]}

def blur_numbers(src, dst):
    im = Image.open(src).convert("RGB")
    big = im.resize((im.width * 2, im.height * 2), Image.LANCZOS).convert("L")
    rows = []
    # texto claro sobre fundo escuro: OCR na imagem normal e invertida, dois modos de segmentação
    for variant in (big, ImageOps.invert(big)):
        buf = io.BytesIO(); variant.save(buf, "PNG")
        for psm, extra in (("11", []), ("12", []), ("11", ["-c", "tessedit_char_whitelist=0123456789,.:%"])):
            tsv = subprocess.run(["tesseract", "stdin", "stdout", "--psm", psm, *extra, "tsv"], input=buf.getvalue(),
                                 capture_output=True).stdout.decode()
            min_conf = 60 if extra else 30   # passe só-dígitos gera mais falsos positivos
            rows += [dict(r, min_conf=min_conf) for r in csv.DictReader(io.StringIO(tsv), delimiter="\t", quoting=csv.QUOTE_NONE)]
    n = 0
    for r in rows:
        if not r.get("text") or not DIGIT.search(r["text"]): continue
        if float(r.get("conf") or 0) < r["min_conf"]: continue
        x, y, w, h = (int(r[k]) // 2 for k in ("left", "top", "width", "height"))
        if h > 70 or w > 260: continue          # descarta falsos positivos em fotos
        pad = max(4, h // 2)
        box = (max(0, x - pad), max(0, y - pad), min(im.width, x + w + pad), min(im.height, y + h + pad))
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(max(6, h * 0.6))), box[:2]); n += 1
    for x, y, w, h in MANUAL.get(os.path.basename(src), []):
        box = (x, y, x + w, y + h)
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(14)), box[:2]); n += 1
    im.save(dst)
    return n

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for s in SCREENS:
        n = blur_numbers(os.path.join(ROOT, s), os.path.join(out, os.path.basename(s)))
        print(f"{os.path.basename(s)}: {n} tokens numéricos desfocados")
