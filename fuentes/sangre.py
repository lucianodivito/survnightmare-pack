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

# Celda: 16 de ancho x 32 de alto. Filas 0-3: lugar para tildes; 4-19: la letra (8x8 al doble); 20-31: chorreones.
W, H, TOP = 16, 32, 4
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
        for dx in (0, 1, 2):   # trazo grueso, como pintado con el dedo
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
        if rnd.random() < 0.2 and not any(abs(x - d[0]) < 2 for d in drips):
            length = rnd.choice([4, 6, 8, 9, 10, 12, 14])
            drips.append((x, y, length))
    pixels = {}
    for (x, y) in on:
        pixels[(x, y)] = 'cuerpo'
    for x, y, length in drips:
        end = min(H - 1, y + length)
        wide = rnd.random() < 0.35 and x + 1 < W
        for yy in range(y + 1, end + 1):
            pixels[(x, yy)] = 'gota'
            if wide and yy < end - 1:
                pixels[(x + 1, yy)] = 'gota'
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

# ---------------------------------------------------------------- manchas para carteles
# Una "letra" del tamaño del cartel (88 x 46, a doble resolución), con salpicaduras, chorreones desde arriba, una
# pasada de mano y a veces una huella. El plugin la pone en un renglón vacío; hay una versión por renglón (cambia
# la altura) para que siempre caiga sobre el cartel entero. Caracteres:  + variante * 4 + renglón.
from PIL import ImageDraw

SW, SH = 176, 92
STAINS = 4


def dried(rnd, alpha):
    return (rnd.randint(88, 118), rnd.randint(5, 10), rnd.randint(7, 12), alpha)


def blob(draw, rnd, cx, cy, size, alpha):
    for _ in range(rnd.randint(5, 9)):
        r = rnd.uniform(size * 0.35, size * 0.7)
        x, y = cx + rnd.uniform(-size * 0.6, size * 0.6), cy + rnd.uniform(-size * 0.45, size * 0.45)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=dried(rnd, alpha))
    # Salpicado alrededor, hacia un lado
    angle = rnd.uniform(0, 6.283)
    import math
    for i in range(rnd.randint(8, 16)):
        a = angle + rnd.uniform(-0.7, 0.7)
        d = size * rnd.uniform(0.9, 2.6)
        r = max(0.6, rnd.uniform(0.6, 2.4) * (1.6 - d / (size * 2.6)))
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        draw.ellipse([x - r, y - r, x + r, y + r], fill=dried(rnd, alpha))


def drip(draw, rnd, x, y0, length, alpha):
    w = rnd.choice([1, 2, 2, 3])
    draw.rectangle([x, y0, x + w - 1, y0 + length], fill=dried(rnd, alpha))
    draw.ellipse([x - 1, y0 + length - 1, x + w, y0 + length + 2], fill=dried(rnd, alpha))


def hand(draw, rnd, cx, cy, alpha):
    c = dried(rnd, alpha)
    draw.rounded_rectangle([cx - 10, cy - 5, cx + 9, cy + 12], 6, fill=c)   # palma
    for dx, h in ((-9, 11), (-4, 15), (1, 16), (6, 13)):                    # dedos, separados
        draw.rounded_rectangle([cx + dx - 1, cy - 5 - h, cx + dx + 2, cy - 3], 1, fill=c)
    for i in range(7):                                                      # pulgar, en diagonal
        draw.ellipse([cx + 9 + i * 1.3 - 2, cy + 2 - i * 1.1 - 2, cx + 9 + i * 1.3 + 2, cy + 2 - i * 1.1 + 2], fill=c)
    for _ in range(3):
        drip(draw, rnd, cx + rnd.randint(-7, 6), cy + 10, rnd.randint(6, 18), alpha)


def smear(img, rnd, alpha):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = rnd.randint(10, SH - 25)
    x0 = rnd.randint(0, 40)
    length = rnd.randint(70, 140)
    slope = rnd.uniform(-0.2, 0.2)
    for i in range(length):
        for k in range(rnd.randint(9, 13)):   # cerdas: rayitas paralelas
            if rnd.random() < 0.8:
                yy = y + i * slope + k
                a = int(alpha * (1 - i / length) * rnd.uniform(0.6, 1))
                d.point((x0 + i, yy), fill=dried(rnd, max(0, a)))
    img.alpha_composite(layer)


