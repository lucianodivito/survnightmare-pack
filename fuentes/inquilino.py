"""
El Inquilino (jefe de El Cuenco): skin de jugador de 64x64 (brazos anchos) para el maniquí del jefe.
Un cadáver flaco de piel gris azulada y mejillas hundidas, ojos negros con un puntito blanco, lágrimas negras que le
bajan por la cara, una sonrisa demasiado ancha llena de dientes finitos, pelo negro ralo que le cuelga (en la capa de
afuera) y un traje viejo con la camisa manchada de sangre seca. Dedos largos y oscuros.
El plugin la usa con terror:entity/inquilino (assets/terror/textures/entity/inquilino.png).
Uso: python fuentes/inquilino.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(404)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

SKIN = (150, 156, 158)      # gris azulado, de muerto
SHADOW = (104, 110, 114)    # lo hundido
SUIT = (46, 45, 48)
SHIRT = (168, 162, 146)     # blanco amarillento, sucio
BLOOD = (92, 18, 18)
PANTS = (28, 27, 30)
SHOES = (16, 15, 17)
BLACK = (6, 5, 6)
HAIR = (14, 13, 14)


def noisy(c, amount=6):
    n = rnd.randint(-amount, amount)
    return tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(x0, y0, x1, y1, color, amount=6):
    for y in range(y0, y1):
        for x in range(x0, x1):
            img.putpixel((x, y), noisy(color, amount))


def px(x, y, color, a=255):
    img.putpixel((x, y), tuple(color[:3]) + (a,))


# ---- Cabeza: piel de muerto en todas las caras, más oscura arriba y atrás
fill(0, 8, 32, 16, SKIN)
fill(8, 0, 24, 8, SHADOW)
fill(24, 8, 32, 16, SHADOW)
# Cara (8..15 x 8..15): sienes y mejillas hundidas
for y in range(8, 16):
    px(8, y, noisy(SHADOW, 4))
    px(15, y, noisy(SHADOW, 4))
for x, y in ((9, 13), (14, 13), (9, 12), (14, 12)):
    px(x, y, noisy(SHADOW, 4))
# Ojos: dos huecos negros de 2x2, con un puntito blanco que te mira
for x in (9, 10, 13, 14):
    for y in (10, 11):
        px(x, y, BLACK)
px(10, 10, (235, 235, 230))
px(13, 10, (235, 235, 230))
# Lágrimas negras que bajan de los ojos
for x, ys in ((9, (12, 13)), (14, (12, 13, 14)), (10, (12,))):
    for y in ys:
        px(x, y, (22, 18, 20))
# La sonrisa: de lado a lado, negra por dentro, con dientes finitos arriba y abajo
for x in range(8, 16):
    px(x, 14, BLACK)
for x in range(9, 15):
    px(x, 15, BLACK)
for x in range(8, 16, 2):
    px(x, 14, (214, 206, 180))   # dientes de arriba
for x in range(10, 14, 2):
    px(x, 15, (190, 180, 152))   # dientes de abajo
px(8, 13, BLACK)                  # las comisuras, que suben
px(15, 13, BLACK)

# ---- Capa de afuera de la cabeza (pelo): mechones negros que cuelgan por los costados, atrás y arriba
for x in range(40, 48):          # arriba (40..47 x 0..7)
    for y in range(0, 8):
        if rnd.random() < 0.55:
            px(x, y, noisy(HAIR, 3))
for face_x0 in (32, 48, 56):     # derecha, izquierda, atrás (de 8 de ancho, filas 8..15)
    for x in range(face_x0, face_x0 + 8):
        length = rnd.randint(3, 8)
        for y in range(8, 8 + length):
            px(x, y, noisy(HAIR, 3))
for x in (40, 41, 46, 47):       # al frente, solo en las puntas: le tapa un poco la cara
    for y in range(8, 8 + rnd.randint(2, 6)):
        px(x, y, noisy(HAIR, 3))

# ---- Cuerpo: saco gastado, camisa sucia con sangre seca, corbata negra
fill(16, 20, 40, 32, SUIT)
fill(20, 16, 36, 20, SUIT)
for y in range(20, 32):
    for x in range(22, 26):
        px(x, y, noisy(SHIRT, 6))
for y in range(20, 30):
    px(23, y, (12, 11, 13))
    px(24, y, (12, 11, 13))
for _ in range(14):              # manchas de sangre en la camisa y el saco
    x, y = rnd.randint(20, 27), rnd.randint(21, 31)
    px(x, y, noisy(BLOOD, 8))
for x, y in ((22, 21), (22, 22), (25, 23), (25, 24), (25, 25)):   # un chorro que baja del cuello
    px(x, y, noisy(BLOOD, 6))
for _ in range(10):              # rasgones
    x, y = rnd.randint(16, 39), rnd.randint(20, 31)
    px(x, y, (30, 29, 32))

# ---- Brazos (derecho: 40-56 x 16-32; izquierdo: 32-48 x 48-64): mangas, y manos grises de dedos largos y oscuros
fill(40, 20, 56, 32, SUIT)
fill(44, 16, 52, 20, SUIT)
fill(32, 52, 48, 64, SUIT)
fill(36, 48, 44, 52, SUIT)
fill(40, 28, 56, 32, SKIN)
fill(32, 60, 48, 64, SKIN)
fill(48, 16, 52, 20, SHADOW)
fill(40, 48, 44, 52, SHADOW)
for x in range(40, 56, 2):       # dedos que se oscurecen en las puntas
    px(x, 31, (60, 62, 66))
for x in range(32, 48, 2):
    px(x, 63, (60, 62, 66))

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
    # Vista de frente (con la capa de pelo encima de la cara) y la textura entera
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
