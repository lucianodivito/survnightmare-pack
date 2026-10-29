"""La armadura del Condenado, diseñada de cero (no parte de ninguna del juego): forma propia en el cuerpo y en los íconos.
- Casco cerrado: rendija para los ojos y una reja de barrotes sobre la boca (entre barrote y barrote se ve la cara).
- Peto: collar de hierro grueso, placas horizontales separadas (lamas) con una correa de cuero al medio, hombreras;
  el brazo queda descubierto y en la muñeca, un grillete.
- Grebas: cinturón con hebilla, placas en los muslos y rodilleras remachadas, con huecos entre medio.
- Botas: de hierro, con un grillete arriba.
Salida: textures/entity/equipment/{humanoid,humanoid_leggings}/condenado.png y los íconos textures/item/*_condenado.png
Uso: python fuentes/condenado_armadura.py [carpeta para vistas]
"""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, 'assets', 'terror', 'textures')

C = {'K': (26, 28, 36, 255), 'D': (52, 57, 70, 255), 'M': (90, 97, 114, 255), 'L': (138, 147, 166, 255),
     'W': (200, 208, 226, 255), 'R': (222, 228, 240, 255), 'H': (56, 42, 34, 255), 'h': (88, 68, 54, 255),
     'B': (34, 38, 48, 255), 'b': (82, 88, 104, 255)}


# ------------------------------------------------------------------ en el cuerpo
def part(x, y, w, h, d):
    """Las caras de una parte del modelo en la plantilla (como una skin)."""
    return {'top': (x + d, y, w, d), 'bottom': (x + d + w, y, w, d), 'right': (x, y + d, d, h),
            'front': (x + d, y + d, w, h), 'left': (x + d + w, y + d, d, h), 'back': (x + 2 * d + w, y + d, w, h)}


def plate(img, box, rows=None, light_top=True):
    """Una placa: acero con el borde de arriba claro, el de abajo oscuro y los costados apenas más oscuros.
    {rows}: qué filas de la cara cubre (None = todas)."""
    x0, y0, w, h = box
    for j in range(h):
        if rows is not None and j not in rows:
            continue
        top = rows is None and j == 0 or rows is not None and j - 1 not in rows
        bottom = rows is None and j == h - 1 or rows is not None and j + 1 not in rows
        for i in range(w):
            if top and light_top:
                c = 'W' if i < w - 1 else 'L'
            elif bottom:
                c = 'D'
            elif i == 0:
                c = 'L'
            elif i == w - 1:
                c = 'D'
            else:
                c = 'M'
            img.putpixel((x0 + i, y0 + j), C[c])


def dot(img, box, i, j, c):
    x0, y0, w, h = box
    if 0 <= i < w and 0 <= j < h:
        img.putpixel((x0 + i, y0 + j), C[c])


def clear(img, box, i, j):
    x0, y0, w, h = box
    img.putpixel((x0 + i, y0 + j), (0, 0, 0, 0))


def shackle(img, box, j):
    """Un grillete: banda oscura de dos filas, con remaches."""
    x0, y0, w, h = box
    for i in range(w):
        img.putpixel((x0 + i, y0 + j), C['b'])
        img.putpixel((x0 + i, y0 + j + 1), C['R'] if i % 3 == 1 else C['B'])


def upper():
    img = Image.new('RGBA', (64, 32), (0, 0, 0, 0))
    head = part(0, 0, 8, 8, 8)
    # Casco: todo cerrado, salvo abajo (el cuello)
    for face in ('top', 'right', 'left', 'back'):
        plate(img, head[face])
    for face in ('right', 'left'):
        dot(img, head[face], 3, 2, 'R')
        dot(img, head[face], 3, 5, 'R')
    front = head['front']
    plate(img, front)
    dot(img, front, 1, 2, 'R')
    dot(img, front, 6, 2, 'R')
    for i in range(1, 7):                         # rendija para los ojos
        clear(img, front, i, 3)
    for j in (4, 5, 6):                           # reja de barrotes sobre la boca
        for i in range(1, 7):
            if i % 2 == 0:
                clear(img, front, i, j)
            else:
                dot(img, front, i, j, 'D' if j < 6 else 'K')
    # Peto: collar, lamas separadas y una correa de cuero al medio
    body = part(16, 16, 8, 12, 4)
    plate(img, body['top'])
    lamas = [0, 1, 3, 4, 6, 7]                    # filas con placa (el resto, huecos)
    for face in ('front', 'back', 'right', 'left'):
        plate(img, body[face], rows=set(lamas))
    for face in ('front', 'back'):
        x0, y0, w, h = body[face]
        for i in range(w):                        # el collar: hierro grueso, claro
            img.putpixel((x0 + i, y0), C['W'] if 1 <= i <= 6 else C['L'])
            img.putpixel((x0 + i, y0 + 1), C['R'] if i in (3, 4) else C['b'])
        for j in range(2, 9):                     # la correa, que une las lamas
            img.putpixel((x0 + 3, y0 + j), C['H'])
            img.putpixel((x0 + 4, y0 + j), C['h'])
    # Brazos: hombrera arriba, el brazo descubierto, grillete en la muñeca
    arm = part(40, 16, 4, 12, 4)
    plate(img, arm['top'])
    for face in ('front', 'back', 'right', 'left'):
        plate(img, arm[face], rows={0, 1, 2})
        dot(img, arm[face], 1, 1, 'R')
        shackle(img, arm[face], 9)
    # Botas: de hierro, con un grillete arriba
    leg = part(0, 16, 4, 12, 4)
    plate(img, leg['bottom'])
    for face in ('front', 'back', 'right', 'left'):
        shackle(img, leg[face], 6)
        plate(img, leg[face], rows={8, 9, 10, 11})
    return img


