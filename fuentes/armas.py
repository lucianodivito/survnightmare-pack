"""
Las armas especiales con su propia textura (terror:<arma>): parten de las del juego (la misma forma, así se reconocen)
y las rehacen, para que se distingan de una común a la distancia.
- Condenado (espada, pico, hacha, pala y la armadura, también puesta): las de "Dark Iron", de Drift007_ (MIT,
  https://modrinth.com/resourcepack/dark-iron-tools-and-armor), en fuentes/dark_iron/. El arco: madera negra y cuerda
  blanca.
- Ballesta del Vigía: madera quemada, metal oxidado con bordes vivos y remaches.
- Mazo de la Luna Roja: la cabeza rojo sangre, con púas y gotas que caen.
- Lanza del Umbral: negra violácea, con el borde violeta y una grieta de alma en el medio.
Copia también los modelos del juego que hagan falta (el arco tensándose, la ballesta cargada, la lanza en la mano).
Uso: python fuentes/armas.py <cliente.jar de la versión> [vista.png]
"""
import colorsys, io, json, os, sys, zipfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAR = zipfile.ZipFile(sys.argv[1])
A = os.path.join(ROOT, 'assets', 'terror')


def hsv(c):
    return colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)


def lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def clamp(r, g, b, a):
    return (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))), a)


def is_wood(c):
    h, s, v = hsv(c)
    return 0.03 < h < 0.14 and s > 0.25


def is_gray(c):
    return hsv(c)[1] < 0.18


# ------------------------------------------------------------------ los estilos (sobre la imagen entera)

def opaque(px, w, h, x, y):
    return 0 <= x < w and 0 <= y < h and px[x, y][3] > 0


