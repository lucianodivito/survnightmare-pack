"""
La Figura (biomas fríos, con nevada): skin de jugador de 64x64 (modelo clásico) para un maniquí alto y flaco.
Casi blanca, del color de la nieve sucia, para que se pierda entre la nevada: sin ropa, con las costillas apenas
marcadas, la cara lisa (sin nariz ni boca) con dos cuencas largas y negras, y las manos y los pies grises,
como congelados. Lo que se ve de lejos es la silueta y las dos manchas negras de la cara.
Salida: assets/terror/textures/entity/figura.png
Uso: python fuentes/figura.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(2209)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
px = img.load()

SKIN = (214, 218, 222)
SKIN_D = (186, 191, 197)
SKIN_DD = (150, 156, 164)
COLD = (122, 130, 140)
HOLE = (12, 12, 14)
HOLE_D = (34, 34, 38)


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

# Piel pálida en todo, con sombras suaves (manchas apenas más oscuras)
for p in [HEAD, BODY] + ARMS + LEGS:
    for box in p.values():
        fill(box, SKIN)
        for _ in range((box[2] - box[0]) * (box[3] - box[1]) // 7):
            put(rnd.randrange(box[0], box[2]), rnd.randrange(box[1], box[3]), SKIN_D, 3)

# La cara: lisa, sin nariz ni boca; solo dos cuencas largas y negras, que se hunden (más claras arriba y abajo)
fx, fy = HEAD['front'][0], HEAD['front'][1]
for x0 in (1, 5):
    for x in (x0, x0 + 1):
        put(fx + x, fy + 2, SKIN_DD, 2)
        put(fx + x, fy + 3, HOLE, 1)
        put(fx + x, fy + 4, HOLE, 1)
        put(fx + x, fy + 5, HOLE_D, 2)
        put(fx + x, fy + 6, SKIN_DD, 2)
put(fx + 3, fy + 6, SKIN_D, 2)   # una sombra mínima donde tendría la boca
put(fx + 4, fy + 6, SKIN_D, 2)
# Arriba, la cabeza un poco más gris (sin pelo)
fill(HEAD['top'], SKIN_D, 4)

# El torso: costillas apenas marcadas, el esternón y la panza hundida
bx, by = BODY['front'][0], BODY['front'][1]
for y in (2, 4, 6):
    for x in range(1, 7):
        if x not in (3, 4):
            put(bx + x, by + y, SKIN_DD, 3)
for y in range(8, 11):
    for x in range(2, 6):
        put(bx + x, by + y, SKIN_D, 3)
bk = BODY['back']
for y in range(bk[1] + 1, bk[3] - 1):                       # la columna
    put(bk[0] + 3, y, SKIN_DD, 3)
    put(bk[0] + 4, y, SKIN_D, 3)

# Manos y pies grises, como congelados (las últimas 3 filas), y los dedos más oscuros
for p in ARMS + LEGS:
    for side in ('front', 'back', 'right', 'left'):
        x0, y0, x1, y1 = p[side]
        fill((x0, y1 - 2, x1, y1), SKIN_DD, 3)
        fill((x0, y1 - 1, x1, y1), COLD, 3)
    fill(p['bottom'], COLD, 4)

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'figura.png')
img.save(out)
print(out)
if len(sys.argv) > 1:
    img.resize((64 * 8, 64 * 8), Image.NEAREST).save(sys.argv[1])