def stain(variant):
    rnd = random.Random(9000 + variant * 31)
    img = Image.new('RGBA', (SW, SH), (0, 0, 0, 0))
    smear(img, rnd, 175)
    layer = Image.new('RGBA', (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    corners = [(rnd.randint(8, 34), rnd.randint(8, 26)), (rnd.randint(142, 168), rnd.randint(8, 26)),
               (rnd.randint(8, 34), rnd.randint(64, 84)), (rnd.randint(142, 168), rnd.randint(64, 84))]
    rnd.shuffle(corners)
    for cx, cy in corners[:rnd.randint(2, 3)]:
        blob(d, rnd, cx, cy, rnd.uniform(5, 11), rnd.randint(195, 225))
    for _ in range(rnd.randint(3, 6) + (6 if variant == 3 else 0)):   # sangre que cae desde arriba
        drip(d, rnd, rnd.randint(4, SW - 6), 0, rnd.randint(8, 46), rnd.randint(190, 220))
    if variant in (1, 2):
        hand(d, rnd, rnd.choice([rnd.randint(22, 40), rnd.randint(136, 154)]), rnd.randint(40, 60), 185)
    img.alpha_composite(layer)
    return img


providers = []
for v in range(STAINS):
    name = 'sangre_mancha%d.png' % v
    stain(v).save(os.path.join(ROOT, 'assets', 'terror', 'textures', 'font', name))
    for line in range(4):
        providers.append({'type': 'bitmap', 'file': 'terror:font/' + name, 'height': SH // 2,
                          'ascent': 11 + 10 * line, 'chars': [chr(0xE100 + v * 4 + line)]})

font = {'providers': [
    {'type': 'space', 'advances': {' ': 5}},
    {'type': 'bitmap', 'file': 'terror:font/sangre.png', 'height': H // 2, 'ascent': 9, 'chars': ROWS},
] + providers}
js = os.path.join(ROOT, 'assets', 'terror', 'font', 'sangre.json')
with open(js, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(font, f, indent=2)
# La misma letra al doble (terror:sangre_grande), para el nombre del server arriba del tab
big = {'providers': [
    {'type': 'space', 'advances': {' ': 10}},
    {'type': 'bitmap', 'file': 'terror:font/sangre.png', 'height': H, 'ascent': 18, 'chars': ROWS},
]}
js_big = os.path.join(ROOT, 'assets', 'terror', 'font', 'sangre_grande.json')
with open(js_big, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(big, f, indent=2)
print(tex)
print(js)
print(js_big)

if len(sys.argv) > 2:   # vista previa: el abecedario grande sobre piedra oscura
    scale = 4
    view = Image.new('RGBA', (sheet.width * scale, sheet.height * scale), (52, 52, 56, 255))
    view.alpha_composite(sheet.resize((sheet.width * scale, sheet.height * scale), Image.NEAREST))
    # Y cómo quedaría un cartel: madera, una mancha y "NO ENTRES"
    for v in range(STAINS):
        board = Image.new('RGBA', (SW + 16, SH + 16), (150, 118, 72, 255))
        board.alpha_composite(stain(v), (8, 8))
        x = 40
        for ch in 'NO':
            i = next(r for r, row in enumerate(ROWS) if ch in row); j = ROWS[i].index(ch)
            board.alpha_composite(sheet.crop((j * W, i * H, j * W + W, i * H + H)), (x + 30, 20)); x += 13
        x = 40
        for ch in 'ENTRES':
            i = next(r for r, row in enumerate(ROWS) if ch in row); j = ROWS[i].index(ch)
            board.alpha_composite(sheet.crop((j * W, i * H, j * W + W, i * H + H)), (x + 5, 40)); x += 13
        board = board.resize((board.width * 3, board.height * 3), Image.NEAREST)
        canvas = Image.new('RGBA', (view.width, view.height + (board.height + 10) * 2), (52, 52, 56, 255)) if v == 0 else canvas
        if v == 0:
            canvas.alpha_composite(view)
        canvas.alpha_composite(board, ((v % 2) * (board.width + 10), view.height + 10 + (v // 2) * (board.height + 10)))
        if v == 1:
            pass
    view = canvas
    view.save(sys.argv[2])
    print(sys.argv[2])
