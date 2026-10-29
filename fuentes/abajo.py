"""
El Fondo (jefe de El Mar quieto): skin de jugador de 64x64 (brazos anchos) para el maniquí del jefe, que el plugin
agranda hasta unos seis bloques. Un ahogado hinchado: piel pálida verdosa con manchas y percebes, ojos blancos
lechosos, la boca abierta y negra, pelo negro largo y mojado que le cae (en la capa de afuera), y ropa podrida.
El plugin la usa con terror:entity/abajo (assets/terror/textures/entity/abajo.png).
Uso: python fuentes/abajo.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(2024)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

SKIN = (150, 168, 150)       # verde pálido de ahogado
SKIN_DARK = (112, 130, 114)
BRUISE = (96, 104, 120)
RAGS = (58, 66, 60)
RAGS_DARK = (40, 46, 42)
BARNACLE = (196, 192, 176)
HAIR = (14, 16, 16)
EYE = (226, 230, 224)
BLACK = (8, 10, 10)


def noisy(c, amount=6):
    n = rnd.randint(-amount, amount)
    return tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(x0, y0, x1, y1, color, amount=6):
    for y in range(y0, y1):
        for x in range(x0, x1):
            img.putpixel((x, y), noisy(color, amount))


def px(x, y, color):
    img.putpixel((x, y), tuple(color[:3]) + (255,))


def blotches(x0, y0, x1, y1, count, color):
    for _ in range(count):
        px(rnd.randint(x0, x1 - 1), rnd.randint(y0, y1 - 1), noisy(color, 6)[:3])


# ---- Cabeza: piel de ahogado, con manchas
fill(0, 8, 32, 16, SKIN)
fill(8, 0, 24, 8, SKIN_DARK)
blotches(0, 8, 32, 16, 18, BRUISE)
# Cara: ojos blancos lechosos, sin pupila, y la boca abierta, negra, que cuelga
for x, y in ((9, 10), (10, 10), (9, 11), (10, 11), (13, 10), (14, 10), (13, 11), (14, 11)):
    px(x, y, EYE)
for x in (9, 10, 13, 14):
    px(x, 12, SKIN_DARK)
for x in range(10, 14):
    for y in (13, 14, 15):
        px(x, y, BLACK)
px(11, 15, (60, 30, 30))
# ---- Capa de afuera: pelo negro largo, mojado, que cae por todos lados (al frente, en mechones)
for x in range(40, 48):
    for y in range(0, 8):
        px(x, y, noisy(HAIR, 3)[:3])
for x0 in (32, 48, 56):
    for x in range(x0, x0 + 8):
        for y in range(8, 16):
            px(x, y, noisy(HAIR, 3)[:3])
for x in (40, 41, 46, 47):
    for y in range(8, 8 + rnd.randint(5, 8)):
        px(x, y, noisy(HAIR, 3)[:3])

# ---- Cuerpo: ropa podrida, rota, con la piel asomando y percebes
fill(16, 20, 40, 32, RAGS)
fill(20, 16, 36, 20, RAGS_DARK)
for _ in range(30):   # agujeros: la piel hinchada se ve
    x, y = rnd.randint(16, 39), rnd.randint(20, 31)
    px(x, y, noisy(SKIN, 6)[:3])
blotches(16, 20, 40, 32, 10, BARNACLE)

# ---- Brazos: piel desnuda, larga, con manchas y percebes; manos oscuras
fill(40, 20, 56, 32, SKIN)
fill(44, 16, 52, 20, SKIN_DARK)
fill(32, 52, 48, 64, SKIN)
fill(36, 48, 44, 52, SKIN_DARK)
blotches(40, 20, 56, 32, 14, BRUISE)
blotches(32, 52, 48, 64, 14, BRUISE)
blotches(40, 20, 56, 30, 6, BARNACLE)
blotches(32, 52, 48, 62, 6, BARNACLE)
fill(40, 30, 56, 32, SKIN_DARK)
fill(32, 62, 48, 64, SKIN_DARK)

# ---- Piernas: harapos y piel; pies hinchados
fill(0, 20, 16, 32, RAGS)
fill(16, 52, 32, 64, RAGS)
for _ in range(16):
    px(rnd.randint(0, 15), rnd.randint(20, 31), noisy(SKIN, 6)[:3])
    px(rnd.randint(16, 31), rnd.randint(52, 63), noisy(SKIN, 6)[:3])
fill(0, 29, 16, 32, SKIN_DARK)
fill(16, 61, 32, 64, SKIN_DARK)
fill(4, 16, 12, 20, RAGS_DARK)
fill(20, 48, 28, 52, RAGS_DARK)
fill(8, 16, 12, 20, SKIN_DARK)
fill(24, 48, 28, 52, SKIN_DARK)

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'abajo.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print(out)
if len(sys.argv) > 1:
    S = 12
    front = Image.new('RGBA', (16, 32), (40, 70, 90, 255))
    front.alpha_composite(img.crop((8, 8, 16, 16)), (4, 0))
    front.alpha_composite(img.crop((40, 8, 48, 16)), (4, 0))
    front.alpha_composite(img.crop((20, 20, 28, 32)), (4, 8))
    front.alpha_composite(img.crop((44, 20, 48, 32)), (0, 8))
    front.alpha_composite(img.crop((36, 52, 40, 64)), (12, 8))
    front.alpha_composite(img.crop((4, 20, 8, 32)), (4, 20))
    front.alpha_composite(img.crop((20, 52, 24, 64)), (8, 20))
    sheet = Image.new('RGBA', (64, 64), (70, 70, 70, 255)); sheet.alpha_composite(img)
    view = Image.new('RGBA', (64 * 8 + 16 * S + 20, max(64 * 8, 32 * S)), (40, 40, 40, 255))
    view.alpha_composite(sheet.resize((64 * 8, 64 * 8), Image.NEAREST))
    view.alpha_composite(front.resize((16 * S, 32 * S), Image.NEAREST), (64 * 8 + 10, 0))
    view.save(sys.argv[1])
