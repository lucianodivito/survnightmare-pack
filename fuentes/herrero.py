"""
El Herrero (NPC): una skin de jugador de 64x64 (modelo clásico). Barba y pelo oscuros, camisa gris arremangada,
delantal de cuero con tiras, cinturón, pantalón pardo, botas, y hollín en la cara y los antebrazos.
Salida: assets/terror/textures/entity/herrero.png (el NPC la usa con skin "pack:entity/herrero").
Uso: python fuentes/herrero.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(1612)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
px = img.load()

SKIN = (186, 136, 102)
HAIR = (42, 32, 26)
BEARD = (58, 42, 32)
SHIRT = (74, 70, 68)
APRON = (112, 72, 42)
STRAP = (78, 50, 30)
BELT = (46, 34, 26)
BUCKLE = (150, 140, 120)
PANTS = (62, 50, 40)
BOOTS = (36, 28, 24)
SOOT = (96, 80, 70)


def put(x, y, c, noise=6):
    n = rnd.randint(-noise, noise)
    px[x, y] = tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(box, c, noise=6):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            put(x, y, c, noise)


def face(name):
    """Las caras de una parte del modelo: (x0, y0, ancho, alto, profundidad) -> cajas por cara."""
    return name


def part(x, y, w, h, d):
    """Cajas de una parte (como en la textura de skin): top, bottom, right, front, left, back."""
    return {
        'top': (x + d, y, x + d + w, y + d),
        'bottom': (x + d + w, y, x + d + 2 * w, y + d),
        'right': (x, y + d, x + d, y + d + h),
        'front': (x + d, y + d, x + d + w, y + d + h),
        'left': (x + d + w, y + d, x + 2 * d + w, y + d + h),
        'back': (x + 2 * d + w, y + d, x + 2 * d + 2 * w, y + d + h),
    }


HEAD = part(0, 0, 8, 8, 8)
BODY = part(16, 16, 8, 12, 4)
RARM = part(40, 16, 4, 12, 4)
LARM = part(32, 48, 4, 12, 4)
RLEG = part(0, 16, 4, 12, 4)
LLEG = part(16, 48, 4, 12, 4)

# Cabeza: piel, pelo arriba y atrás, barba abajo
for side, box in HEAD.items():
    fill(box, SKIN)
fill(HEAD['top'], HAIR)
fill(HEAD['back'], HAIR)
for side in ('front', 'right', 'left', 'back'):
    x0, y0, x1, y1 = HEAD[side]
    fill((x0, y0, x1, y0 + 2), HAIR)               # pelo
    fill((x0, y0 + 5, x1, y1), BEARD)              # barba
fill(HEAD['bottom'], BEARD)
fx, fy = HEAD['front'][0], HEAD['front'][1]
for x in (1, 2, 5, 6):
    put(fx + x, fy + 2, HAIR, 2)                     # cejas
put(fx + 1, fy + 3, (235, 230, 220), 2); put(fx + 2, fy + 3, (40, 34, 30), 2)   # ojos
put(fx + 5, fy + 3, (40, 34, 30), 2); put(fx + 6, fy + 3, (235, 230, 220), 2)
put(fx + 3, fy + 4, (160, 112, 84), 3); put(fx + 4, fy + 4, (160, 112, 84), 3)  # nariz
put(fx + 3, fy + 6, (90, 54, 44), 2); put(fx + 4, fy + 6, (90, 54, 44), 2)      # boca, entre la barba
for _ in range(5):                                  # hollín en la cara
    put(fx + rnd.randrange(8), fy + rnd.randrange(2, 5), SOOT, 4)

# Torso: camisa, delantal adelante con tiras, cinturón
for box in BODY.values():
    fill(box, SHIRT)
x0, y0, x1, y1 = BODY['front']
fill((x0 + 1, y0 + 2, x1 - 1, y1), APRON)
fill((x0 + 1, y0, x0 + 2, y0 + 2), STRAP)
fill((x1 - 2, y0, x1 - 1, y0 + 2), STRAP)
fill((x0, y0 + 7, x1, y0 + 8), BELT)
put(x0 + 3, y0 + 7, BUCKLE, 3); put(x0 + 4, y0 + 7, BUCKLE, 3)
for _ in range(10):                                 # quemaduras y manchas del delantal
    put(x0 + 1 + rnd.randrange(6), y0 + 2 + rnd.randrange(10), (82, 50, 28), 4)
bx0, by0, bx1, by1 = BODY['back']
fill((bx0 + 1, by0, bx0 + 2, by1 - 5), STRAP)        # tiras cruzadas atrás
fill((bx1 - 2, by0, bx1 - 1, by1 - 5), STRAP)
fill((bx0, by0 + 7, bx1, by0 + 8), BELT)
for side in ('right', 'left'):
    sx0, sy0, sx1, sy1 = BODY[side]
    fill((sx0, sy0 + 7, sx1, sy0 + 8), BELT)

# Brazos: manga hasta el codo, antebrazo con hollín
for arm in (RARM, LARM):
    for side, box in arm.items():
        fill(box, SKIN)
        if side in ('top',):
            fill(box, SHIRT)
        if side not in ('top', 'bottom'):
            x0, y0, x1, y1 = box
            fill((x0, y0, x1, y0 + 5), SHIRT)
            for _ in range(4):
                if rnd.random() < 0.5: put(x0 + rnd.randrange(x1 - x0), y0 + 6 + rnd.randrange(6), SOOT, 5)

# Piernas: pantalón, delantal adelante arriba, botas
for leg in (RLEG, LLEG):
    for side, box in leg.items():
        fill(box, PANTS)
        if side not in ('top', 'bottom'):
            x0, y0, x1, y1 = box
            fill((x0, y1 - 3, x1, y1), BOOTS)
    fill(leg['bottom'], BOOTS)
    x0, y0, x1, y1 = leg['front']
    fill((x0, y0, x1, y0 + 6), APRON)

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'herrero.png')
img.save(out)
print(out)
if len(sys.argv) > 1:
    img.resize((64 * 8, 64 * 8), Image.NEAREST).save(sys.argv[1])
