"""
Las grietas (terror:grieta_1 ... terror:grieta_8): tajos en el aire con forma de tentáculo, cada uno distinto, como un
desgarro en el mundo. Por dentro, un fondo azul casi negro con puntitos celestes, turquesas y blancos que titilan
(parecido al portal del End); alrededor, un halo celeste translúcido. 128x128 por cuadro, 8 cuadros animados.
Cada forma sale de una curva al azar (con semilla fija, así son siempre las mismas): gruesa en el medio, finita en las
puntas, a veces con la punta enroscada. El plugin elige una al azar para cada grieta.
Uso: python fuentes/grieta.py [vista.png]
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S, FRAMES, SHAPES = 128, 8, 8
STAR_COLORS = [(90, 210, 220), (120, 170, 255), (210, 240, 255), (60, 150, 170), (150, 110, 230)]


def catmull(points, steps=60):
    """Una curva suave que pasa por todos los puntos."""
    out = []
    pts = [points[0]] + points + [points[-1]]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in range(2)))
    out.append(points[-1])
    return out


def stroke(d, curve, width, rnd, big, start=0.0):
    """Dibuja una curva como un desgarro: punta en los dos extremos (o, si {@code start} > 0, ancha donde nace y
    afilada al final), y el borde mordido, irregular, como algo rasgado."""
    total = len(curve)
    # Ruido del borde: suma de ondas cortas, para que el grosor tiemble a lo largo del tajo
    waves = [(rnd.uniform(6, 18), rnd.uniform(0, math.pi * 2), rnd.uniform(0.08, 0.18)) for _ in range(3)]
    for i, (px, py) in enumerate(curve):
        t = i / (total - 1)
        shape = math.sin(math.pi * t) if start == 0 else (1 - t) ** 1.2
        jag = 1 + sum(a * math.sin(t * f * math.pi * 2 + ph) for f, ph, a in waves) + rnd.uniform(-0.12, 0.12)
        r = max(0.4, width * shape * jag) * big
        d.ellipse([px * big - r, py * big - r, px * big + r, py * big + r], fill=255)


def shape_mask(rnd):
    """La forma: un tajo largo y ondulado que cruza el cuadro, afilado en las dos puntas y grueso en el medio, con el
    borde mordido; a veces con una o dos rajaduras finitas que se abren hacia un costado."""
    big = 4   # se dibuja grande y se achica, para que los bordes queden prolijos
    n = rnd.randint(5, 7)
    amp, freq, phase = rnd.uniform(10, 24), rnd.uniform(0.5, 1.2), rnd.uniform(0, math.pi * 2)
    pts = [(i / (n - 1), math.sin(i / (n - 1) * math.pi * 2 * freq + phase) * amp + rnd.uniform(-5, 5)) for i in range(n)]
    pts = [(10 + t * 108, 64 + y) for t, y in pts]
    curve = catmull(pts)
    # Las rajaduras: salen del medio del tajo hacia un costado, cada vez más finitas
    branches = []
    for _ in range(rnd.choice((0, 1, 1, 2))):
        k = rnd.randint(len(curve) * 3 // 10, len(curve) * 7 // 10)
        bx, by = curve[k]
        nx, ny = curve[min(len(curve) - 1, k + 1)]
        along = math.atan2(ny - by, nx - bx)
        a = along + rnd.choice((1, -1)) * rnd.uniform(0.5, 1.1)
        length = rnd.uniform(18, 32)
        mid = (bx + math.cos(a) * length * 0.5 + rnd.uniform(-4, 4), by + math.sin(a) * length * 0.5 + rnd.uniform(-4, 4))
        end = (bx + math.cos(a + rnd.uniform(-0.4, 0.4)) * length, by + math.sin(a + rnd.uniform(-0.4, 0.4)) * length)
        branches.append(catmull([(bx, by), mid, end], 30))
    # Girado al azar, y encajado en el cuadro dejando lugar para el halo
    rot = rnd.uniform(-math.pi, math.pi)
    every = curve + [p for b in branches for p in b]
    turned = lambda p: ((p[0] - 64) * math.cos(rot) - (p[1] - 64) * math.sin(rot), (p[0] - 64) * math.sin(rot) + (p[1] - 64) * math.cos(rot))
    every = [turned(p) for p in every]
    min_x, max_x = min(p[0] for p in every), max(p[0] for p in every)
    min_y, max_y = min(p[1] for p in every), max(p[1] for p in every)
    fit = min((S - 28) / max(1, max_x - min_x), (S - 28) / max(1, max_y - min_y))
    place = lambda p: (14 + (turned(p)[0] - min_x) * fit + ((S - 28) - (max_x - min_x) * fit) / 2,
                       14 + (turned(p)[1] - min_y) * fit + ((S - 28) - (max_y - min_y) * fit) / 2)
    width = rnd.uniform(7, 10)
    mask = Image.new('L', (S * big, S * big), 0)
    d = ImageDraw.Draw(mask)
    stroke(d, [place(p) for p in curve], width, rnd, big)
    for b in branches:
        stroke(d, [place(p) for p in b], width * 0.45, rnd, big, start=1)
    return mask.resize((S, S), Image.LANCZOS)


def render(seed):
    rnd = random.Random(seed)
    mask = shape_mask(rnd)
    halo = mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
    stars = [(x, y, rnd.random(), rnd.choice(STAR_COLORS)) for x in range(S) for y in range(S)
             if mask.getpixel((x, y)) > 128 and rnd.random() < 0.06]
    sheet = Image.new('RGBA', (S, S * FRAMES), (0, 0, 0, 0))
    for f in range(FRAMES):
        frame = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        flicker = 0.85 + 0.15 * math.sin(f / FRAMES * math.pi * 2)
        for y in range(S):
            for x in range(S):
                m, h = mask.getpixel((x, y)), halo.getpixel((x, y))
                if m > 110:
                    n = rnd.randint(-3, 3)
                    frame.putpixel((x, y), (6 + n, 8 + n, 20 + n, 255))
                elif h > 8:
                    # El halo: celeste, más fuerte pegado al tajo, y que respira un poco
                    a = int(min(1, h / 255 * 1.6) * 120 * flicker)
                    frame.putpixel((x, y), (190, 228, 255, a))
        for x, y, phase, color in stars:
            b = 0.5 + 0.5 * math.sin((f / FRAMES + phase) * math.pi * 2)
            if b < 0.3:
                continue
            base = frame.getpixel((x, y))
            frame.putpixel((x, y), tuple(int(base[i] * (1 - b) + color[i] * b) for i in range(3)) + (255,))
        sheet.paste(frame, (0, S * f))
    return sheet


tex_dir = os.path.join(ROOT, 'assets', 'terror', 'textures', 'item')
os.makedirs(tex_dir, exist_ok=True)
previews = []
for i in range(1, SHAPES + 1):
    name = f'grieta_{i}'
    sheet = render(7000 + i * 13)
    sheet.save(os.path.join(tex_dir, name + '.png'))
    json.dump({'animation': {'frametime': 4, 'interpolate': True}}, open(os.path.join(tex_dir, name + '.png.mcmeta'), 'w'), indent=2)
    face = {'uv': [0, 0, 16, 16], 'texture': '#tajo'}
    model = {'textures': {'tajo': f'terror:item/{name}', 'particle': f'terror:item/{name}'},
             'elements': [{'from': [0, 0, 7.95], 'to': [16, 16, 8.05], 'shade': False,
                           'faces': {'north': face, 'south': dict(face)}}]}
    json.dump(model, open(os.path.join(ROOT, 'assets', 'terror', 'models', 'item', name + '.json'), 'w'), indent=2)
    json.dump({'model': {'type': 'minecraft:model', 'model': f'terror:item/{name}'}},
              open(os.path.join(ROOT, 'assets', 'terror', 'items', name + '.json'), 'w'), indent=2)
    previews.append(sheet.crop((0, 0, S, S)))
# La redonda de antes ya no se usa
for old in ('textures/item/grieta.png', 'textures/item/grieta.png.mcmeta', 'models/item/grieta.json', 'items/grieta.json'):
    p = os.path.join(ROOT, 'assets', 'terror', old)
    if os.path.exists(p):
        os.remove(p)
print(f'{SHAPES} grietas en {tex_dir}')
if len(sys.argv) > 1:
    view = Image.new('RGBA', (S * 4, S * 2), (110, 140, 90, 255))
    for i, p in enumerate(previews):
        view.alpha_composite(p, ((i % 4) * S, (i // 4) * S))
    view.resize((S * 4 * 2, S * 2 * 2), Image.NEAREST).save(sys.argv[1])
