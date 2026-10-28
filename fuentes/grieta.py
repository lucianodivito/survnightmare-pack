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


def shape_mask(rnd):
    """La forma: una curva con 4 a 6 puntos, a veces con un rulo en una punta, y grosor que crece hacia el medio."""
    big = 4   # se dibuja grande y se achica, para que los bordes queden prolijos
    # Una ola que cruza todo el cuadro, con una o dos vueltas
    n = rnd.randint(6, 8)
    amp, freq, phase = rnd.uniform(16, 30), rnd.uniform(0.7, 1.6), rnd.uniform(0, math.pi * 2)
    pts = [(i / (n - 1), math.sin(i / (n - 1) * math.pi * 2 * freq + phase) * amp + rnd.uniform(-6, 6)) for i in range(n)]
    pts = [(10 + t * 100, 64 + y) for t, y in pts]
    if rnd.random() < 0.7:
        # Una punta se enrosca en espiral, hacia adentro
        ex, ey = pts[-1]
        px, py = pts[-2]
        a0 = math.atan2(ey - py, ex - px)
        turn = rnd.choice((1, -1))
        for k in range(1, 7):
            a = a0 + turn * k * 0.9
            r = 16 * (1 - k / 8)
            pts.append((ex + math.cos(a) * r - math.cos(a0) * 4, ey + math.sin(a) * r - math.sin(a0) * 4))
    # Girada al azar, y encajada en el cuadro dejando lugar para el halo
    rot = rnd.uniform(-math.pi, math.pi)
    pts = [((x - 64) * math.cos(rot) - (y - 64) * math.sin(rot), (x - 64) * math.sin(rot) + (y - 64) * math.cos(rot)) for x, y in pts]
    min_x, max_x = min(p[0] for p in pts), max(p[0] for p in pts)
    min_y, max_y = min(p[1] for p in pts), max(p[1] for p in pts)
    fit = min((S - 28) / max(1, max_x - min_x), (S - 28) / max(1, max_y - min_y))
    pts = [(14 + (x - min_x) * fit + ((S - 28) - (max_x - min_x) * fit) / 2,
            14 + (y - min_y) * fit + ((S - 28) - (max_y - min_y) * fit) / 2) for x, y in pts]
    curve = catmull(pts)
    width = rnd.uniform(6, 9)
    mask = Image.new('L', (S * big, S * big), 0)
    d = ImageDraw.Draw(mask)
    total = len(curve)
    wobble = [rnd.uniform(0.75, 1.15) for _ in range(12)]
    for i, (px, py) in enumerate(curve):
        t = i / (total - 1)
        w = width * (math.sin(math.pi * min(1, t)) ** 0.6) * wobble[int(t * 11)]
        r = max(0.6, w) * big
        d.ellipse([px * big - r, py * big - r, px * big + r, py * big + r], fill=255)
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
