"""
Los bichos de los eventos:
- El Ojo (Luna de Sangre): un ojo enorme e inyectado en sangre, de frente siempre (terror:ojo_sangre, 32x32).
- El Empapado (lluvia): skin de jugador de 64x64 (terror:entity/empapado): piel pálida azulada, pelo negro largo y
  mojado que le tapa la cara (apenas se ve un ojo), camisón blanco empapado y pies descalzos.
Uso: python fuentes/eventos.py [carpeta para vistas]
"""
import json, math, os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(1408)


def clamp(c):
    return tuple(max(0, min(255, int(v))) for v in c[:3]) + (c[3] if len(c) > 3 else 255,)


# ------------------------------------------------------------------ El Ojo
S = 32
eye = Image.new('RGBA', (S, S), (0, 0, 0, 0))
px = eye.load()
cx, cy = 15.5, 15.5
for y in range(S):
    for x in range(S):
        dx, dy = (x - cx) / 15.2, (y - cy) / 10.5          # ovalado: más ancho que alto
        d = math.hypot(dx, dy)
        if d > 1:
            continue
        r = math.hypot(x - cx, y - cy)
        if d > 0.86:                                        # párpado: carne oscura e hinchada
            c = (92 + rnd.randint(-8, 8), 18, 22)
        else:                                               # el blanco, amarillento y sucio, más rojo hacia el borde
            k = (d / 0.86) ** 2
            c = (232 - 20 * k, 214 - 110 * k, 196 - 120 * k)
        if r < 7.2:                                         # iris rojo anaranjado, más oscuro hacia afuera
            t = r / 7.2
            c = (200 - 90 * t, 58 - 30 * t, 24 - 10 * t)
        if r < 3.3:                                         # pupila
            c = (12, 6, 8)
        px[x, y] = clamp(c)
# Venas: líneas rojas que salen del borde hacia el iris
for _ in range(14):
    a = rnd.uniform(0, math.pi * 2)
    x, y = cx + math.cos(a) * 14, cy + math.sin(a) * 9.5
    for step in range(rnd.randint(5, 9)):
        ix, iy = int(round(x)), int(round(y))
        if 0 <= ix < S and 0 <= iy < S and px[ix, iy][3] and math.hypot(ix - cx, iy - cy) > 7.5:
            px[ix, iy] = clamp((170, 20, 26))
        a += rnd.uniform(-0.6, 0.6)
        x -= math.cos(a) * 1.2
        y -= math.sin(a) * 0.9
px[13, 12] = (255, 255, 255, 255)                           # el brillo
px[14, 12] = (240, 230, 225, 255)
px[13, 13] = (220, 210, 205, 255)
tex = os.path.join(ROOT, 'assets', 'terror', 'textures', 'item', 'ojo_sangre.png')
eye.save(tex)
json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'terror:item/ojo_sangre'}},
          open(os.path.join(ROOT, 'assets', 'terror', 'models', 'item', 'ojo_sangre.json'), 'w'), indent=2)
json.dump({'model': {'type': 'minecraft:model', 'model': 'terror:item/ojo_sangre'}},
          open(os.path.join(ROOT, 'assets', 'terror', 'items', 'ojo_sangre.json'), 'w'), indent=2)

# ------------------------------------------------------------------ El Empapado
skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
sp = skin.load()
PALE = (176, 190, 196)
HAIR = (14, 14, 18)
GOWN = (196, 200, 198)
WET = (150, 160, 162)


def put(x, y, c, noise=5):
    n = rnd.randint(-noise, noise)
    sp[x, y] = clamp((c[0] + n, c[1] + n, c[2] + n))


def fill(box, c, noise=5):
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            put(x, y, c, noise)


def part(x, y, w, h, d):
    return {'top': (x + d, y, x + d + w, y + d), 'bottom': (x + d + w, y, x + d + 2 * w, y + d),
            'right': (x, y + d, x + d, y + d + h), 'front': (x + d, y + d, x + d + w, y + d + h),
            'left': (x + d + w, y + d, x + 2 * d + w, y + d + h), 'back': (x + 2 * d + w, y + d, x + 2 * d + 2 * w, y + d + h)}


HEAD, BODY = part(0, 0, 8, 8, 8), part(16, 16, 8, 12, 4)
ARMS = [part(40, 16, 4, 12, 4), part(32, 48, 4, 12, 4)]
LEGS = [part(0, 16, 4, 12, 4), part(16, 48, 4, 12, 4)]
# Cabeza: todo pelo, salvo una rendija en la cara con un ojo
for box in HEAD.values():
    fill(box, HAIR, 4)
fx, fy = HEAD['front'][0], HEAD['front'][1]
for y in range(2, 7):
    put(fx + 5, fy + y, PALE, 6)
put(fx + 5, fy + 3, (8, 8, 10), 2)                         # el ojo, negro
put(fx + 5, fy + 5, (120, 120, 130), 3)
# Pelo que cae sobre los hombros y la espalda (capa exterior del cuerpo: 16..40, 32..48)
JACKET = part(16, 32, 8, 12, 4)
for side in ('front', 'back', 'right', 'left'):
    x0, y0, x1, y1 = JACKET[side]
    for x in range(x0, x1):
        length = rnd.randint(2, 6) if side == 'front' else rnd.randint(5, 10)
        if side == 'front' and x0 + 2 <= x < x1 - 2:
            continue
        for y in range(y0, y0 + length):
            put(x, y, HAIR, 4)
# Camisón empapado (más oscuro donde está mojado) y gotas
for box in list(BODY.values()) + [b for leg in LEGS for b in leg.values()]:
    fill(box, GOWN, 6)
    for _ in range(4):
        x, y = rnd.randrange(box[0], box[2]), rnd.randrange(box[1], box[3])
        for i in range(rnd.randint(1, 4)):
            if y + i < box[3]:
                put(x, y + i, WET, 4)
for leg in LEGS:                                            # pies descalzos
    for side in ('front', 'back', 'right', 'left'):
        x0, y0, x1, y1 = leg[side]
        fill((x0, y1 - 2, x1, y1), PALE, 6)
    fill(leg['bottom'], PALE, 6)
for arm in ARMS:                                            # brazos flacos y pálidos, manga corta
    for side, box in arm.items():
        fill(box, PALE, 7)
        if side not in ('top', 'bottom'):
            fill((box[0], box[1], box[2], box[1] + 3), GOWN, 6)
    fill(arm['top'], GOWN, 6)
skin.save(os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'empapado.png'))
print('ojo_sangre, empapado')
if len(sys.argv) > 1:
    eye.resize((S * 12, S * 12), Image.NEAREST).save(os.path.join(sys.argv[1], 'ojo.png'))
    skin.resize((64 * 8, 64 * 8), Image.NEAREST).save(os.path.join(sys.argv[1], 'empapado.png'))
