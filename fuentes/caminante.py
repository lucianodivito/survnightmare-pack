"""
El Caminante (jefe de El Campo de postes): skin de jugador de 64x64 (brazos anchos) para el maniquí del jefe, que el
plugin estira a casi tres bloques de alto. Sin cara: piel gris lisa, apenas una sombra donde irían los ojos; un abrigo
largo y negro hasta las rodillas, sombrero de ala ancha (en la capa de afuera) y manos pálidas de dedos largos.
El plugin la usa con terror:entity/caminante (assets/terror/textures/entity/caminante.png).
Uso: python fuentes/caminante.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(1717)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

SKIN = (178, 178, 172)
SHADE = (150, 150, 145)
COAT = (26, 25, 28)
COAT_EDGE = (40, 38, 42)
PANTS = (20, 19, 22)
HAT = (18, 17, 19)
HAT_BAND = (48, 40, 36)


def noisy(c, amount=5):
    n = rnd.randint(-amount, amount)
    return tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(x0, y0, x1, y1, color, amount=5):
    for y in range(y0, y1):
        for x in range(x0, x1):
            img.putpixel((x, y), noisy(color, amount))


def px(x, y, color):
    img.putpixel((x, y), tuple(color[:3]) + (255,))


# ---- Cabeza: piel lisa en todas las caras. La cara no tiene nada: apenas dos sombras y una línea donde iría la boca
fill(0, 8, 32, 16, SKIN, 4)
fill(8, 0, 24, 8, SHADE, 4)
for x in (9, 10, 13, 14):
    px(x, 11, SHADE)
for x in range(10, 14):
    px(x, 14, (164, 164, 158))
# ---- Sombrero (capa de afuera): copa arriba y una banda alrededor, y el ala que tapa la frente
for x in range(40, 48):
    for y in range(0, 8):
        px(x, y, noisy(HAT, 3)[:3])
for x0 in (32, 40, 48, 56):
    for x in range(x0, x0 + 8):
        px(x, 8, noisy(HAT, 3)[:3])
        px(x, 9, noisy(HAT_BAND, 3)[:3])
        px(x, 10, noisy(HAT, 3)[:3])

# ---- Cuerpo: abrigo negro cerrado, con botones y el borde un poco más claro
fill(16, 20, 40, 32, COAT)
fill(20, 16, 36, 20, COAT)
for y in range(20, 32):
    px(23, y, COAT_EDGE)
for y in range(22, 32, 3):
    px(24, y, (60, 56, 52))
for x in range(20, 28):
    px(x, 20, COAT_EDGE)   # cuello alto

# ---- Brazos: mangas del abrigo hasta abajo; manos pálidas y largas (las dos últimas filas)
fill(40, 20, 56, 32, COAT)
fill(44, 16, 52, 20, COAT)
fill(32, 52, 48, 64, COAT)
fill(36, 48, 44, 52, COAT)
fill(40, 29, 56, 32, SKIN, 4)
fill(32, 61, 48, 64, SKIN, 4)
fill(48, 16, 52, 20, SKIN, 4)
fill(40, 48, 44, 52, SKIN, 4)
for x in range(40, 56, 2):
    px(x, 31, SHADE)
for x in range(32, 48, 2):
    px(x, 63, SHADE)

# ---- Piernas: el abrigo baja hasta las rodillas; después, pantalón negro y zapatos
fill(0, 20, 16, 27, COAT)
fill(16, 52, 32, 59, COAT)
fill(0, 27, 16, 32, PANTS)
fill(16, 59, 32, 64, PANTS)
fill(4, 16, 12, 20, COAT)
fill(20, 48, 28, 52, COAT)
fill(8, 16, 12, 20, (12, 12, 14), 2)
fill(24, 48, 28, 52, (12, 12, 14), 2)

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'caminante.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print(out)
if len(sys.argv) > 1:
    S = 12
    front = Image.new('RGBA', (16, 32), (200, 140, 110, 255))
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
