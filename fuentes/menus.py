"""
Genera los fondos de los menús de 6 filas: uno por menú, con casilleros solo donde hay botones, agrupados en paneles
con relieve (y alguna gota de sangre que chorrea de abajo). El resto es fondo oscuro.
Salida: assets/terror/textures/gui/menu_<nombre>.png y sus caracteres en assets/terror/font/menu.json
(el plugin elige el fondo de cada menú con ChestMenu.darkTitle). Si se mueve un botón en el plugin, hay que moverlo acá.
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
OUTLINE = (16, 15, 18)
BLOOD = (110, 16, 28)
BLOOD_DARK = (70, 10, 18)

CELESTE, VERDE, DORADO, VIOLETA = (60, 120, 128), (60, 130, 84), (150, 112, 40), (104, 84, 146)


def nav(*slots):
    """La fila de abajo (volver, cerrar...): cada botón en su panel chico."""
    return [([s], None) for s in slots]


def ability(count, spaced, top_border, bottom):
    """Ascensión: arriba el perfil, en el medio cada ícono con su barra debajo (filas 2 y 3), abajo los botones.
    Las columnas, como AbilityMenu.columns."""
    step = 2 if spaced and count <= 4 else 1
    start = 4 - (count - 1) * step // 2
    cols = [start + i * step for i in range(count)]
    groups = [([4], top_border)]
    if step == 1:
        groups.append(([r * 9 + c for c in cols for r in (2, 3)], None))
    else:
        groups += [([2 * 9 + c, 3 * 9 + c], None) for c in cols]
    return groups + bottom


MENUS = {
    'principal': ('', [([11, 12, 13, 14, 15, 20, 21, 22, 23, 24, 30, 31, 32], None)] + nav(49)),
    'proteccion': ('', [([11, 12, 13, 14, 15], None), ([29, 30, 31, 32, 33], CELESTE)]
                   + nav(45, 47, 49, 51)),
    'encargos': ('', [([4], None), ([20], None), ([22], None), ([24], None)] + nav(49)),
    'destilador': ('', [([11], VERDE), ([15], DORADO), ([28, 29, 30], None), ([32, 33, 34], None)] + nav(49)),
    'tienda': ('', [([4], DORADO), ([20, 21, 22, 23, 24, 30, 31, 32], None)] + nav(49, 51)),
    # Acá la fila 4 está llena: los botones de abajo van sin panel (si no, se pisarían)
    'tienda_items': ('', [([4], DORADO), ([r * 9 + c for r in range(1, 5) for c in range(1, 8)], None),
                                ([45, 48, 49, 50], 'suelto')]),
}
MENUS['kits'] = ('\ue016', [([13], None),
                            ([28, 29, 30, 31, 32, 33, 34], (104, 84, 146))] + nav(45, 49))
MENUS['caja_ruleta'] = ('\ue017', [([18, 19, 20, 21, 22, 23, 24, 25, 26], None)])
MENUS['caja_lista'] = ('\ue018', [([20], None), ([22], None), ([24], None)] + nav(49))
# Premios de una caja: un panel liso (sin casilleros) del alto justo, seg\u00fan cu\u00e1ntas filas de premios hay
for rows in range(1, 6):
    MENUS['caja_premios_%d' % rows] = (chr(0xE040 + rows), [([r * 9 + c for r in range(rows) for c in range(9)], 'liso')]
                                       + nav(45, 49, 53))
MENUS['herrero'] = (chr(0xE01A), [([4], DORADO), ([r * 9 + c for r in range(1, 4) for c in range(1, 8)], None)] + nav(49, 51))
MENUS['recompensas'] = (chr(0xE01B), [([4], DORADO), ([r * 9 + c for r in range(1, 5) for c in range(1, 8)], None)] + nav(49))
MENUS['clan'] = (chr(0xE01C), [([4], DORADO), ([r * 9 + c for r in range(2, 4) for c in range(1, 8)], None)] + nav(45, 47, 49, 51, 53))
for n in range(1, 8):
    MENUS['ascension_%d' % n] = (chr(0xE020 + n), ability(n, False, VIOLETA, nav(49, 53)))
    MENUS['etapa_%d' % n] = (chr(0xE030 + n), ability(n, True, VIOLETA, nav(45, 49, 53)))


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


def draw_panel(px, rnd, slots, border, pad=3):
    """El panel detrás de un grupo: la unión de los casilleros agrandada, con luz arriba, sombra abajo y alguna gota
    de sangre que chorrea del borde de abajo."""
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
                px[q] = OUTLINE + (255,)
    # Gotas: desde el borde de abajo (lejos de las esquinas), una cada tanto
    # (no si el panel llega a la fila 4: caerían sobre los botones de abajo)
    edge = sorted((x, y) for (x, y) in mask if (x, y + 1) not in mask
                  and (x - 3, y) in mask and (x + 3, y) in mask and y < GY + 5 * 18 - 4)
    for (x, y) in edge:
        if rnd.random() < 0.045:
            length = rnd.choice((1, 2, 2, 3, 4))
            for i in range(1, length + 2):
                if (x, y + i) in mask or y + i >= GY + 6 * 18:
                    break
                px[x, y + i] = (BLOOD if i <= length else BLOOD_DARK) + (255,)
            if length >= 3 and rnd.random() < 0.5:   # la gota, un poco más gorda al final
                px[x + 1, y + length] = BLOOD_DARK + (255,)


def frame(name, groups):
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
    for slots, border in groups:
        if border != 'suelto':
            draw_panel(px, rnd, slots, None if border == 'liso' else border)
    for slots, border in groups:
        if border == 'liso':   # panel sin casilleros: los ítems quedan apoyados encima
            continue
        for s in slots:
            draw_slot(px, *slot_xy(s))
    if name == 'caja_ruleta':
        cx = GX + 4 * 18 + 9
        for d in range(5):
            for x in range(cx - 5 + d, cx + 5 - d):
                px[x, GY + 2 * 18 - 8 + d] = BLOOD + (255,)          # arriba, apuntando para abajo
                px[x, GY + 3 * 18 + 7 - d] = BLOOD + (255,)          # abajo, apuntando para arriba
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
for name, (char, groups) in MENUS.items():
    img = frame(name, groups)
    img.save(os.path.join(ROOT, 'assets', 'terror', 'textures', 'gui', 'menu_%s.png' % name))
    font['providers'].append({'type': 'bitmap', 'file': 'terror:gui/menu_%s.png' % name, 'ascent': 13, 'height': H,
                              'chars': [char]})
    if len(sys.argv) > 1:
        preview(img, name, sys.argv[1])
with open(fonts, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(font, f, indent=2)
print(len(MENUS), 'fondos')