def edge(px, w, h, x, y):
    """Si el píxel toca un lado vacío (es borde de la figura)."""
    return any(not opaque(px, w, h, x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def lit(px, w, h, x, y):
    """Borde del lado iluminado (arriba o a la derecha): ahí va el color; el otro lado queda oscuro."""
    return not opaque(px, w, h, x, y - 1) or not opaque(px, w, h, x + 1, y)


def hashed(x, y, n):
    return (x * 7 + y * 13 + x * y) % n == 0


def spikes(img, mask, color, every=4, away=None):
    """Púas: desde el borde de {mask}, un píxel hacia afuera (a lo vacío), cada tanto."""
    px = img.load()
    w, h = img.size
    out = []
    for (x, y) in mask:
        for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] == 0 and hashed(nx, ny, every):
                if away and not away(nx, ny):
                    continue
                out.append((nx, ny))
    for p in out:
        px[p] = color


def gray(v):
    v = max(0, min(255, int(v)))
    return (v, v, v + (3 if v < 250 else 0), 255)


def condenado_herramienta(img):
    """Hierro forjado y hueso: blanco del lado iluminado, gris en el medio, contorno negro; púas negras y el mango
    envuelto en cadena gris oscura. Nada de rojo: blanco, gris y negro (y bien claro, así no parece netherita)."""
    px = img.load()
    w, h = img.size
    orig = {(x, y): px[x, y] for y in range(h) for x in range(w)}
    metal = {p for p, c in orig.items() if c[3] and 0.38 < hsv(c)[0] < 0.62 and hsv(c)[1] > 0.15}
    handle = {p for p, c in orig.items() if c[3] and is_wood(c)}
    for (x, y) in metal:
        l = lum(orig[(x, y)])
        if lit(px, w, h, x, y):
            px[x, y] = gray(238)                                                        # el filo, casi blanco
        elif edge(px, w, h, x, y):
            px[x, y] = gray(30)                                                         # contorno negro
        else:
            px[x, y] = gray(95 + (l - 60) * 0.7)                                         # gris
    for (x, y) in handle:                                                               # mango: a rayas, de preso
        px[x, y] = gray(225) if (x + y) % 4 < 2 else gray(32)
    spikes(img, metal, gray(28), 3,
           away=lambda nx, ny: all(abs(nx - hx) + abs(ny - hy) > 2 for hx, hy in handle))
    return img


def condenado_arco(img):
    """Madera negra, cuerda blanca y púas negras en las puntas."""
    px = img.load()
    w, h = img.size
    orig = {(x, y): px[x, y] for y in range(h) for x in range(w)}
    wood = {p for p, c in orig.items() if c[3] and is_wood(c)}
    for (x, y), c in orig.items():
        if not c[3]:
            continue
        l = lum(c)
        if (x, y) in wood:
            px[x, y] = gray(150) if lit(px, w, h, x, y) and hashed(x, y, 2) else gray(l * 0.3 + 22)
        elif is_gray(c) and l > 120:
            px[x, y] = gray(232)                                                        # cuerda blanca
        elif is_gray(c):
            px[x, y] = gray(l * 0.6)
    return img


def vigia(img):
    px = img.load()
    w, h = img.size
    orig = {(x, y): px[x, y] for y in range(h) for x in range(w)}
    for (x, y), c in orig.items():
        if not c[3]:
            continue
        l = lum(c)
        if is_wood(c):
            px[x, y] = clamp(c[0] * 0.45, c[1] * 0.35, c[2] * 0.3, 255)                 # madera quemada
        elif is_gray(c) and 40 < l < 210:
            if lit(px, w, h, x, y) and hashed(x, y, 2):
                px[x, y] = clamp(220, 120, 48, 255)                                      # algún borde de óxido vivo
            elif hashed(x, y, 4):
                px[x, y] = clamp(225, 205, 180, 255)                                     # remaches
            else:
                px[x, y] = clamp(l * 1.15, l * 0.6, l * 0.32, 255)                       # óxido
    return img


def luna_roja(img):
    px = img.load()
    w, h = img.size
    orig = {(x, y): px[x, y] for y in range(h) for x in range(w)}
    # La cabeza: arriba a la derecha (el mazo es todo del mismo gris azulado: se separa por la posición)
    head = {(x, y) for (x, y), c in orig.items() if c[3] and (y <= 8 or (y <= 10 and x >= 8))}
    for (x, y) in head:
        l = lum(orig[(x, y)])
        if edge(px, w, h, x, y):
            px[x, y] = clamp(225, 40, 52, 255)
        else:
            px[x, y] = clamp(l * 0.55 + 50, 12, 20, 255)
    spikes(img, head, clamp(70, 8, 14, 255), 2)
    for (x, y) in sorted(head):                                                          # gotas que caen
        if y + 1 < h and px[x, y + 1][3] == 0 and hashed(x, y, 3):
            for i in range(1, 3):
                if y + i < h and px[x, y + i][3] == 0:
                    px[x, y + i] = clamp(170, 14, 24, 255) if i == 1 else clamp(110, 8, 16, 255)
    return img


def umbral(img):
    px = img.load()
    w, h = img.size
    orig = {(x, y): px[x, y] for y in range(h) for x in range(w)}
    for (x, y), c in orig.items():
        if not c[3]:
            continue
        l = lum(c)
        if lit(px, w, h, x, y) and l > 50:
            px[x, y] = clamp(150, 104, 220, 255)                                         # borde violeta (de un lado)
        elif l > 110:
            px[x, y] = clamp(110, 220, 232, 255)                                         # la grieta de alma
        else:
            px[x, y] = clamp(l * 0.35 + 14, l * 0.2 + 6, l * 0.45 + 26, 255)              # negro violáceo
    return img


def armadura(img):
    """Acero pavonado: la armadura de netherita con todo su sombreado y sus detalles, pero con el brillo estirado a un
    gris azulado intermedio (más claro que la netherita, más oscuro y frío que el hierro). Así, puesta y en el ícono,
    se lee como una armadura del juego y no se confunde con ninguna."""
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if not c[3]:
                continue
            l = lum(c)
            v = 40 + (l - 10) / 101 * 165                  # 10..111 de la netherita -> 40..205
            px[x, y] = (max(0, min(255, int(v * 0.9))), max(0, min(255, int(v * 0.96))), max(0, min(255, int(v * 1.08 + 4))), c[3])
    return img


def steel(v):
    """Un gris acero, apenas azulado."""
    v = max(0, min(255, int(v)))
    return (v, v + 2 if v < 253 else v, min(255, v + 8), 255)


# ------------------------------------------------------------------ el Condenado, dibujado a mano (16x16)
# Hierro forjado: K contorno, D sombra, M acero, L acero claro, W filo, R remache; el mango de cuero (H, h) con
# eslabones de cadena (C, c).
CON = {'K': (22, 24, 32, 255), 'D': (50, 55, 68, 255), 'M': (92, 99, 116, 255), 'L': (146, 155, 174, 255),
       'W': (212, 220, 236, 255), 'R': (184, 192, 208, 255), 'H': (52, 40, 34, 255), 'h': (84, 66, 54, 255),
       'C': (160, 168, 184, 255), 'c': (84, 90, 104, 255)}   # acero pavonado, como la armadura


def sprite(rows):
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        assert len(row) == 16, (y, row)
        for x, ch in enumerate(row):
            if ch in CON:
                img.putpixel((x, y), CON[ch])
    return img


ESPADA = [
    '............KKK.',
    '...........KWWLK',
    '..........KWLLDK',
    '.........KWLMDK.',
    '........KWLMDK..',
    '.......KWLMDK...',
    '......KWLMDK....',
    '..KK.KWLMDK.....',
    '.KRMKWLMDK......',
    '.KMLWLMDK.......',
    '..KLMMDK........',
    '..KCKMMK........',
    '.KcHCKRMK.......',
    'KRKCHK..........',
    'KRRK.K..........',
    '.KK.............',
]

PICO = [
    '...KKKKKK.......',
    '..KWWWWLLKK.....',
    '.KWLLLMMMDDK....',
    '.KLMKKKKMMDDK...',
    '.KDK....KRMDDK..',
    '..K....KCKMDDDK.',
    '......KcHKKRMDK.',
    '.....KCHK..KMMLK',
    '....KcHK....KMLK',
    '...KCHK.....KMWK',
    '..KcHK......KLWK',
    '.KCHK.......KLWK',
    'KRHK.......KMLWK',
    'KRK........KLWK.',
    '.K.........KKK..',
    '................',
]

HACHA = [
    '.....KKKK.......',
    '....KWWLLK......',
    '...KWLLMMDK.....',
    '...KWLMMMDDK....',
    '...KWLMMRKDK....',
    '...KLMMDKCHK....',
    '....KDDKcHK.....',
    '.....KKCHK......',
    '......KcHK......',
    '.....KCHK.......',
    '....KcHK........',
    '...KCHK.........',
    '..KcHK..........',
    '.KRHK...........',
    'KRRK............',
    '.KK.............',
]

PALA = [
    '..........KKK...',
    '.........KWWLK..',
    '........KWLLMDK.',
    '........KWLMMDK.',
    '........KLMMDDK.',
    '.........KMDDK..',
    '........KRKKK...',
    '.......KCHK.....',
    '......KcHK......',
    '.....KCHK.......',
    '....KcHK........',
    '...KCHK.........',
    '..KcHK..........',
    '.KRHK...........',
    'KRRK............',
    '.KK.............',
]


def dibujo(rows):
    return lambda img: sprite(rows)


# (nombre del ítem nuevo, ítem del juego del que parte, paleta)
DARK = os.path.join(ROOT, 'fuentes', 'dark_iron')


def dark(name):
    """Una textura de "Dark Iron" (Drift007_, MIT): fuentes/dark_iron/."""
    return lambda img: Image.open(os.path.join(DARK, name + '.png')).convert('RGBA')


ARMAS = [
    ('espada_condenado', 'iron_sword', dark('iron_sword')),
    ('pico_condenado', 'iron_pickaxe', dark('iron_pickaxe')),
    ('hacha_condenado', 'iron_axe', dark('iron_axe')),
    ('pala_condenado', 'iron_shovel', dark('iron_shovel')),
    ('arco_condenado', 'bow', condenado_arco),
    ('ballesta_vigia', 'crossbow', vigia),
    ('mazo_luna_roja', 'mace', luna_roja),
    ('lanza_umbral', 'netherite_spear', umbral),
    ('yelmo_condenado', 'netherite_helmet', dark('iron_helmet')),
    ('peto_condenado', 'netherite_chestplate', dark('iron_chestplate')),
    ('grebas_condenado', 'netherite_leggings', dark('iron_leggings')),
    ('botas_condenado', 'netherite_boots', dark('iron_boots')),
]


def recolor(path, style):
    return style(Image.open(io.BytesIO(JAR.read(path))).convert('RGBA'))


def write_json(rel, data):
    path = os.path.join(A, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, 'w'), indent=2)


