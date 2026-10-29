"""
Las cajas físicas (terror:caja_<nombre>): un cofre en 3D un poco más grande que un cofre común, para taparlo (el plugin
lo pone encima del bloque de CrazyCrates con un ItemDisplay). Oxidada (madera vieja con flejes oxidados y verdín), de
Sangre (madera roja oscura, hierro negro, sangre que chorrea de la tapa) y de Grieta (obsidiana con grietas que brillan).
Cada una: una textura de 32x32 (lado, tapa, frente, cerradura), su modelo y su ítem.
Uso: python fuentes/cajas.py [vista.png]
"""
import json, os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def clamp(c):
    return tuple(max(0, min(255, int(v))) for v in c) + (255,)


def shade(c, k):
    return clamp([v * k for v in c[:3]])


def texture(name, base, band, seam, lock, extra):
    rnd = random.Random(name)
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    px = img.load()

    def plank(x0, y0, w, h, horizontal=True):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                k = 1 + rnd.uniform(-0.06, 0.06)
                line = (y - y0) % 4 == 3 if horizontal else (x - x0) % 4 == 3
                if line:
                    k *= 0.78
                px[x, y] = shade(base, k)

    # Lado (0,0)-(16,16): tapa arriba (filas 0-4), junta (5), cuerpo (6-15); flejes verticales
    plank(0, 0, 16, 16)
    for x in range(16):
        px[x, 5] = shade(seam, 1)
        px[x, 0] = shade(base, 1.18)
    for bx in (2, 13):
        for y in range(16):
            px[bx, y] = shade(band, 1.05 + rnd.uniform(-0.05, 0.05))
            px[bx + 1 if bx == 2 else bx - 1, y] = shade(band, 0.8)
    # Tapa (16,0)-(32,16): tablas y los mismos flejes cruzando
    plank(16, 0, 16, 16, horizontal=False)
    for bx in (2, 13):
        for y in range(16):
            px[16 + bx, y] = shade(band, 1.1)
            px[16 + (bx + 1 if bx == 2 else bx - 1), y] = shade(band, 0.85)
    for x in range(16):
        px[16 + x, 0] = shade(base, 0.7)
        px[16 + x, 15] = shade(base, 0.7)
    # Frente (0,16)-(16,32): como el lado, con la chapa de la cerradura
    for y in range(16):
        for x in range(16):
            px[x, 16 + y] = px[x, y]
    for y in range(3, 9):
        for x in range(6, 10):
            px[x, 16 + y] = shade(band, 0.95 if (x in (6, 9) or y in (3, 8)) else 1.15)
    # Cerradura (16,16)-(20,20)
    for y in range(4):
        for x in range(4):
            px[16 + x, 16 + y] = shade(lock, 1.2 if (x, y) in ((1, 1), (2, 1)) else (0.75 if y == 3 or x == 3 else 1))
    # Abajo (20,16)-(32,28): oscuro
    for y in range(16, 28):
        for x in range(20, 32):
            px[x, y] = shade(base, 0.45)
    extra(px, rnd)
    return img


def rusty(px, rnd):
    # Óxido y verdín sobre los flejes y la chapa
    for _ in range(40):
        x, y = rnd.randrange(32), rnd.randrange(16)
        if rnd.random() < 0.5:
            px[x, y] = clamp((70, 140, 120)) if rnd.random() < 0.5 else clamp((150, 80, 40))
    for _ in range(12):
        x, y = rnd.randrange(16), 16 + rnd.randrange(16)
        px[x, y] = clamp((70, 140, 120))


def bloody(px, rnd):
    # Sangre que chorrea desde la junta de la tapa, en el lado y el frente
    for oy in (0, 16):
        for x in range(16):
            if rnd.random() < 0.35:
                n = rnd.choice((1, 2, 2, 3, 4, 6))
                for i in range(n):
                    if 6 + i < 16:
                        px[x, oy + 6 + i] = clamp((150, 12, 24)) if i < n - 1 else clamp((95, 6, 16))
    for _ in range(14):   # manchas en la tapa
        x, y = 16 + rnd.randrange(16), rnd.randrange(16)
        px[x, y] = clamp((130, 10, 20))


