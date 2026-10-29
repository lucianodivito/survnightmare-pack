"""
El Gigante Hueco (jefe colosal del mundo): skin de jugador de 64x64 (modelo clásico), para un maniquí enorme.
Huesudo y pálido como un cadáver seco: costillas marcadas, cuencas vacías con una lucecita al fondo, una boca rasgada,
brazos y piernas flacos, harapos en la cintura, y un farol encendido metido en el pecho (su punto débil).
Salida: assets/terror/textures/entity/gigante.png
Uso: python fuentes/gigante.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(7311)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
px = img.load()

BONE = (178, 172, 158)
BONE_D = (128, 122, 110)
BONE_DD = (82, 78, 72)
HOLE = (16, 12, 12)
RAG = (60, 52, 46)
RAG_D = (40, 34, 30)
LAMP = (255, 196, 92)
LAMP_L = (255, 238, 170)
LAMP_D = (200, 120, 40)
IRON = (52, 48, 46)


def put(x, y, c, noise=5):
    n = rnd.randint(-noise, noise)
    px[x, y] = tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(box, c, noise=6):
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

# Hueso en todo el cuerpo, con manchas más oscuras
for p in [HEAD, BODY] + ARMS + LEGS:
    for box in p.values():
        fill(box, BONE)
        for _ in range((box[2] - box[0]) * (box[3] - box[1]) // 6):
            put(rnd.randrange(box[0], box[2]), rnd.randrange(box[1], box[3]), BONE_D, 6)

# La cara: cuencas vacías con una lucecita, la nariz hundida, la boca rasgada con dientes
fx, fy = HEAD['front'][0], HEAD['front'][1]
for x, y in [(1, 2), (2, 2), (1, 3), (2, 3), (5, 2), (6, 2), (5, 3), (6, 3)]:
    put(fx + x, fy + y, HOLE, 2)
put(fx + 2, fy + 3, LAMP_D, 2)
put(fx + 5, fy + 3, LAMP_D, 2)
put(fx + 3, fy + 4, BONE_DD, 2)
put(fx + 4, fy + 4, BONE_DD, 2)
for x in range(1, 7):
    put(fx + x, fy + 6, HOLE if x % 2 else BONE, 3)
put(fx + 0, fy + 6, BONE_DD, 2)
put(fx + 7, fy + 6, BONE_DD, 2)
for x in range(8):                                       # la frente, más oscura arriba
    put(fx + x, fy, BONE_D, 4)

# El torso: costillas marcadas y el farol en el pecho
bx, by = BODY['front'][0], BODY['front'][1]
for y in (1, 3, 5, 7):
    for x in range(8):
        if x not in (3, 4):
            put(bx + x, by + y, BONE_DD, 4)
for y in range(1, 9):                                     # el esternón
    put(bx + 3, by + y, BONE_D, 3)
    put(bx + 4, by + y, BONE_D, 3)
lamp = {(2, 2): IRON, (3, 2): IRON, (4, 2): IRON, (5, 2): IRON,
        (2, 3): IRON, (3, 3): LAMP_L, (4, 3): LAMP, (5, 3): IRON,
        (2, 4): IRON, (3, 4): LAMP, (4, 4): LAMP_D, (5, 4): IRON,
        (2, 5): IRON, (3, 5): IRON, (4, 5): IRON, (5, 5): IRON}
for (x, y), c in lamp.items():
    put(bx + x, by + y, c, 2)
bk = BODY['back']
for y in range(bk[1] + 1, bk[3] - 3):                     # la columna en la espalda
    put(bk[0] + 3, y, BONE_DD, 3)
    put(bk[0] + 4, y, BONE_D, 3)

# Harapos en la cintura y en lo alto de las piernas
for box in BODY.values():
    if box[3] - box[1] == 12:
        fill((box[0], box[3] - 3, box[2], box[3]), RAG, 6)
        for x in range(box[0], box[2]):
            if rnd.random() < 0.5:
                put(x, box[3] - 3, RAG_D, 4)
for leg in LEGS:
    for side in ('front', 'back', 'right', 'left'):
        x0, y0, x1, y1 = leg[side]
        fill((x0, y0, x1, y0 + 3), RAG, 6)
        for x in range(x0, x1):
            if rnd.random() < 0.5:
                put(x, y0 + 3, RAG_D, 4)

# Manos y pies: puntas oscuras
for p in ARMS + LEGS:
    for side in ('front', 'back', 'right', 'left'):
        x0, y0, x1, y1 = p[side]
        fill((x0, y1 - 1, x1, y1), BONE_DD, 4)

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'gigante.png')
img.save(out)
print(out)
if len(sys.argv) > 1:
    img.resize((64 * 8, 64 * 8), Image.NEAREST).save(sys.argv[1])
