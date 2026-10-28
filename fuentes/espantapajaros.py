"""
El Espantapájaros (jefe de El Trigal) y los espantapájaros del trigal: todos con la misma skin, para que no se sepa
cuál es él. Skin de jugador de 64x64 (brazos anchos): cabeza de bolsa de arpillera atada con soga al cuello, ojos de
botón (uno colgando de un hilo), una boca cosida de lado a lado; sombrero de paja (en la capa de afuera); camisa a
cuadros gastada, paja saliendo de las mangas y del pantalón, pantalón con parches.
El plugin la usa con terror:entity/espantapajaros (assets/terror/textures/entity/espantapajaros.png).
Uso: python fuentes/espantapajaros.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(1888)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

SACK = (168, 140, 96)        # arpillera
SACK_DARK = (128, 104, 70)
STRAW = (214, 184, 92)
STRAW_DARK = (170, 140, 60)
ROPE = (120, 96, 60)
RED = (112, 30, 28)          # cuadros de la camisa
RED_DARK = (58, 20, 20)
PANTS = (78, 66, 52)
PATCH = (110, 92, 60)
BLACK = (14, 12, 12)


def noisy(c, amount=7):
    n = rnd.randint(-amount, amount)
    return tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(x0, y0, x1, y1, color, amount=7):
    for y in range(y0, y1):
        for x in range(x0, x1):
            img.putpixel((x, y), noisy(color, amount))


def px(x, y, color):
    img.putpixel((x, y), tuple(color[:3]) + (255,))


def burlap(x0, y0, x1, y1):
    """Trama de arpillera: filas y columnas un poco más oscuras."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = SACK_DARK if (x % 2 == 0 and y % 3 == 0) or (y % 2 == 0 and x % 3 == 1) else SACK
            img.putpixel((x, y), noisy(c, 6))


def plaid(x0, y0, x1, y1):
    """Cuadros rojos y negros, gastados."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = RED_DARK if (x % 4 < 2) ^ (y % 4 < 2) else RED
            if rnd.random() < 0.08:
                c = (c[0] - 20, c[1] - 6, c[2] - 6)
            img.putpixel((x, y), noisy(c, 6))


def straw_tufts(x0, y, x1, rows=2):
    for x in range(x0, x1):
        for k in range(rnd.randint(1, rows)):
            px(x, y - k, noisy(rnd.choice((STRAW, STRAW_DARK)), 8)[:3])


# ---- Cabeza: bolsa de arpillera en todas las caras
burlap(0, 8, 32, 16)
burlap(8, 0, 24, 8)
# Cara (8..15 x 8..15): un ojo de botón negro, el otro colgando más abajo de un hilo
for x, y in ((9, 10), (10, 10), (9, 11), (10, 11)):
    px(x, y, BLACK)
px(9, 10, (60, 56, 56))
for y in (10, 11):
    px(14, y, (40, 36, 30))           # el hilo del que cuelga
for x, y in ((13, 12), (14, 12), (13, 13), (14, 13)):
    px(x, y, BLACK)
# La boca cosida: una línea de lado a lado con puntadas
for x in range(9, 15):
    px(x, 14, (60, 30, 26))
for x in range(9, 15, 2):
    px(x, 13, BLACK)
    px(x, 15, BLACK)
# Soga al cuello (abajo de la cabeza, en las 4 caras de la fila de abajo)
for x in range(0, 32):
    px(x, 15, noisy(ROPE, 6)[:3])
for x in range(9, 15, 2):            # las puntadas de la boca por encima de la soga
    px(x, 15, BLACK)

# ---- Capa de afuera de la cabeza: el sombrero de paja (arriba y una banda alrededor)
for x in range(40, 48):
    for y in range(0, 8):
        px(x, y, noisy(rnd.choice((STRAW, STRAW, STRAW_DARK)), 8)[:3])
for x0 in (32, 40, 48, 56):
    for x in range(x0, x0 + 8):
        px(x, 8, noisy(STRAW_DARK, 8)[:3])
        px(x, 9, noisy(STRAW, 8)[:3])
        if rnd.random() < 0.3:
            px(x, 10, noisy(STRAW_DARK, 8)[:3])   # alguna paja que se escapa

# ---- Cuerpo: camisa a cuadros, con un roto y paja asomando por el cuello
plaid(16, 20, 40, 32)
plaid(20, 16, 36, 20)
straw_tufts(21, 21, 27, 2)
for x, y in ((25, 26), (26, 26), (25, 27)):   # un roto con paja
    px(x, y, noisy(STRAW, 6)[:3])

# ---- Brazos: mangas a cuadros y paja saliendo de los puños; manos de arpillera
plaid(40, 20, 56, 32)
plaid(44, 16, 52, 20)
plaid(32, 52, 48, 64)
plaid(36, 48, 44, 52)
burlap(40, 29, 56, 32)
burlap(32, 61, 48, 64)
straw_tufts(40, 31, 56, 2)
straw_tufts(32, 63, 48, 2)
fill(48, 16, 52, 20, STRAW_DARK)
fill(40, 48, 44, 52, STRAW_DARK)

# ---- Piernas: pantalón con parches; paja saliendo de abajo
fill(0, 20, 16, 32, PANTS)
fill(4, 16, 12, 20, PANTS)
fill(16, 52, 32, 64, PANTS)
fill(20, 48, 28, 52, PANTS)
fill(5, 23, 8, 26, PATCH)
fill(18, 56, 21, 59, PATCH)
straw_tufts(0, 31, 16, 3)
straw_tufts(16, 63, 32, 3)
fill(8, 16, 12, 20, STRAW_DARK)
fill(24, 48, 28, 52, STRAW_DARK)

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'espantapajaros.png')
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