def lower():
    img = Image.new('RGBA', (64, 32), (0, 0, 0, 0))
    body = part(16, 16, 8, 12, 4)
    # Cinturón (las últimas filas del torso)
    for face in ('front', 'back', 'right', 'left'):
        x0, y0, w, h = body[face]
        for i in range(w):
            img.putpixel((x0 + i, y0 + 9), C['h'])
            img.putpixel((x0 + i, y0 + 10), C['H'])
        if face == 'front':
            img.putpixel((x0 + 3, y0 + 9), C['R'])
            img.putpixel((x0 + 4, y0 + 9), C['R'])
            img.putpixel((x0 + 3, y0 + 10), C['L'])
            img.putpixel((x0 + 4, y0 + 10), C['L'])
    # Piernas: placa en el muslo y rodillera, con huecos entre medio
    leg = part(0, 16, 4, 12, 4)
    for face in ('front', 'back', 'right', 'left'):
        plate(img, leg[face], rows={0, 1, 2, 3})
        plate(img, leg[face], rows={5, 6})
        dot(img, leg[face], 1, 5, 'R')
    return img


# ------------------------------------------------------------------ los íconos (dibujados a mano)
ICONOS = {
    'yelmo_condenado': [
        '................',
        '................',
        '....KKKKKKKK....',
        '...KWWWLLLLMK...',
        '..KWLLLMMMMMDK..',
        '..KLRMMMMMMRDK..',
        '..KMKKKKKKKKDK..',
        '..KMK......KDK..',
        '..KMDKDKDKDKDK..',
        '..KMK.K.K.K.DK..',
        '..KDDKDKDKDKDK..',
        '...KKKKKKKKKK...',
        '................',
        '................',
        '................',
        '................',
    ],
    'peto_condenado': [
        '................',
        '.KKKK......KKKK.',
        'KWLLMKKKKKKMLLDK',
        'KLMMMKbbRbKMMMDK',
        'KKMMDKKKKKKDMMKK',
        '.KKKWLLHhLLMDKK.',
        '...KLMMHhMMMDK..',
        '...KKKKHhKKKKK..',
        '...KWLLHhLLLMK..',
        '...KLMMHhMMMDK..',
        '...KKKKHhKKKKK..',
        '...KWLLHhLLLMK..',
        '...KLMMHhMMMDK..',
        '...KDDDDDDDDDK..',
        '....KKKKKKKKK...',
        '................',
    ],
    'grebas_condenado': [
        '................',
        '...KKKKKKKKKKK..',
        '...KhHHHRHHHhK..',
        '...KWLLK.KWLLK..',
        '...KLMMK.KLMMK..',
        '...KMMDK.KMMDK..',
        '...KKKKK.KKKKK..',
        '...KDMDK.KDMDK..',
        '...KRWLK.KRWLK..',
        '...KLMDK.KLMDK..',
        '...KMMDK.KMMDK..',
        '...KMDDK.KMDDK..',
        '...KKKKK.KKKKK..',
        '................',
        '................',
        '................',
    ],
    'botas_condenado': [
        '................',
        '................',
        '................',
        '................',
        '................',
        '..KKKKK...KKKKK.',
        '..KbRbK...KbRbK.',
        '..KBBBK...KBBBK.',
        '..KLMDK...KLMDK.',
        '..KLMDKK..KLMDKK',
        '.KWLMMDK.KWLMMDK',
        '.KLMMMDK.KLMMMDK',
        '.KKKKKKK.KKKKKKK',
        '................',
        '................',
        '................',
    ],
}


def icon(rows):
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        assert len(row) == 16, (y, row, len(row))
        for x, ch in enumerate(row):
            if ch in C:
                img.putpixel((x, y), C[ch])
    return img


up, low = upper(), lower()
for layer, img in (('humanoid', up), ('humanoid_leggings', low)):
    path = os.path.join(A, 'entity', 'equipment', layer, 'condenado.png')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
for name, rows in ICONOS.items():
    icon(rows).save(os.path.join(A, 'item', name + '.png'))
print('armadura del Condenado')
