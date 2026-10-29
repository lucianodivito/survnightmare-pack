"""
La cara de Lo que hay (ítem terror:cara_nada): la del screamer y la de los momentos de oscuridad total. No es pixel
art de skin: está pintada a 128x128, con sombras suaves. Una cara pálida y estirada, cuencas hundidas y negras con un
puntito blanco que te mira, una boca abierta que se alarga hacia abajo, grietas y algo oscuro que le chorrea.
Uso: python fuentes/cara_nada.py [vista.png]
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(1313)
S = 128
img = Image.new('RGBA', (S, S), (0, 0, 0, 0))

# La forma de la cara: un óvalo alargado, más angosto abajo
face = Image.new('L', (S, S), 0)
d = ImageDraw.Draw(face)
d.ellipse([26, 6, 102, 124], fill=255)
face = face.filter(ImageFilter.GaussianBlur(1.2))

# La piel: gris pálido, con sombras hacia los bordes y ruido
skin = Image.new('RGBA', (S, S), (0, 0, 0, 0))
for y in range(S):
    for x in range(S):
        a = face.getpixel((x, y))
        if a == 0:
            continue
        dx, dy = (x - 64) / 38, (y - 64) / 58
        shade = max(0.0, 1 - (dx * dx + dy * dy) ** 1.4 * 0.75)
        v = 70 + 120 * shade + rnd.uniform(-8, 8)
        skin.putpixel((x, y), (int(v * 0.95), int(v * 0.97), int(v), a))
img.alpha_composite(skin)

dark = ImageDraw.Draw(img)
# Las cuencas: hundidas, de bordes difusos (una sombra borrosa), inclinadas hacia afuera, con el fondo negro
shadow = Image.new('L', (S, S), 0)
ds = ImageDraw.Draw(shadow)
for cx, tilt in ((47, -6), (81, 6)):
    ds.polygon([(cx - 15, 40 + tilt * 0.6), (cx - 4, 30), (cx + 13, 36 - tilt * 0.6), (cx + 11, 54), (cx - 2, 62), (cx - 14, 54)], fill=255)
shadow = shadow.filter(ImageFilter.GaussianBlur(4))
black = Image.new('RGBA', (S, S), (0, 0, 0, 255))
img = Image.composite(black, img, shadow.point(lambda v: int(v * 0.95)))
dark = ImageDraw.Draw(img)
for cx in (47, 81):
    dark.polygon([(cx - 8, 44), (cx - 2, 38), (cx + 7, 42), (cx + 5, 52), (cx - 3, 55), (cx - 8, 50)], fill=(0, 0, 0, 255))
    dark.ellipse([cx - 1, 45, cx + 1, 47], fill=(245, 245, 240, 255))   # el puntito que te mira
# La boca: abierta, negra, estirada hacia abajo como si gritara
mouth = [(52, 82), (58, 78), (64, 79), (70, 78), (76, 82), (74, 104), (68, 120), (60, 120), (54, 104)]
dark.polygon(mouth, fill=(0, 0, 0, 255))
dark.line([(52, 82), (54, 104), (60, 120)], fill=(40, 30, 30, 255), width=2)
dark.line([(76, 82), (74, 104), (68, 120)], fill=(40, 30, 30, 255), width=2)
# Lo que chorrea de los ojos
for cx in (44, 50, 78, 84):
    length = rnd.randint(18, 40)
    for i in range(length):
        dark.point((cx + int(math.sin(i * 0.3) * 1), 58 + i), fill=(10, 8, 8, 255))
        dark.point((cx + 1, 58 + i), fill=(25, 18, 18, 255))
# Grietas en la frente y las mejillas
for x0, y0 in ((60, 12), (36, 62), (90, 66)):
    x, y = x0, y0
    for _ in range(26):
        nx, ny = x + rnd.choice((-2, -1, 0, 1, 2)), y + rnd.choice((1, 2))
        dark.line([(x, y), (nx, ny)], fill=(20, 18, 18, 255), width=1)
        x, y = nx, ny

out_tex = os.path.join(ROOT, 'assets', 'terror', 'textures', 'item', 'cara_nada.png')
img.save(out_tex)
face_json = {'uv': [0, 0, 16, 16], 'texture': '#cara'}
json.dump({'textures': {'cara': 'terror:item/cara_nada', 'particle': 'terror:item/cara_nada'},
           'elements': [{'from': [0, 0, 7.95], 'to': [16, 16, 8.05], 'shade': False,
                         'faces': {'north': face_json, 'south': dict(face_json)}}]},
          open(os.path.join(ROOT, 'assets', 'terror', 'models', 'item', 'cara_nada.json'), 'w'), indent=2)
json.dump({'model': {'type': 'minecraft:model', 'model': 'terror:item/cara_nada'}},
          open(os.path.join(ROOT, 'assets', 'terror', 'items', 'cara_nada.json'), 'w'), indent=2)
print(out_tex)
if len(sys.argv) > 1:
    view = Image.new('RGBA', (S, S), (6, 6, 8, 255))
    view.alpha_composite(img)
    view.resize((S * 4, S * 4), Image.NEAREST).save(sys.argv[1])
