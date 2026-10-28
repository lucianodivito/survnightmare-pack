"""
Huella de pie descalzo (terror:huella), vista desde arriba con los dedos hacia arriba: barro oscuro y húmedo.
Es un pie derecho, en 32x32; el plugin la espeja para el izquierdo. Genera la textura y el modelo.
Uso: python fuentes/huella.py [vista.png]
"""
import json, os, random, sys
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(77)

# Se dibuja grande (128x128) y se achica a 32x32
big = Image.new('L', (128, 128), 0)
d = ImageDraw.Draw(big)
d.ellipse([46, 84, 78, 124], fill=255)           # talón
d.polygon([(50, 100), (76, 100), (86, 62), (56, 62)], fill=255)   # puente (más angosto del lado de adentro)
d.ellipse([44, 36, 92, 72], fill=255)            # planta
for cx, cy, r in ((82, 18, 9), (66, 15, 6.5), (54, 19, 5.5), (44, 25, 5), (36, 34, 4.5)):   # dedos (el gordo a la derecha)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
mask = big.resize((32, 32), Image.BOX)

img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
for y in range(32):
    for x in range(32):
        a = mask.getpixel((x, y))
        if a < 90:
            continue
        v = rnd.randint(30, 44)
        edge = a < 200
        c = (v + 14, v + 6, v) if not edge else (v + 26, v + 18, v + 10)   # el borde, más claro (barro que se seca)
        img.putpixel((x, y), c + (255,))

tex = os.path.join(ROOT, 'assets', 'terror', 'textures', 'item', 'huella.png')
os.makedirs(os.path.dirname(tex), exist_ok=True)
img.save(tex)
model = os.path.join(ROOT, 'assets', 'terror', 'models', 'item', 'huella.json')
json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'terror:item/huella'}}, open(model, 'w'), indent=2)
item = os.path.join(ROOT, 'assets', 'terror', 'items', 'huella.json')
json.dump({'model': {'type': 'minecraft:model', 'model': 'terror:item/huella'}}, open(item, 'w'), indent=2)
print(tex, model, item, sep='\n')
if len(sys.argv) > 1:
    view = Image.new('RGBA', (32, 32), (110, 140, 70, 255)); view.alpha_composite(img)
    view.resize((256, 256), Image.NEAREST).save(sys.argv[1])
