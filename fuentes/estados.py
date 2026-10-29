"""
Los estados de Ascensión (terror:estado_<nombre>), debajo de cada habilidad y de cada etapa en lugar de los vidrios:
activa (vela encendida, llama de alma), apagada (la misma vela sin llama, humeando), disponible (el ✦ de la Esencia, en
dorado: la puedes comprar) y bloqueada (un candado). Una textura de 16x16 para cada uno, con su modelo y su ítem.
Uso: python fuentes/estados.py [vista.png]
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WAX = {'L': (234, 228, 210, 255), 'W': (206, 198, 178, 255), 'D': (150, 142, 124, 255),
       'k': (34, 30, 30, 255), 'p': (78, 76, 84, 255), 'P': (48, 47, 53, 255)}
CANDLE = [
    '......LWWD......',
    '.....LLWWD......',
    '.....LLWWDD.....',
    '......LWWD......',
    '......LWWD......',
    '......LWWD......',
    '......LWWD......',
    '....pppppppp....',
    '.....PPPPPP.....',
]

ESTADOS = {
    'activa': ([
        '.......o........',
        '......oo........',
        '......oMo.......',
        '.....oMCMo......',
        '.....oMCMo......',
        '......oMo.......',
        '.......k........',
    ] + CANDLE, dict(WAX, o=(52, 150, 176, 255), M=(110, 222, 236, 255), C=(232, 255, 255, 255))),

    'apagada': ([
        '........s.......',
        '.......s........',
        '.......s........',
        '........s.......',
        '........s.......',
        '.......s........',
        '.......k........',
    ] + CANDLE, dict(WAX, s=(120, 120, 126, 170), L=(170, 166, 154, 255), W=(146, 140, 126, 255),
                     D=(104, 98, 88, 255))),

    'disponible': ([
        '................',
        '.......y........',
        '.......y........',
        '......yYy.......',
        '......yYy.......',
        '.....yYWYy......',
        '...yyYWWWYyy....',
        '.yyYYWWWWWYYyy..',
        '...yyYWWWYyy....',
        '.....yYWYy......',
        '......yYy.......',
        '......yYy.......',
        '.......y........',
        '.......y........',
        '................',
        '................',
    ], {'y': (168, 112, 30, 255), 'Y': (232, 172, 52, 255), 'W': (255, 236, 160, 255)}),

    'bloqueada': ([
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
    ], {'s': (112, 110, 118, 255), 'S': (160, 158, 166, 255), 'B': (120, 118, 126, 255),
        'H': (84, 82, 90, 255), 'D': (46, 45, 50, 255), 'r': (120, 18, 28, 255)}),
}

view = Image.new('RGBA', (16 * len(ESTADOS) + len(ESTADOS) - 1, 16), (60, 60, 60, 255))
for i, (name, (art, colors)) in enumerate(ESTADOS.items()):
    assert len(art) == 16 and all(len(r) == 16 for r in art), (name, len(art), [len(r) for r in art])
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            if ch in colors:
                img.putpixel((x, y), colors[ch])
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