previews = []
for out, base, palette in ARMAS:
    armor = base.startswith('netherite_') and not base.endswith('spear')
    models = []
    if armor:
        # Las piezas de armadura: un modelo simple (sin los adornos de herrería)
        definition = {'model': {'type': 'minecraft:model', 'model': 'terror:item/' + out}}
        models.append((base, out))
    else:
        definition = json.loads(JAR.read('assets/minecraft/items/%s.json' % base))

        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == 'model' and isinstance(v, str) and v.startswith('minecraft:item/'):
                        name = v.split('/', 1)[1]
                        models.append((name, out + '__' + name))
                        node[k] = 'terror:item/' + out + '__' + name
                    else:
                        walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
        walk(definition)
    write_json('items/%s.json' % out, definition)
    for name, new in models:
        model = json.loads(JAR.read('assets/minecraft/models/item/%s.json' % name))
        if armor:
            model = {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'minecraft:item/' + base}}
        for key, tex in list(model.get('textures', {}).items()):
            if not tex.startswith('minecraft:item/'):
                continue
            tname = tex.split('/', 1)[1]
            img = recolor('assets/minecraft/textures/item/%s.png' % tname, palette)
            tnew = new if armor else out + '__' + tname
            img.save(os.path.join(A, 'textures', 'item', tnew + '.png'))
            model['textures'][key] = 'terror:item/' + tnew
            if len(previews) < 40 and img.width == 16:
                previews.append(img)
        write_json('models/item/%s.json' % new, model)
    print(out)

# La armadura del Condenado (puesta y los íconos) y sus herramientas son las de "Dark Iron" (Drift007_, MIT). El
# "equipment" que la viste:
write_json('equipment/condenado.json', {'layers': {
    'humanoid': [{'texture': 'terror:condenado'}], 'humanoid_leggings': [{'texture': 'terror:condenado'}]}})
for layer in ('humanoid', 'humanoid_leggings'):   # puesta: la de Dark Iron
    path = os.path.join(A, 'textures', 'entity', 'equipment', layer, 'condenado.png')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.open(os.path.join(DARK, layer + '.png')).convert('RGBA').save(path)

if len(sys.argv) > 2 and previews:
    view = Image.new('RGBA', (17 * len(previews), 16), (60, 60, 60, 255))
    for i, img in enumerate(previews):
        view.alpha_composite(img, (i * 17, 0))
    view.resize((view.width * 8, view.height * 8), Image.NEAREST).save(sys.argv[2])