def cracked(px, rnd):
    # Grietas que brillan (violeta y alma) en lado, tapa y frente
    for ox, oy in ((0, 0), (16, 0), (0, 16)):
        for _ in range(3):
            x, y = rnd.randrange(3, 13), rnd.randrange(16)
            for _ in range(rnd.randrange(4, 9)):
                if 0 <= x < 16 and 0 <= y < 16:
                    px[ox + x, oy + y] = clamp((150, 110, 240)) if rnd.random() < 0.7 else clamp((110, 230, 240))
                x += rnd.choice((-1, 0, 1))
                y += rnd.choice((-1, 1))


CAJAS = {
    'oxidada': texture('oxidada', (96, 74, 58), (118, 86, 60), (40, 32, 28), (130, 96, 64), rusty),
    'sangre': texture('sangre', (78, 26, 28), (42, 38, 40), (24, 10, 12), (190, 30, 40), bloody),
    'grieta': texture('grieta', (30, 22, 44), (62, 52, 92), (12, 8, 20), (110, 230, 240), cracked),
}

# El modelo: cuerpo, tapa (un poco más ancha) y cerradura. UV en unidades de 0 a 16 sobre la textura de 32.
SIDE_BODY, SIDE_LID = [0, 3, 8, 8], [0, 0, 8, 2.5]
FRONT_BODY, FRONT_LID = [0, 11, 8, 16], [0, 8, 8, 10.5]


def faces(lid):
    side = SIDE_LID if lid else SIDE_BODY
    front = FRONT_LID if lid else FRONT_BODY
    return {
        'north': {'uv': side, 'texture': '#t'},
        'east': {'uv': side, 'texture': '#t'},
        'west': {'uv': side, 'texture': '#t'},
        'south': {'uv': front, 'texture': '#t'},
        'up': {'uv': [8, 0, 16, 8], 'texture': '#t'},
        'down': {'uv': [10, 8, 16, 14], 'texture': '#t'},
    }


def model(name):
    return {
        'textures': {'t': 'terror:item/caja_' + name, 'particle': 'terror:item/caja_' + name},
        'elements': [
            {'from': [0.6, 0, 0.6], 'to': [15.4, 10, 15.4], 'faces': faces(False)},
            {'from': [0.3, 10, 0.3], 'to': [15.7, 15.2, 15.7], 'faces': faces(True)},
            {'from': [7, 7.5, 15.7], 'to': [9, 11, 16.4], 'faces': {
                f: {'uv': [8, 8, 10, 10], 'texture': '#t'} for f in ('north', 'east', 'south', 'west', 'up', 'down')}},
        ],
        'display': {'fixed': {'scale': [1, 1, 1]}, 'gui': {'rotation': [30, 225, 0], 'scale': [0.625, 0.625, 0.625]}},
    }


view = Image.new('RGBA', (32 * len(CAJAS) + len(CAJAS) - 1, 32), (60, 60, 60, 255))
for i, (name, img) in enumerate(CAJAS.items()):
    key = 'caja_' + name
    img.save(os.path.join(ROOT, 'assets', 'terror', 'textures', 'item', key + '.png'))
    json.dump(model(name), open(os.path.join(ROOT, 'assets', 'terror', 'models', 'item', key + '.json'), 'w'), indent=2)
    json.dump({'model': {'type': 'minecraft:model', 'model': 'terror:item/' + key}},
              open(os.path.join(ROOT, 'assets', 'terror', 'items', key + '.json'), 'w'), indent=2)
    view.alpha_composite(img, (i * 33, 0))
    print(key)
if len(sys.argv) > 1:
    view.resize((view.width * 10, view.height * 10), Image.NEAREST).save(sys.argv[1])
