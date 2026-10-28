"""
Ítem Ectoplasma (terror:ectoplasma): un frasco con baba espectral. Genera la textura y el modelo.
Uso: python fuentes/ectoplasma.py [vista.png]
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = [
    '................',
    '......cccc......',
    '......cCCc......',
    '.....GggggG.....',
    '.....EgaagG.....',
    '.....EgaagG.....',
    '.....gaaaaG.....',
    '....gaaaaaaG....',
    '...gEELEEEEEG...',
    '...gELEEEEbEG...',
    '...gEbEEEEEEG...',
    '...gEEEEEDEEG...',
    '...gEEEDDEEDG...',
    '....GDDDDDDG....',
    '.....GGGGGG.....',
    '................',
]
COLORS = {
    'c': (112, 76, 44, 255), 'C': (148, 104, 62, 255),        # corcho
    'g': (205, 218, 222, 200), 'G': (120, 132, 138, 220),     # vidrio, y su borde en sombra
    'a': (210, 230, 235, 70),                                 # vidrio vacío
    'E': (140, 236, 168, 255), 'D': (70, 178, 112, 255),      # la baba, y su fondo
    'L': (232, 255, 238, 255), 'b': (196, 255, 214, 255),     # brillo y burbujas
}
img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
for y, row in enumerate(ART):
    for x, ch in enumerate(row):
        if ch in COLORS:
            img.putpixel((x, y), COLORS[ch])

tex = os.path.join(ROOT, 'assets', 'terror', 'textures', 'item', 'ectoplasma.png')
os.makedirs(os.path.dirname(tex), exist_ok=True)
img.save(tex)
model = os.path.join(ROOT, 'assets', 'terror', 'models', 'item', 'ectoplasma.json')
os.makedirs(os.path.dirname(model), exist_ok=True)
json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'terror:item/ectoplasma'}}, open(model, 'w'), indent=2)
item = os.path.join(ROOT, 'assets', 'terror', 'items', 'ectoplasma.json')
os.makedirs(os.path.dirname(item), exist_ok=True)
json.dump({'model': {'type': 'minecraft:model', 'model': 'terror:item/ectoplasma'}}, open(item, 'w'), indent=2)
print(tex, model, item, sep='\n')
if len(sys.argv) > 1:
    view = Image.new('RGBA', (16, 16), (60, 60, 60, 255)); view.alpha_composite(img)
    view.resize((256, 256), Image.NEAREST).save(sys.argv[1])
