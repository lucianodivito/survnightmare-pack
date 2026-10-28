"""
Genera la letra de sangre (terror:sangre): las letras del juego (ascii.png de vanilla) agrandadas al doble, con bordes
manchados, chorreones hacia abajo y color de sangre. Solo mayúsculas (el plugin pasa el texto a mayúsculas).
Salida: assets/terror/textures/font/sangre.png y assets/terror/font/sangre.json.
Uso: python fuentes/sangre.py <ascii.png de vanilla> [vista.png]
"""
import json, os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASCII = Image.open(sys.argv[1]).convert('RGBA')

# Celda: 16 de ancho x 28 de alto. Filas 0-3: lugar para tildes; 4-19: la letra (8x8 al doble); 20-27: chorreones.
W, H, TOP = 16, 28, 4
ROWS = [
    'ABCDEFGHIJKLMNOP',
    'QRSTUVWXYZÑÁÉÍÓÚ',
    '0123456789.,!?¡¿',
    "-'\":;()+/<>_#*%&",
]
ROWS = [r[:16].ljust(16, '\0') for r in ROWS]
ACCENTED = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ñ': 'N'}
FLIPPED = {'¡': '!', '¿': '?'}


def base_mask(ch):
    """La letra de vanilla como lista de (x, y) en su celda de 8x8, y su ancho."""
    code = ord(ch)
    cx, cy = (code % 16) * 8, (code // 16) * 8
    pts = [(x, y) for y in range(8) for x in range(8) if ASCII.getpixel((cx + x, cy + y))[3] > 0]
    width = max((x for x, _ in pts), default=-1) + 1
    return pts, width


def glyph(ch):
    rnd = random.Random(ord(ch) * 7919)
    src = ACCENTED.get(ch, FLIPPED.get(ch, ch))
    pts, width = base_mask(src)
    if ch in FLIPPED:   # ¡ ¿: el ! y el ? dados vuelta dentro de la altura de una mayúscula (filas 0-6)
        pts = [(width - 1 - x, 6 - y) for x, y in pts]
    on = set()
    for x, y in pts:
        for dx in (0, 1):
            for dy in (0, 1):
                on.add((x * 2 + dx, TOP + y * 2 + dy))
    if ch in ACCENTED:
        mid = width   # centro de la letra, al doble
        if ch == 'Ñ':
            on |= {(mid - 4, 2), (mid - 3, 1), (mid - 2, 1), (mid - 1, 2), (mid, 2), (mid + 1, 1), (mid - 4, 3), (mid, 3)}
        else:
            on |= {(mid, 0), (mid + 1, 0), (mid - 1, 1), (mid, 1), (mid - 2, 2), (mid - 1, 2)}
    # Bordes manchados: algo de sangre de más pegada al trazo, y algún hueco
    for (x, y) in list(on):
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in on and 0 <= nx < W and 0 <= ny < TOP + 16 and rnd.random() < 0.035:
                on.add((nx, ny))
    # Chorreones: desde el borde de abajo de los trazos
    drips = []
    for (x, y) in sorted(on):
        if (x, y + 1) in on or y < TOP + 6:
            continue
        if rnd.random() < 0.13:
            length = rnd.choice([3, 4, 6, 7, 8, 9, 10])
            drips.append((x, y, length))
    pixels = {}
    for (x, y) in on:
        pixels[(x, y)] = 'cuerpo'
    for x, y, length in drips:
        end = min(H - 1, y + length)
        for yy in range(y + 1, end + 1):
            pixels[(x, yy)] = 'gota'
        if rnd.random() < 0.5 and end + 1 < H:   # la gota de la punta
            pixels[(x, end + 1)] = 'punta'
            if x + 1 < W and rnd.random() < 0.5:
                pixels[(x + 1, end)] = 'punta'
    return pixels


def color(kind, x, y, pixels, rnd):
    if kind == 'cuerpo':
        r = rnd.randint(140, 158)
        c = (r, rnd.randint(8, 13), rnd.randint(10, 15))
    elif kind == 'gota':
        r = rnd.randint(118, 135)
        c = (r, rnd.randint(6, 10), rnd.randint(8, 12))
    else:
        c = (rnd.randint(92, 105), 5, 8)
    # Abajo y a la derecha del trazo, más oscuro (sangre que se junta y se seca); algún brillo arriba
    if kind == 'cuerpo' and ((x + 1, y) not in pixels or (x, y + 1) not in pixels) and rnd.random() < 0.6:
        c = tuple(int(v * 0.78) for v in c[:3])
    elif kind == 'cuerpo' and (x, y - 1) not in pixels and rnd.random() < 0.15:
        c = (178, 26, 28)
    return c + (255,)


sheet = Image.new('RGBA', (W * 16, H * len(ROWS)), (0, 0, 0, 0))
for row, chars in enumerate(ROWS):
    for col, ch in enumerate(chars):
        if ch == '\0':
            continue
        pixels = glyph(ch)
        rnd = random.Random(ord(ch) * 104729)
        for (x, y), kind in pixels.items():
            if 0 <= x < W and 0 <= y < H:
                sheet.putpixel((col * W + x, row * H + y), color(kind, x, y, pixels, rnd))

tex = os.path.join(ROOT, 'assets', 'terror', 'textures', 'font', 'sangre.png')
os.makedirs(os.path.dirname(tex), exist_ok=True)
sheet.save(tex)
font = {'providers': [
    {'type': 'space', 'advances': {' ': 5}},
    {'type': 'bitmap', 'file': 'terror:font/sangre.png', 'height': H // 2, 'ascent': 9, 'chars': ROWS},
]}
js = os.path.join(ROOT, 'assets', 'terror', 'font', 'sangre.json')
with open(js, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(font, f, indent=2)
print(tex)
print(js)

if len(sys.argv) > 2:   # vista previa: el abecedario grande sobre piedra oscura
    scale = 4
    view = Image.new('RGBA', (sheet.width * scale, sheet.height * scale), (52, 52, 56, 255))
    view.alpha_composite(sheet.resize((sheet.width * scale, sheet.height * scale), Image.NEAREST))
    view.save(sys.argv[2])
    print(sys.argv[2])
