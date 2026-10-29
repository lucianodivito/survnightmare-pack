"""
Genera los fondos de los menús de 6 filas: uno por menú, con casilleros solo donde hay botones, agrupados en paneles,
una línea de sangre bajo el título y la fila de abajo (volver, cerrar...) separada. El resto es fondo oscuro.
Salida: assets/terror/textures/gui/menu_<nombre>.png y los caracteres \\ue010... en assets/terror/font/menu.json
(el plugin elige el fondo de cada menú con ChestMenu.darkTitle).
Uso: python fuentes/menus.py [carpeta para vistas previas]
"""
import json, os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 176, 222
GX, GY = 7, 17          # esquina del primer casillero del cofre
INV_Y, HOTBAR_Y = 139, 197

FRAME_OUT = (22, 18, 20)
FRAME_LIGHT = (74, 72, 78)
BASE = (40, 38, 43)
BASE_DARK = (31, 30, 34)
SLOT_IN = (24, 23, 27)
SLOT_TOP = (14, 13, 16)
SLOT_BOTTOM = (70, 68, 75)
PANEL = (50, 48, 54)
PANEL_LIGHT = (78, 75, 82)
PANEL_SHADOW = (20, 19, 22)
BLOOD = (110, 16, 28)
BLOOD_DARK = (70, 10, 18)

# Cada menú: grupos de casilleros (cada grupo es un panel) y su color de borde. La última fila va aparte.
NAV = 'nav'
MENUS = {
    'principal': [([11, 12, 13, 14, 15, 20, 21, 22, 23, 24, 30, 31, 32], None), ([49], NAV)],
    'proteccion': [([11, 12, 13, 14, 15], None), ([29, 31, 33], (60, 120, 128)), ([45, 47, 49, 51], NAV)],
    'encargos': [([4], None), ([20], None), ([22], None), ([24], None), ([49], NAV)],
    'destilador': [([13], (60, 130, 84)), ([29, 31, 33], None), ([49], NAV)],
    'tienda': [([4], (150, 112, 40)), ([20, 21, 22, 23, 24, 31], None), ([49, 51], NAV)],
    'tienda_items': [([4], (150, 112, 40)), ([r * 9 + c for r in range(1, 5) for c in range(1, 8)], None),
                     ([45, 48, 49, 50], NAV)],
}
FIRST_CHAR = 0xE010


