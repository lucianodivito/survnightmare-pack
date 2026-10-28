"""
La grieta (terror:grieta): un disco de oscuridad con estrellitas que titilan, para el portal redondo de las grietas.
64x64 por cuadro, 8 cuadros animados; el disco se ve igual de los dos lados. Genera la textura, su .mcmeta, el modelo
y el ítem. El plugin lo muestra con un ItemDisplay y le pone el anillo de partículas alrededor.
Uso: python fuentes/grieta.py [vista.png]
"""
import json, math, os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(2077)
S, FRAMES = 64, 8
C = (S - 1) / 2
R = 31.0

stars = [(rnd.uniform(4, S - 4), rnd.uniform(4, S - 4), rnd.random(), rnd.choice(((200, 150, 255), (255, 255, 255), (150, 90, 230))))
         for _ in range(70)]
stars = [s for s in stars if math.hypot(s[0] - C, s[1] - C) < R - 3]

sheet = Image.new('RGBA', (S, S * FRAMES), (0, 0, 0, 0))
for f in range(FRAMES):
    frame = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    for y in range(S):
        for x in range(S):
            d = math.hypot(x - C, y - C)
            if d > R:
                continue
            # Casi negro en el medio, un violeta apagado hacia el borde, y el borde mismo más claro
            t = d / R
            base = (8 + 30 * t ** 3, 4 + 10 * t ** 3, 16 + 55 * t ** 3)
            n = rnd.uniform(-3, 3)
            c = [int(max(0, min(255, v + n))) for v in base]
            if d > R - 1.6:
                c = [120, 60, 190]
            frame.putpixel((x, y), tuple(c) + (255,))
    for sx, sy, phase, color in stars:
        bright = 0.5 + 0.5 * math.sin((f / FRAMES + phase) * math.pi * 2)   # titila
        if bright < 0.25:
            continue
        px, py = int(sx), int(sy)
        bg = frame.getpixel((px, py))
        mix = tuple(int(bg[i] * (1 - bright) + color[i] * bright) for i in range(3)) + (255,)
        frame.putpixel((px, py), mix)
    sheet.paste(frame, (0, S * f))

tex = os.path.join(ROOT, 'assets', 'terror', 'textures', 'item', 'grieta.png')
os.makedirs(os.path.dirname(tex), exist_ok=True)
sheet.save(tex)
json.dump({'animation': {'frametime': 5, 'interpolate': True}}, open(tex + '.mcmeta', 'w'), indent=2)

# Una placa finita, con la misma cara de los dos lados
face = {'uv': [0, 0, 16, 16], 'texture': '#disco'}
model = {
    'textures': {'disco': 'terror:item/grieta', 'particle': 'terror:item/grieta'},
    'elements': [{'from': [0, 0, 7.95], 'to': [16, 16, 8.05], 'shade': False,
                  'faces': {'north': face, 'south': dict(face)}}],
}
mpath = os.path.join(ROOT, 'assets', 'terror', 'models', 'item', 'grieta.json')
json.dump(model, open(mpath, 'w'), indent=2)
ipath = os.path.join(ROOT, 'assets', 'terror', 'items', 'grieta.json')
json.dump({'model': {'type': 'minecraft:model', 'model': 'terror:item/grieta'}}, open(ipath, 'w'), indent=2)
print(tex, mpath, ipath, sep='\n')
if len(sys.argv) > 1:
    view = Image.new('RGBA', (S * 4, S), (120, 140, 110, 255))
    for i in range(4):
        view.alpha_composite(sheet.crop((0, S * i * 2, S, S * i * 2 + S)), (S * i, 0))
    view.resize((S * 16, S * 4), Image.NEAREST).save(sys.argv[1])
