"""
Los estados de Ascensión (terror:estado_<nombre>), en lugar de los vidrios, con los símbolos de cualquier interfaz:
- activa / apagada: un interruptor encendido (verde, perilla a la derecha) o apagado (gris, perilla a la izquierda)
- disponible: un círculo dorado con "+" (la puedes comprar)
- bloqueada: un candado
- alcanzada / siguiente (etapas): un círculo verde con ✓, un círculo dorado con una flecha para arriba
Una textura de 16x16 para cada uno, con su modelo y su ítem.
Uso: python fuentes/estados.py [vista.png]
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHITE = (250, 250, 250, 255)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (255,)


def toggle(on):
    """Un interruptor: la pista redondeada y la perilla."""
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    track = (64, 186, 96, 255) if on else (86, 86, 94, 255)
    rows = {4: (3, 12), 5: (2, 13), 6: (1, 14), 7: (1, 14), 8: (1, 14), 9: (1, 14), 10: (2, 13), 11: (3, 12)}
    for y, (a, b) in rows.items():
        for x in range(a, b + 1):
            edge = y in (4, 11) or x in (a, b)
            img.putpixel((x, y), shade(track, 0.7) if edge else track)
    # Perilla: un círculo de 6 a un costado
    cx = 9 if on else 3
    knob = {5: (1, 4), 6: (0, 5), 7: (0, 5), 8: (0, 5), 9: (0, 5), 10: (1, 4)}
    face = WHITE if on else (196, 196, 202, 255)
    for y, (a, b) in knob.items():
        for x in range(cx + a, cx + b + 1):
            bottom = y == 10 or (y == 9 and x in (cx, cx + 5))
            img.putpixel((x, y), shade(face, 0.78) if bottom else face)
    return img


def badge(color, glyph):
    """Un círculo de color con un símbolo blanco adentro."""
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5
            if d <= 7.3:
                img.putpixel((x, y), shade(color, 0.68) if d > 6.2 else (shade(color, 1.12) if y < 6 else color))
    for (x, y) in glyph:
        img.putpixel((x, y), WHITE)
    return img


PLUS = [(x, y) for x in (7, 8) for y in range(4, 12)] + [(x, y) for y in (7, 8) for x in range(4, 12)]
CHECK = []
for (x, y) in [(4, 8), (5, 9), (6, 10), (7, 9), (8, 8), (9, 7), (10, 6), (11, 5)]:
    CHECK += [(x, y), (x, y - 1)]
ARROW = [(x, y) for x in (7, 8) for y in range(7, 12)]
for i, y in enumerate(range(4, 8)):
    ARROW += [(x, y) for x in range(7 - i, 9 + i)]


def padlock():
    art = [
        '................',
        '................',
        '.....ssssss.....',
        '....sS....Ss....',
        '....s......s....',
        '....s......s....',
        '....s......s....',
        '...BBBBBBBBBB...',
        '...BHHHHHHHHD...',
        '...BHHHrrHHHD...',
        '...BHHHrrHHHD...',
        '...BHHHHrHHHD...',
        '...BHHHHrHHHD...',
        '...BHHHHHHHHD...',
        '...DDDDDDDDDD...',
        '................',
    ]
    colors = {'s': (112, 110, 118, 255), 'S': (160, 158, 166, 255), 'B': (120, 118, 126, 255),
              'H': (84, 82, 90, 255), 'D': (46, 45, 50, 255), 'r': (120, 18, 28, 255)}
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            if ch in colors:
                img.putpixel((x, y), colors[ch])
    return img


GREEN, GOLD = (64, 186, 96, 255), (226, 164, 40, 255)
ESTADOS = {
    'activa': toggle(True),
    'apagada': toggle(False),
    'disponible': badge(GOLD, PLUS),
    'bloqueada': padlock(),
    'alcanzada': badge(GREEN, CHECK),
    'siguiente': badge(GOLD, ARROW),
}

view = Image.new('RGBA', (16 * len(ESTADOS) + len(ESTADOS) - 1, 16), (60, 60, 60, 255))
for i, (name, img) in enumerate(ESTADOS.items()):
    key = 'estado_' + name
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
