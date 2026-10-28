"""
Lo que hay (jefe de La Nada): dos cosas.
- Su skin (terror:entity/loquehay): un cuerpo negro casi puro, que en La Nada no se ve; flaco, de dedos largos. La cara
  (la que aparece en el screamer) tiene ojos blancos rasgados y una boca enorme, abierta y dentada.
- Sus ojos (ítem terror:ojos, un plano que el plugin pone flotando a la altura de la cabeza, con brillo): dos puntos de
  luz blancos con un borde rojo. Es lo único que se ve de él en la oscuridad.
Uso: python fuentes/loquehay.py [vista.png]
"""
import json, os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(666)

# ---------------------------------------------------------------- la skin
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
BODY = (10, 10, 12)
EDGE = (22, 22, 26)
EYE = (240, 240, 236)
MOUTH = (2, 2, 2)
TOOTH = (210, 204, 190)


def noisy(c, amount=3):
    n = rnd.randint(-amount, amount)
    return tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(x0, y0, x1, y1, color, amount=3):
    for y in range(y0, y1):
        for x in range(x0, x1):
            img.putpixel((x, y), noisy(color, amount))


def px(x, y, color):
    img.putpixel((x, y), tuple(color[:3]) + (255,))


fill(0, 0, 64, 64, BODY)
# Recortes de la plantilla: lo que no se usa, transparente (solo las partes del cuerpo quedan negras)
mask = Image.new('L', (64, 64), 0)
for box in ((8, 0, 24, 8), (0, 8, 32, 16), (20, 16, 36, 20), (16, 20, 40, 32), (4, 16, 12, 20), (0, 20, 16, 32),
            (44, 16, 52, 20), (40, 20, 56, 32), (20, 48, 28, 52), (16, 52, 32, 64), (36, 48, 44, 52), (32, 52, 48, 64)):
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            mask.putpixel((x, y), 255)
img.putalpha(mask)
# Cara (8..15 x 8..15): ojos blancos rasgados, inclinados; una boca enorme, dentada
for x, y in ((8, 10), (9, 10), (10, 11), (15, 10), (14, 10), (13, 11)):
    px(x, y, EYE)
for x in range(9, 15):
    for y in (13, 14, 15):
        px(x, y, MOUTH)
for x in range(9, 15, 2):
    px(x, 13, TOOTH)
    px(x + 1, 15, TOOTH)
# Dedos largos (las puntas de las manos, un poco más claras)
for x in range(40, 56, 2):
    px(x, 31, EDGE)
for x in range(32, 48, 2):
    px(x, 63, EDGE)
skin = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'loquehay.png')
os.makedirs(os.path.dirname(skin), exist_ok=True)
img.save(skin)

# ---------------------------------------------------------------- los ojos
eyes = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
for cx in (4, 11):
    # Una rendija blanca horizontal, con un brillo rojo que se apaga hacia afuera
    for dx in (-1, 0, 1):
        eyes.putpixel((cx + dx, 7), (255, 255, 250, 255))
        eyes.putpixel((cx + dx, 6), (150, 12, 12, 255))
        eyes.putpixel((cx + dx, 8), (150, 12, 12, 255))
    eyes.putpixel((cx - 2, 7), (200, 20, 20, 255))
    eyes.putpixel((cx + 2, 7), (200, 20, 20, 255))
tex = os.path.join(ROOT, 'assets', 'terror', 'textures', 'item', 'ojos.png')
eyes.save(tex)
face = {'uv': [0, 0, 16, 16], 'texture': '#ojos'}
json.dump({'textures': {'ojos': 'terror:item/ojos', 'particle': 'terror:item/ojos'},
           'elements': [{'from': [0, 0, 7.95], 'to': [16, 16, 8.05], 'shade': False,
                         'faces': {'north': face, 'south': dict(face)}}]},
          open(os.path.join(ROOT, 'assets', 'terror', 'models', 'item', 'ojos.json'), 'w'), indent=2)
json.dump({'model': {'type': 'minecraft:model', 'model': 'terror:item/ojos'}},
          open(os.path.join(ROOT, 'assets', 'terror', 'items', 'ojos.json'), 'w'), indent=2)
print(skin, tex, sep='\n')

if len(sys.argv) > 1:
    S = 12
    view = Image.new('RGBA', (64 * 8 + 16 * S + 20, 64 * 8), (60, 60, 60, 255))
    sheet = Image.new('RGBA', (64, 64), (90, 90, 90, 255)); sheet.alpha_composite(img)
    view.alpha_composite(sheet.resize((64 * 8, 64 * 8), Image.NEAREST))
    face_img = Image.new('RGBA', (8, 8), (90, 90, 90, 255)); face_img.alpha_composite(img.crop((8, 8, 16, 16)))
    view.alpha_composite(face_img.resize((16 * S, 16 * S), Image.NEAREST), (64 * 8 + 10, 0))
    e = Image.new('RGBA', (16, 16), (5, 5, 5, 255)); e.alpha_composite(eyes)
    view.alpha_composite(e.resize((16 * S, 16 * S), Image.NEAREST), (64 * 8 + 10, 16 * S + 10))
    view.save(sys.argv[1])
