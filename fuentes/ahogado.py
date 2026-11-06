"""
El Ahogado: skin de jugador de 64x64 (modelo clásico) para un maniquí que nada bajo el agua. Un pescador ahogado (no la
"llorona" del Empapado ni el gigante pálido del Fondo): un piloto de lluvia amarillo, desteñido y sucio, con la capucha
puesta y enredado en una red de pesca; la cara hinchada, entre azul y morada, los ojos lechosos y la boca abierta;
botas de goma negras.
Salida: assets/terror/textures/entity/ahogado.png
Uso: python fuentes/ahogado.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(8812)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
px = img.load()

FACE = (118, 128, 152)
FACE_D = (96, 98, 128)
BRUISE = (104, 84, 116)
EYE = (214, 218, 210)
EYE_D = (150, 156, 150)
MOUTH = (22, 16, 22)
COAT = (166, 144, 70)
COAT_D = (134, 114, 56)
COAT_DD = (104, 86, 34)
NET = (58, 46, 34)
BOOT = (26, 26, 28)
BOOT_L = (48, 48, 52)
HAND = FACE_D


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
HAT = part(32, 0, 8, 8, 8)          # la segunda capa de la cabeza: la capucha


def coat(box):
    """Tela de piloto: amarilla, desteñida a manchas, con pliegues más oscuros y mugre."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            put(x, y, COAT if rnd.random() < 0.88 else COAT_D, 4)
    for _ in range(max(1, (x1 - x0) * (y1 - y0) // 24)):
        put(rnd.randrange(x0, x1), rnd.randrange(y0, y1), COAT_DD, 4)


# La cara: hinchada, azul morada, con moretones; los ojos lechosos (sin pupila) y la boca abierta
for box in HEAD.values():
    fill(box, FACE, 5)
fx, fy = HEAD['front'][0], HEAD['front'][1]
for x, y in [(1, 2), (6, 2), (0, 5), (7, 4), (3, 1), (4, 7)]:
    put(fx + x, fy + y, BRUISE, 4)
for x0 in (1, 5):
    put(fx + x0, fy + 3, EYE, 3)
    put(fx + x0 + 1, fy + 3, EYE, 3)
    put(fx + x0, fy + 4, EYE_D, 3)
    put(fx + x0 + 1, fy + 4, EYE, 3)
    put(fx + x0, fy + 2, FACE_D, 3)
    put(fx + x0 + 1, fy + 2, FACE_D, 3)
for x in (3, 4):
    put(fx + x, fy + 5, MOUTH, 2)
    put(fx + x, fy + 6, MOUTH, 2)
put(fx + 2, fy + 6, FACE_D, 3)
put(fx + 5, fy + 6, FACE_D, 3)

# La capucha (segunda capa): todo el contorno de la cabeza amarillo, dejando la cara a la vista
for side in ('top', 'back', 'right', 'left'):
    coat(HAT[side])
hx, hy = HAT['front'][0], HAT['front'][1]
for x in range(8):
    put(hx + x, hy, COAT_D, 4)                 # el borde de la capucha sobre la frente
for y in range(1, 8):
    put(hx, hy + y, COAT_D, 4)
    put(hx + 7, hy + y, COAT_D, 4)

# El piloto: torso, brazos y hasta la rodilla
for side in ('front', 'back', 'right', 'left', 'top'):
    coat(BODY[side])
for arm in ARMS:
    for side in ('front', 'back', 'right', 'left', 'top'):
        coat(arm[side])
bx, by = BODY['front'][0], BODY['front'][1]
for y in range(by, by + 12):                   # el cierre del medio, oscuro
    put(bx + 3, y, COAT_DD, 3)
for y in (by + 3, by + 6, by + 9):             # los broches
    put(bx + 4, y, BOOT_L, 2)

# La red de pesca, enredada en diagonal sobre el pecho y la espalda, y en un brazo
# (cuerdas en diagonal que se cruzan, cada 4: un rombo)
def net(box):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            if (x - x0 + y - y0) % 4 == 0 or (x - x0 - (y - y0)) % 4 == 0:
                put(x, y, NET, 3)


x0, y0, x1, y1 = BODY['front']
net((x0, y0 + 2, x1, y0 + 9))
x0, y0, x1, y1 = BODY['back']
net((x0, y0, x1, y0 + 7))
x0, y0, x1, y1 = ARMS[0]['front']
net((x0, y0, x1, y0 + 6))

# Las piernas: el piloto hasta la rodilla, y las botas de goma negras
for leg in LEGS:
    for side in ('front', 'back', 'right', 'left'):
        x0, y0, x1, y1 = leg[side]
        coat((x0, y0, x1, y0 + 5))
        fill((x0, y0 + 5, x1, y1), BOOT, 3)
        for x in range(x0, x1):
            put(x, y0 + 5, BOOT_L, 3)          # el borde de la bota
    fill(leg['bottom'], BOOT, 3)

# Las manos: hinchadas y moradas (las últimas 2 filas del brazo)
for arm in ARMS:
    for side in ('front', 'back', 'right', 'left'):
        x0, y0, x1, y1 = arm[side]
        fill((x0, y1 - 2, x1, y1), HAND, 4)
    fill(arm['bottom'], HAND, 4)

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'ahogado.png')
img.save(out)
print(out)
if len(sys.argv) > 1:
    img.resize((64 * 8, 64 * 8), Image.NEAREST).save(sys.argv[1])
