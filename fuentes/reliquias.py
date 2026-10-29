"""
Las reliquias de los jefes (terror:reliquia_<nombre>): una textura de 16x16 para cada una, con su modelo y su ítem.
Uso: python fuentes/reliquias.py [vista.png]
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RELIQUIAS = {
    # La campanita del Inquilino: de bronce viejo, con verdín, colgando de una manija de madera
    'campanita': ([
        '................',
        '.......HH.......',
        '......h..h......',
        '......hHHh......',
        '.......dd.......',
        '......dBBd......',
        '.....dbBBBd.....',
        '.....dbBBrd.....',
        '....dbBBBBBd....',
        '....dbBBBBrd....',
        '....dbBrBBBd....',
        '...dbBBBBBBBd...',
        '...ddddddddddd..',
        '.......cc.......',
        '................',
        '................',
    ], {
        'h': (90, 60, 36, 255), 'H': (126, 88, 52, 255),
        'B': (168, 132, 62, 255), 'b': (214, 186, 104, 255), 'd': (104, 78, 40, 255),
        'r': (86, 126, 102, 255), 'c': (54, 46, 40, 255),
    }),
    # La pelota del Chico: roja, desteñida y sucia
    'pelota': ([
        '................',
        '................',
        '.....oRRRRo.....',
        '....RRRRRRRR....',
        '...RRrRRRRRRR...',
        '...RrRRRRRRRo...',
        '..oWWWWWWWWWWo..',
        '..WWwWWWWWWWWo..',
        '..WWWWWWsWWWWo..',
        '..RRRRRRRRRRRo..',
        '...RRRRRRssRo...',
        '...oRRRRRRRRo...',
        '....oRRRRRRo....',
        '.....oooooo.....',
        '................',
        '................',
    ], {
        'R': (146, 56, 52, 255), 'r': (192, 98, 90, 255), 'o': (88, 34, 32, 255),
        'W': (196, 188, 172, 255), 'w': (228, 222, 208, 255), 's': (92, 76, 58, 255),
    }),
    # La hoz del Espantapájaros: hoja curva, oxidada, mango de madera gastado
    'hoz': ([
        '................',
        '......SSSSS.....',
        '....SSsssssS....',
        '...Ss.....SsS...',
        '..Ss.......Ss...',
        '..S.........S...',
        '..r.........s...',
        '...r.......Sr...',
        '..........Sr....',
        '.........HS.....',
        '........Hh......',
        '.......Hh.......',
        '......Hh........',
        '.....Hh.........',
        '....hh..........',
        '................',
    ], {
        'S': (138, 138, 140, 255), 's': (196, 196, 198, 255), 'r': (124, 76, 48, 255),
        'H': (122, 86, 52, 255), 'h': (84, 58, 36, 255),
    }),
    # El farol del poste: hierro negro, vidrio sucio, una llama que casi no da luz
    'farol': ([
        '................',
        '......cccc......',
        '......c..c......',
        '.......cc.......',
        '.....IIIIII.....',
        '....IiiiiiiI....',
        '.....IggggI.....',
        '.....IgfggI.....',
        '.....IgFfgI.....',
        '.....IgFFgI.....',
        '.....IggggI.....',
        '....IiiiiiiI....',
        '.....IIIIII.....',
        '................',
        '................',
        '................',
    ], {
        'c': (78, 78, 82, 255), 'I': (46, 46, 50, 255), 'i': (96, 96, 102, 255),
        'g': (38, 42, 38, 230), 'F': (214, 168, 76, 255), 'f': (250, 224, 150, 255),
    }),
    # El peldaño: un escalón de porcelana, rajado
    'peldano': ([
        '................',
        '................',
        '................',
        '.......wwwwwww..',
        '.......wPPPPPQ..',
        '.......wPPkPPQ..',
        '.......wPPPkPQ..',
        '..wwwwwwPPPPPQ..',
        '..wPPPPPPPPPPQ..',
        '..wPPPPPPPPPPQ..',
        '..wPkPPPPPPPPQ..',
        '..wPPkkPPPPPPQ..',
        '..wPPPPPPPkPPQ..',
        '..QQQQQQQQQQQQ..',
        '................',
        '................',
    ], {
        'w': (240, 236, 228, 255), 'P': (212, 206, 196, 255), 'Q': (146, 140, 132, 255),
        'k': (66, 60, 56, 255),
    }),
    # El ancla: hierro comido por el óxido, con algas pegadas
    'ancla': ([
        '................',
        '.......OO.......',
        '......O..O......',
        '.......OO.......',
        '.....AaaaA......',
        '.......aA.......',
        '.......aA.......',
        '.......aM.......',
        '.......aA.......',
        '..A....aA....A..',
        '..aA...aA...aA..',
        '...aA..aM..aA...',
        '....aAAAAAMA....',
        '.....AAMAAA.....',
        '................',
        '................',
    ], {
        'O': (70, 64, 60, 255), 'A': (92, 68, 56, 255), 'a': (138, 100, 76, 255),
        'M': (66, 98, 58, 255),
    }),
    # Los ojos de Nadie: su cara negra, sin boca, con los mismos ojos de su skin (rendijas blancas, brillo rojo)
    'ojos': ([
        '................',
        '................',
        '................',
        '...eKKKKKKKKe...',
        '...KKKKKKKKKK...',
        '...KKKKKKKKKK...',
        '...KrrrKKrrrK...',
        '...KWWWKKWWWK...',
        '...KrrrKKrrrK...',
        '...KKKKKKKKKK...',
        '...KKKKKKKKKK...',
        '...KKKKKKKKKK...',
        '...eKKKKKKKKe...',
        '................',
        '................',
        '................',
    ], {
        'K': (10, 10, 12, 255), 'e': (22, 22, 26, 255),
        'W': (250, 250, 245, 255), 'r': (120, 10, 10, 255),
    }),
}

view = Image.new('RGBA', (16 * len(RELIQUIAS) + len(RELIQUIAS) - 1, 16), (60, 60, 60, 255))
for i, (name, (art, colors)) in enumerate(RELIQUIAS.items()):
    assert len(art) == 16 and all(len(r) == 16 for r in art), name
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            if ch in colors:
                img.putpixel((x, y), colors[ch])
    key = 'reliquia_' + name
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
