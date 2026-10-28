"""
El Inquilino (jefe de El Cuenco): skin de jugador de 64x64 (brazos anchos) para el maniquí del jefe. Un hombre pálido,
gris, de traje viejo, con las cuencas de los ojos vacías y una boca demasiado larga y finita. El plugin la usa con
terror:entity/inquilino (assets/terror/textures/entity/inquilino.png).
Uso: python fuentes/inquilino.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(404)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

SKIN = (176, 174, 166)
SUIT = (58, 58, 62)
SHIRT = (196, 194, 186)
PANTS = (34, 34, 37)
SHOES = (20, 20, 22)


def noisy(c, amount=6):
    n = rnd.randint(-amount, amount)
    return tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(x0, y0, x1, y1, color, amount=6):
    for y in range(y0, y1):
        for x in range(x0, x1):
            img.putpixel((x, y), noisy(color, amount))


def px(x, y, color):
    img.putpixel((x, y), tuple(color) + (255,))


# ---- Cabeza (todas las caras): piel gris, pelada, un poco más oscura arriba
fill(0, 8, 32, 16, SKIN)
fill(8, 0, 24, 8, SKIN)
fill(8, 0, 16, 8, (150, 148, 140))   # arriba
# Cara: cuencas negras y hundidas, con un borde oscuro
for x in (9, 10, 13, 14):
    for y in (11, 12):
        px(x, y, (10, 9, 9))
for x, y in ((9, 10), (10, 10), (13, 10), (14, 10), (8, 11), (11, 11), (12, 11), (15, 11)):
    px(x, y, (118, 114, 108))
for x in (9, 10, 13, 14):
    px(x, 13, (128, 124, 118))   # ojeras
# La boca: una línea larga y finita, de lado a lado
for x in range(9, 15):
    px(x, 14, (60, 50, 50))
px(8, 14, (90, 80, 78))
px(15, 14, (90, 80, 78))

# ---- Cuerpo: saco gris, camisa clara y corbata negra al frente
fill(16, 20, 40, 32, SUIT)
fill(20, 16, 36, 20, SUIT)
for y in range(20, 24):
    w = 24 - y   # el cuello en V
    for x in range(24 - w - 1, 24 + w + 1):
        if 20 <= x < 28:
            px(x, y, noisy(SHIRT, 4)[:3])
for y in range(20, 30):
    px(23, y, (14, 14, 16))
    px(24, y, (14, 14, 16))
for y in range(24, 32, 3):   # botones
    px(21, y, (30, 30, 32))

# ---- Brazos (derecho: 40-56 x 16-32; izquierdo: 32-48 x 48-64): mangas del saco, manos pálidas y largas
fill(40, 20, 56, 32, SUIT)
fill(44, 16, 52, 20, SUIT)
fill(32, 52, 48, 64, SUIT)
fill(36, 48, 44, 52, SUIT)
fill(40, 29, 56, 32, SKIN)
fill(32, 61, 48, 64, SKIN)
fill(48, 16, 52, 20, SKIN)   # abajo de la mano derecha
fill(40, 48, 44, 52, SKIN)   # abajo de la mano izquierda

# ---- Piernas (derecha: 0-16 x 16-32; izquierda: 16-32 x 48-64): pantalón negro y zapatos
fill(0, 20, 16, 32, PANTS)
fill(4, 16, 12, 20, PANTS)
fill(16, 52, 32, 64, PANTS)
fill(20, 48, 28, 52, PANTS)
fill(0, 30, 16, 32, SHOES, 3)
fill(16, 62, 32, 64, SHOES, 3)
fill(8, 16, 12, 20, SHOES, 3)
fill(24, 48, 28, 52, SHOES, 3)

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'inquilino.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print(out)
if len(sys.argv) > 1:
    # Vista de frente: cabeza, cuerpo, brazos y piernas
    S = 10
    front = Image.new('RGBA', (16, 32), (90, 110, 80, 255))
    front.alpha_composite(img.crop((8, 8, 16, 16)), (4, 0))
    front.alpha_composite(img.crop((20, 20, 28, 32)), (4, 8))
    front.alpha_composite(img.crop((44, 20, 48, 32)), (0, 8))
    front.alpha_composite(img.crop((36, 52, 40, 64)), (12, 8))
    front.alpha_composite(img.crop((4, 20, 8, 32)), (4, 20))
    front.alpha_composite(img.crop((20, 52, 24, 64)), (8, 20))
    view = Image.new('RGBA', (64 * S + 16 * S + 20, 64 * S), (40, 40, 40, 255))
    sheet = Image.new('RGBA', (64, 64), (70, 70, 70, 255)); sheet.alpha_composite(img)
    view.alpha_composite(sheet.resize((64 * S, 64 * S), Image.NEAREST))
    view.alpha_composite(front.resize((16 * S, 32 * S), Image.NEAREST), (64 * S + 10, 0))
    view.save(sys.argv[1])
