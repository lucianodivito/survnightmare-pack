"""
El Chico (jefe de El Patio de nadie): skin de jugador de 64x64 (brazos anchos) para el maniquí del jefe, que el plugin
achica al tamaño de un chico. Pálido, de ojos negros vacíos y una boca chiquita y negra, pelo negro largo que le tapa
un ojo (en la capa de afuera), un camisón blanco sucio con barro, y descalzo (piernas y pies pálidos, con tierra).
El plugin la usa con terror:entity/chico (assets/terror/textures/entity/chico.png).
Uso: python fuentes/chico.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(1999)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

SKIN = (206, 204, 198)       # pálido, casi blanco
SHADOW = (160, 158, 152)
GOWN = (214, 210, 196)       # camisón blanco, viejo
DIRT = (96, 84, 68)
BLACK = (6, 5, 6)
HAIR = (12, 11, 12)


def noisy(c, amount=6):
    n = rnd.randint(-amount, amount)
    return tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(x0, y0, x1, y1, color, amount=6):
    for y in range(y0, y1):
        for x in range(x0, x1):
            img.putpixel((x, y), noisy(color, amount))


def px(x, y, color):
    img.putpixel((x, y), tuple(color[:3]) + (255,))


def stains(x0, y0, x1, y1, count, color=DIRT):
    for _ in range(count):
        px(rnd.randint(x0, x1 - 1), rnd.randint(y0, y1 - 1), noisy(color, 10)[:3])


# ---- Cabeza: pálida; pelo negro arriba, atrás y a los costados (abajo de la capa de afuera)
fill(0, 8, 32, 16, SKIN)
fill(8, 0, 24, 8, HAIR, 3)
fill(24, 8, 32, 16, HAIR, 3)
for y in range(8, 13):
    for x in (0, 1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19, 20, 21, 22, 23):
        px(x, y, noisy(HAIR, 3))
# Cara (8..15 x 8..15): ojos negros grandes, ojeras, boca chiquita
for x in (9, 10, 13, 14):
    for y in (10, 11, 12):
        px(x, y, BLACK)
for x in (9, 10, 13, 14):
    px(x, 13, SHADOW)
for x in (11, 12):
    px(x, 14, BLACK)
px(11, 15, (40, 30, 30))
# ---- Capa de afuera (pelo): flequillo largo que le tapa el ojo derecho, y mechones que caen
for x in range(40, 48):
    for y in range(0, 8):
        px(x, y, noisy(HAIR, 3))
for x in range(40, 48):       # al frente: flequillo
    length = 1
    if x in (40, 41, 42, 43):   # el lado del ojo derecho: el pelo baja hasta tapar el ojo
        length = rnd.randint(5, 7)
    for y in range(8, 8 + length):
        px(x, y, noisy(HAIR, 3))
for x0 in (32, 48, 56):       # costados y atrás: pelo largo hasta abajo
    for x in range(x0, x0 + 8):
        for y in range(8, 8 + rnd.randint(6, 8)):
            px(x, y, noisy(HAIR, 3))

# ---- Cuerpo: camisón blanco, sucio, con barro abajo
fill(16, 20, 40, 32, GOWN)
fill(20, 16, 36, 20, GOWN)
stains(16, 28, 40, 32, 12)
stains(16, 20, 40, 28, 3)
for x in range(22, 26):   # el cuello del camisón, un poco más oscuro
    px(x, 20, (180, 176, 162))

# ---- Brazos: mangas cortas del camisón arriba, brazos pálidos y flacos, manos sucias
fill(40, 20, 56, 32, SKIN)
fill(44, 16, 52, 20, GOWN)
fill(40, 20, 56, 23, GOWN)
fill(32, 52, 48, 64, SKIN)
fill(36, 48, 44, 52, GOWN)
fill(32, 52, 48, 55, GOWN)
fill(48, 16, 52, 20, SHADOW)
fill(40, 48, 44, 52, SHADOW)
stains(40, 30, 56, 32, 5)
stains(32, 62, 48, 64, 5)

# ---- Piernas: el camisón llega a las rodillas; después, piernas pálidas y pies descalzos, con tierra
fill(0, 20, 16, 32, SKIN)
fill(4, 16, 12, 20, GOWN)
fill(0, 20, 16, 25, GOWN)
fill(16, 52, 32, 64, SKIN)
fill(20, 48, 28, 52, GOWN)
fill(16, 52, 32, 57, GOWN)
stains(0, 23, 16, 25, 4)
stains(16, 55, 32, 57, 4)
fill(0, 30, 16, 32, (120, 110, 96), 8)    # pies con barro
fill(16, 62, 32, 64, (120, 110, 96), 8)
fill(8, 16, 12, 20, (110, 100, 86), 8)    # plantas de los pies
fill(24, 48, 28, 52, (110, 100, 86), 8)

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'chico.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print(out)
if len(sys.argv) > 1:
    S = 12
    front = Image.new('RGBA', (16, 32), (120, 140, 110, 255))
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