def slot_xy(slot):
    return GX + (slot % 9) * 18, GY + (slot // 9) * 18


def noise(img, rnd, amount=3):
    px = img.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a:
                n = rnd.randint(-amount, amount)
                px[x, y] = (max(0, r + n), max(0, g + n), max(0, b + n), a)


def rect(px, x0, y0, x1, y1, color):
    for y in range(y0, y1):
        for x in range(x0, x1):
            px[x, y] = color + (255,)


def draw_slot(px, x, y):
    """Un casillero de 18x18 hundido, como los del juego pero oscuro."""
    rect(px, x, y, x + 18, y + 18, SLOT_IN)
    for i in range(17):
        px[x + i, y] = SLOT_TOP + (255,)
        px[x, y + i] = SLOT_TOP + (255,)
        px[x + 17 - i, y + 17] = SLOT_BOTTOM + (255,)
        px[x + 17, y + 17 - i] = SLOT_BOTTOM + (255,)


def draw_panel(px, slots, border, pad=3):
    """El panel detrás de un grupo: la unión de los casilleros agrandada, con luz arriba y sombra abajo."""
    mask = set()
    for s in slots:
        x, y = slot_xy(s)
        for yy in range(y - pad, y + 18 + pad):
            for xx in range(x - pad, x + 18 + pad):
                mask.add((xx, yy))
    # Esquinas redondeadas: se sacan los píxeles con solo dos vecinos dentro
    for (x, y) in list(mask):
        if sum((x + dx, y + dy) in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) <= 2:
            mask.discard((x, y))
    light = border or PANEL_LIGHT
    for (x, y) in mask:
        top = (x, y - 1) not in mask or (x - 1, y) not in mask
        bottom = (x, y + 1) not in mask or (x + 1, y) not in mask
        if top and not bottom:
            c = light
        elif bottom and not top:
            c = PANEL_SHADOW
        elif top and bottom:
            c = tuple((a + b) // 2 for a, b in zip(light, PANEL_SHADOW))
        else:
            c = PANEL
        px[x, y] = c + (255,)
    # Contorno oscuro por fuera, para que el panel se despegue del fondo
    for (x, y) in mask:
        for dx, dy in ((1, 0), (0, 1), (1, 1)):
            q = (x + dx, y + dy)
            if q not in mask and 0 <= q[0] < W and 0 <= q[1] < H:
                px[q] = (16, 15, 18, 255)


def blood_line(px, rnd, y, x0, x1, drips=9):
    """Una raya de sangre que se apaga en las puntas, con algunas gotas que chorrean."""
    span = x1 - x0
    for x in range(x0, x1):
        t = min(x - x0, x1 - 1 - x) / (span * 0.18)
        if t < 1 and rnd.random() > t:
            continue
        px[x, y] = BLOOD + (255,)
        if rnd.random() < 0.6:
            px[x, y + 1] = BLOOD_DARK + (255,)
    for _ in range(drips):
        x = rnd.randint(x0 + span // 6, x1 - span // 6)
        length = rnd.choice((2, 2, 3, 3, 4, 5))
        for i in range(1, length + 1):
            px[x, y + i] = (BLOOD if i < length else BLOOD_DARK) + (255,)


def nav_bar(px, rnd, blood=True):
    """La fila de abajo (volver, cerrar...): una franja más oscura de lado a lado, con una raya de sangre arriba
    (si la fila de arriba está libre: si no, la raya pisaría los casilleros)."""
    y0, y1 = GY + 5 * 18, GY + 6 * 18
    rect(px, 3, y0, W - 4, y1 + 1, (27, 26, 30))
    for x in range(3, W - 4):
        px[x, y0] = SLOT_TOP + (255,)
        px[x, y1 + 1] = (52, 50, 56, 255)
    if blood:
        blood_line(px, rnd, y0 - 1, GX + 20, W - GX - 20, drips=0)


def frame(name):
    rnd = random.Random(name)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()
    # El marco del cofre: borde oscuro con esquinas redondeadas, luz adentro
    rect(px, 1, 1, W - 1, H - 1, FRAME_OUT)
    rect(px, 2, 2, W - 2, H - 2, FRAME_LIGHT)
    rect(px, 4, 4, W - 3, H - 3, BASE_DARK)
    rect(px, 3, 3, W - 4, H - 4, BASE)
    for x, y in ((1, 1), (W - 2, 1), (1, H - 2), (W - 2, H - 2)):
        px[x, y] = (0, 0, 0, 0)
    # Viñeta: más oscuro hacia los bordes del cofre
    for y in range(3, H - 4):
        for x in range(3, W - 4):
            d = min(x - 3, W - 5 - x, y - 3, H - 5 - y)
            if d < 10:
                r, g, b, a = px[x, y]
                k = 10 - d
                px[x, y] = (r - k, g - k, b - k, a)
    noise(img, rnd)
    blood_line(px, rnd, 14, GX + 1, W - GX - 1)
    for slots, border in MENUS[name]:
        if border == NAV:
            row4 = any(s // 9 == 4 for group, b in MENUS[name] if b != NAV for s in group)
            nav_bar(px, rnd, blood=not row4)
            for s in slots:
                draw_slot(px, *slot_xy(s))
        else:
            draw_panel(px, slots, border)
            for s in slots:
                draw_slot(px, *slot_xy(s))
    # El inventario del jugador, como siempre
    for r in range(3):
        for c in range(9):
            draw_slot(px, GX + c * 18, INV_Y + r * 18)
    for c in range(9):
        draw_slot(px, GX + c * 18, HOTBAR_Y)
    return img


def preview(img, name, out):
    view = img.resize((W * 3, H * 3), Image.NEAREST)
    bg = Image.new('RGBA', view.size, (60, 60, 60, 255))
    bg.alpha_composite(view)
    bg.save(os.path.join(out, 'menu_%s.png' % name))


fonts = os.path.join(ROOT, 'assets', 'terror', 'font', 'menu.json')
font = json.load(open(fonts, encoding='utf-8'))
font['providers'] = [p for p in font['providers'] if not p.get('file', '').startswith('terror:gui/menu_')]
for i, name in enumerate(MENUS):
    img = frame(name)
    img.save(os.path.join(ROOT, 'assets', 'terror', 'textures', 'gui', 'menu_%s.png' % name))
    font['providers'].append({'type': 'bitmap', 'file': 'terror:gui/menu_%s.png' % name, 'ascent': 13, 'height': H,
                              'chars': [chr(FIRST_CHAR + i)]})
    print(name, hex(FIRST_CHAR + i))
    if len(sys.argv) > 1:
        preview(img, name, sys.argv[1])
with open(fonts, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(font, f, indent=2)
