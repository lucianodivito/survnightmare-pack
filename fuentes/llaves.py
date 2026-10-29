"""
Las llaves de las cajas (terror:llave_<nombre>): una llave en diagonal, con el ojo arriba a la izquierda y los dientes
abajo. Oxidada (hierro con óxido), de sangre (roja, chorreando) y de grieta (negra con una piedra de alma en el ojo).
Una textura de 16x16 para cada una, con su modelo y su ítem. CrazyCrates las usa con Model: terror / llave_<nombre>.
Uso: python fuentes/llaves.py [vista.png]
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def key_shape():
    """Píxeles de la llave: el ojo (un aro), la caña en diagonal (2 de grueso) y dos dientes."""
    pts = {}
    for y in range(8):
        for x in range(8):
            d = ((x - 3.5) ** 2 + (y - 3.5) ** 2) ** 0.5
            if 1.6 <= d <= 3.4:
                pts[(x, y)] = 'L' if x + y < 7 else 'D'
    for t in range(6, 15):
        pts[(t, t)] = 'L'
        if t + 1 < 16:
            pts[(t + 1, t)] = 'M'
        pts[(t, t + 1) if t + 1 < 16 else (t, t)] = 'D'
    for t, n in ((10, 2), (12, 3)):   # dientes, hacia abajo a la izquierda
        for i in range(1, n + 1):
            pts[(t - i, t + i)] = 'D' if i == n else 'M'
    return {p: c for p, c in pts.items() if 0 <= p[0] < 16 and 0 <= p[1] < 16}


def draw(colors, extra=None):
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for (x, y), c in key_shape().items():
        img.putpixel((x, y), colors[c])
    if extra:
        extra(img)
    return img


def rust(img):
    # Manchas de óxido
    for p in [(2, 1), (6, 3), (8, 8), (11, 11), (9, 12), (13, 13)]:
        if img.getpixel(p)[3]:
            img.putpixel(p, (160, 82, 40, 255))


def blood(img):
    # Gotas que chorrean de la caña
    for x, y, n in [(8, 9, 3), (13, 14, 1), (5, 6, 2)]:
        for i in range(1, n + 1):
            if y + i < 16 and img.getpixel((x, y + i))[3] == 0:
                img.putpixel((x, y + i), (150, 14, 26, 255) if i < n else (96, 8, 18, 255))


def rift(img):
    # Una piedra de alma en el ojo, y un brillo en la caña
    for p, c in [((3, 3), (120, 236, 240, 255)), ((4, 3), (70, 190, 210, 255)), ((3, 4), (70, 190, 210, 255)),
                 ((4, 4), (40, 130, 160, 255)), ((9, 9), (150, 120, 220, 255))]:
        img.putpixel(p, c)


LLAVES = {
    'oxidada': draw({'L': (176, 170, 160, 255), 'M': (128, 118, 108, 255), 'D': (78, 66, 58, 255)}, rust),
    'sangre': draw({'L': (214, 64, 70, 255), 'M': (160, 26, 40, 255), 'D': (96, 10, 22, 255)}, blood),
    'grieta': draw({'L': (112, 92, 150, 255), 'M': (62, 50, 88, 255), 'D': (30, 24, 44, 255)}, rift),
}

view = Image.new('RGBA', (16 * len(LLAVES) + len(LLAVES) - 1, 16), (60, 60, 60, 255))
for i, (name, img) in enumerate(LLAVES.items()):
    key = 'llave_' + name
    tex = os.path.join(ROOT, 'assets', 'terror', 'textures', 'item', key + '.png')
    os.makedirs(os.path.dirname(tex), exist_ok=True)
    img.save(tex)
    model = os.path.join(ROOT, 'assets', 'terror', 'models', 'item', key + '.json')
    json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'terror:item/' + key}}, open(model, 'w'), indent=2)
    item = os.path.join(ROOT, 'assets', 'terror', 'items', key + '.json')
    json.dump({'model': {'type': 'minecraft:model', 'model': 'terror:item/' + key}}, open(item, 'w'), indent=2)
    view.alpha_composite(img, (i * 17, 0))
    print(key)
if len(sys.argv) > 1:
    view.resize((view.width * 12, view.height * 12), Image.NEAREST).save(sys.argv[1])
