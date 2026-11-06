"""
El Ahogado: skin de jugador de 64x64 (modelo clásico) para un maniquí que nada bajo el agua. Una mujer ahogada: piel
gris verdosa e hinchada, el pelo negro, largo y mojado que le tapa la cara (entre los mechones se ve un solo ojo,
blanco), y un camisón blanco, sucio y roto que le llega a las rodillas. Las manos y los pies, morados de frío.
Salida: assets/terror/textures/entity/ahogado.png
Uso: python fuentes/ahogado.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(4471)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
px = img.load()

SKIN = (138, 156, 146)
SKIN_D = (116, 134, 126)
SKIN_DD = (96, 106, 104)
COLD = (98, 92, 110)
HAIR = (14, 14, 16)
HAIR_L = (34, 33, 38)
GOWN = (196, 198, 194)
GOWN_D = (158, 160, 154)
DIRT = (122, 120, 104)
EYE = (226, 230, 224)


def put(x, y, c, noise=4):
    n = rnd.randint(-noise, noise)
    px[x, y] = tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(box, c, noise=4):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            put(x, y, c, noise)


def part(x, y, w, h, d):
    return {'top': (x + d, y, x + d + w, y + d), 'bottom': (x + d + w, y, x + d + 2 * w, y + d),
            'right': (x, y + d, x + d, y + d + h), 'front': (x + d, y + d, x + d + w, y + d + h),
            'left': (x + d + w, y + d, x + 2 * d + w, y + d + h), 'back': (x + 2 * d + w, y + d, x + 2 * d + 2 * w, y + d + h)}


HEAD, BODY = part(0, 0, 8, 8, 8), part(16, 16, 8, 12, 4)
ARMS = [part(40, 16, 4, 12, 4), part(32, 48, 4, 12, 4)]
LEGS = [part(0, 16, 4, 12, 4), part(16, 48, 4, 12, 4)]
HAT = part(32, 0, 8, 8, 8)          # la segunda capa de la cabeza: el pelo que cae

# Piel en todo, con manchas (hinchada, gris verdosa)
for p in [HEAD, BODY] + ARMS + LEGS:
    for box in p.values():
        fill(box, SKIN, 5)
        for _ in range((box[2] - box[0]) * (box[3] - box[1]) // 6):
            put(rnd.randrange(box[0], box[2]), rnd.randrange(box[1], box[3]), SKIN_D, 4)

# La cabeza: pelo negro arriba, atrás y a los costados
for side in ('top', 'back', 'right', 'left'):
    fill(HEAD[side], HAIR, 3)
    x0, y0, x1, y1 = HEAD[side]
    for _ in range(6):
        put(rnd.randrange(x0, x1), rnd.randrange(y0, y1), HAIR_L, 3)
# La cara, debajo del pelo: piel oscura, y un ojo blanco (el que se ve entre los mechones)
fx, fy = HEAD['front'][0], HEAD['front'][1]
fill(HEAD['front'], SKIN_DD, 4)
put(fx + 5, fy + 4, EYE, 3)
put(fx + 6, fy + 4, EYE, 3)
put(fx + 5, fy + 5, SKIN_D, 3)
put(fx + 2, fy + 6, HAIR, 2)   # la boca, apenas
put(fx + 3, fy + 6, HAIR, 2)

# La segunda capa: los mechones mojados que le caen por la cara (dejando el ojo) y por los costados y la espalda
hx, hy = HAT['front'][0], HAT['front'][1]
for x in range(8):
    # cada columna de pelo cae hasta una altura distinta; en las columnas 5-6 queda el hueco del ojo
    length = 8 if x in (0, 1, 2, 3, 7) else 3
    for y in range(length):
        if x == 4 and y in (4, 5):
            continue
        put(hx + x, hy + y, HAIR if (x + y) % 3 else HAIR_L, 3)
for side in ('top', 'back', 'right', 'left'):
    x0, y0, x1, y1 = HAT[side]
    for y in range(y0, y1):
        for x in range(x0, x1):
            put(x, y, HAIR if rnd.random() < 0.8 else HAIR_L, 3)

# El camisón: blanco sucio, del pecho a las rodillas, con manchas y roto abajo
def gown(box, rows):
    x0, y0, x1, y1 = box
    for y in range(y0, min(y1, y0 + rows)):
        for x in range(x0, x1):
            put(x, y, GOWN if rnd.random() < 0.8 else GOWN_D, 4)
    # Chorreado de agua: alguna columna más gris, de arriba hacia abajo; y muy poca mugre
    for _ in range(max(1, (x1 - x0) // 4)):
        x = rnd.randrange(x0, x1)
        start = rnd.randrange(y0, min(y1, y0 + rows))
        for y in range(start, min(y1, y0 + rows)):
            put(x, y, GOWN_D, 3)
    for _ in range(max(1, (x1 - x0) * rows // 24)):
        put(rnd.randrange(x0, x1), rnd.randrange(y0, min(y1, y0 + rows)), DIRT, 4)


for side in ('front', 'back', 'right', 'left'):
    gown(BODY[side], 12)
fill(BODY['top'], GOWN, 4)
for leg in LEGS:
    for side in ('front', 'back', 'right', 'left'):
        x0, y0, x1, y1 = leg[side]
        gown(leg[side], 5)
        for x in range(x0, x1):                 # el borde roto, desparejo
            if rnd.random() < 0.5:
                put(x, y0 + 5, GOWN_D, 4)
for arm in ARMS:                                # mangas cortas
    for side in ('front', 'back', 'right', 'left'):
        gown(arm[side], 3)
    fill(arm['top'], GOWN, 4)

# El pelo, que cae mojado sobre los hombros y el pecho (adelante y atrás, a los costados del cuello)
for side in ('front', 'back'):
    x0, y0, x1, y1 = BODY[side]
    for x in (x0, x0 + 1, x1 - 2, x1 - 1):
        for y in range(y0, y0 + rnd.randint(3, 5)):
            put(x, y, HAIR if rnd.random() < 0.8 else HAIR_L, 3)

# Manos y pies morados, con los dedos más oscuros
for p in ARMS + LEGS:
    for side in ('front', 'back', 'right', 'left'):
        x0, y0, x1, y1 = p[side]
        fill((x0, y1 - 2, x1, y1), COLD, 4)
    fill(p['bottom'], COLD, 4)

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'ahogado.png')
img.save(out)
print(out)
if len(sys.argv) > 1:
    img.resize((64 * 8, 64 * 8), Image.NEAREST).save(sys.argv[1])
