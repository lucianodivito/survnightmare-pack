"""
Las armas especiales con su propia textura (terror:<arma>): parten de las del juego (la misma forma, así se reconocen)
y les cambian los colores de los detalles, para que se distingan de una común a la distancia.
- Condenado (espada, pico, hacha, arco): el metal pasa a acero gris oscuro, con un brillo rojo en el filo.
- Armadura del Condenado: la de netherita, más negra y con las costuras en rojo; también puesta (equipment).
- Ballesta del Vigía: madera oscura y metal oxidado.   - Mazo de la Luna Roja: la cabeza, rojo sangre.
- Lanza del Umbral: la netherita con reflejos violetas.
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


# ------------------------------------------------------------------ las paletas

def condenado(c):
    r, g, b, a = c
    if a == 0:
        return c
    h, s, v = hsv(c)
    l = lum(c)
    if 0.38 < h < 0.62 and s > 0.15:            # el diamante: acero gris oscuro, el brillo en rojo
        if l > 185:
            return clamp(196, 44, 52, a)
        k = l * 0.62
        return clamp(k + 4, k + 4, k + 10, a)
    if is_wood(c):                               # mango: madera ennegrecida
        return clamp(r * 0.55, g * 0.5, b * 0.5, a)
    if is_gray(c) and l > 150:                   # la cuerda del arco: roja
        return clamp(150, 30, 38, a)
    return c


def armadura(c):
    r, g, b, a = c
    if a == 0:
        return c
    l = lum(c)
    if l > 105:                                  # los brillos de la netherita: costuras rojas
        return clamp(150 + (l - 105) * 0.4, 28, 36, a)
    k = l * 0.7
    return clamp(k + 3, k, k + 2, a)


def vigia(c):
    r, g, b, a = c
    if a == 0:
        return c
    l = lum(c)
    if is_wood(c):
        return clamp(r * 0.62, g * 0.55, b * 0.5, a)
    if is_gray(c) and 40 < l < 200:               # el metal: oxidado
        return clamp(l * 1.15, l * 0.7, l * 0.42, a)
    return c


def luna_roja(c):
    r, g, b, a = c
    if a == 0:
        return c
    l = lum(c)
    if is_gray(c):                                # la cabeza del mazo: rojo sangre
        return clamp(l * 0.95 + 25, l * 0.22, l * 0.24, a)
    return c


def umbral(c):
    r, g, b, a = c
    if a == 0:
        return c
    l = lum(c)
    if l > 95:                                   # los brillos: violeta de grieta
        return clamp(l * 0.8 + 20, l * 0.55 + 10, l * 1.05 + 30, a)
    return clamp(r * 0.9 + 6, g * 0.85, b * 0.95 + 14, a)


# (nombre del ítem nuevo, ítem del juego del que parte, paleta)
ARMAS = [
    ('espada_condenado', 'diamond_sword', condenado),
    ('pico_condenado', 'diamond_pickaxe', condenado),
    ('hacha_condenado', 'diamond_axe', condenado),
    ('arco_condenado', 'bow', condenado),
    ('ballesta_vigia', 'crossbow', vigia),
    ('mazo_luna_roja', 'mace', luna_roja),
    ('lanza_umbral', 'netherite_spear', umbral),
    ('yelmo_condenado', 'netherite_helmet', armadura),
    ('peto_condenado', 'netherite_chestplate', armadura),
    ('grebas_condenado', 'netherite_leggings', armadura),
    ('botas_condenado', 'netherite_boots', armadura),
]


def recolor(path, palette):
    img = Image.open(io.BytesIO(JAR.read(path))).convert('RGBA')
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            px[x, y] = palette(px[x, y])
    return img


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

# La armadura puesta: su propio "equipment" (el ítem lo usa con equippable asset_id terror:condenado)
for layer in ('humanoid', 'humanoid_leggings'):
    img = recolor('assets/minecraft/textures/entity/equipment/%s/netherite.png' % layer, armadura)
    path = os.path.join(A, 'textures', 'entity', 'equipment', layer, 'condenado.png')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
write_json('equipment/condenado.json', {'layers': {
    'humanoid': [{'texture': 'terror:condenado'}], 'humanoid_leggings': [{'texture': 'terror:condenado'}]}})
print('equipment condenado')

if len(sys.argv) > 2 and previews:
    view = Image.new('RGBA', (17 * len(previews), 16), (60, 60, 60, 255))
    for i, img in enumerate(previews):
        view.alpha_composite(img, (i * 17, 0))
    view.resize((view.width * 8, view.height * 8), Image.NEAREST).save(sys.argv[2])
