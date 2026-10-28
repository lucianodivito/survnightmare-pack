"""
Aldeano esclavo: repinta la profesión "nitwit" (la usan los vendedores de Shopkeepers que pone el plugin Terror).
Parte del aldeano de vanilla (base + tipo llanura) y lo pinta encima entero: piel pálida y enferma, ojos hundidos,
moretones, sangre seca, harapos, collar de hierro con cadena y grilletes en las muñecas.
Uso: python fuentes/esclavo.py <carpeta textures/entity/villager de vanilla> [vista.png]
"""
import colorsys, os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1]
rnd = random.Random(1347)

base = Image.open(os.path.join(SRC, 'villager.png')).convert('RGBA')
base.alpha_composite(Image.open(os.path.join(SRC, 'type', 'plains.png')).convert('RGBA'))
src = base.copy()
out = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

# Partes del modelo (x0, y0, x1, y1) en la textura de 64x64
HEAD = (0, 0, 32, 18)
BODY = (16, 20, 44, 38)
LEGS = (0, 22, 16, 38)
ARMS = (44, 22, 60, 34)
HANDS = (40, 38, 64, 46)
JACKET = (0, 38, 28, 64)
HEAD_FRONT = (8, 8, 16, 18)


def inside(x, y, box):
    return box[0] <= x < box[2] and box[1] <= y < box[3]


def is_skin(c):
    r, g, b, a = c
    if a == 0:
        return False
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return (h < 0.09 or h > 0.97) and 0.2 < s < 0.6 and v > 0.55


def sick(c):
    """Piel pálida, grisácea y apenas verdosa."""
    r, g, b, a = c
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    v = lum * 0.78 + rnd.uniform(-6, 6)
    return (int(v + 4), int(v + 8), int(v - 6), 255)


def rag(c):
    """La ropa: gris pardo, sucio, desparejo."""
    r, g, b, a = c
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    v = lum * 0.62 + rnd.uniform(-5, 4)
    if rnd.random() < 0.07:
        v *= 0.75   # manchas de mugre
    return (int(v + 10), int(v + 5), int(v), 255)


def clamp(c):
    return tuple(max(0, min(255, int(v))) for v in c)


for y in range(64):
    for x in range(64):
        c = src.getpixel((x, y))
        if c[3] == 0:
            continue
        if not any(inside(x, y, b) for b in (HEAD, BODY, LEGS, ARMS, HANDS, JACKET)):
            continue
        out.putpixel((x, y), clamp(sick(c) if is_skin(c) else rag(c)))

# ---- La cara: ojos hundidos (sin el verde), ojeras y sangre seca bajo la nariz
for y in range(HEAD_FRONT[1], HEAD_FRONT[3]):
    for x in range(HEAD_FRONT[0], HEAD_FRONT[2]):
        r, g, b, a = src.getpixel((x, y))
        if a and g > r + 30:                       # el iris verde -> casi negro
            out.putpixel((x, y), (22, 18, 18, 255))
        elif a and r > 220 and g > 220 and b > 220:   # lo blanco del ojo -> amarillento, irritado
            out.putpixel((x, y), (128, 116, 96, 255))
eye_rows = [y for y in range(8, 18) for x in range(8, 16) if src.getpixel((x, y))[1] > src.getpixel((x, y))[0] + 30]
if eye_rows:
    under = max(eye_rows) + 1
    for x in range(9, 15):                       # ojeras
        r, g, b, a = out.getpixel((x, under))
        out.putpixel((x, under), clamp((r * 0.62, g * 0.58, b * 0.66, 255)))
for x, y in ((10, 15), (10, 16), (10, 17)):      # un hilo de sangre seca que baja de un ojo
    out.putpixel((x, y), (74, 20, 20, 255))

# ---- Moretones: manchas violáceas en la cabeza y los brazos
for box, count in ((HEAD, 5), (ARMS, 4), (HANDS, 2)):
    for _ in range(count):
        for _ in range(30):
            x, y = rnd.randrange(box[0], box[2]), rnd.randrange(box[1], box[3])
            if out.getpixel((x, y))[3] and is_skin(src.getpixel((x, y))):
                break
        else:
            continue
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            px, py = x + dx, y + dy
            if inside(px, py, box) and out.getpixel((px, py))[3] and rnd.random() < 0.85:
                r, g, b, a = out.getpixel((px, py))
                out.putpixel((px, py), clamp((r * 0.75 + 8, g * 0.62, b * 0.74 + 12, 255)))

# ---- Hierro
IRON = [(64, 64, 68, 255), (84, 84, 90, 255), (104, 104, 110, 255), (132, 132, 138, 255)]


def iron(x, y, shade=1):
    out.putpixel((x, y), IRON[max(0, min(3, shade + rnd.choice((-1, 0, 0, 1))))])


# Collar: las 2 filas de arriba del saco (los 4 costados), y la parte de arriba alrededor del cuello
for x in range(0, 28):
    iron(x, 44, 2)
    iron(x, 45, 1)
for x in range(8, 12):
    for y in (41, 42):
        iron(x, y, 2)
# Argolla al frente y cadena que cuelga
for x, y in ((9, 46), (10, 46), (9, 47), (10, 47)):
    iron(x, y, 3)
for i, y in enumerate(range(48, 57)):
    if i % 2 == 0:
        iron(9, y, 2); iron(10, y, 1)
    else:
        iron(9 + (i // 2) % 2, y, 3)

# Grilletes: aro de hierro al final de cada brazo (los 4 costados) y en la punta de las manos
for x in range(44, 60):
    iron(x, 32, 1)
    iron(x, 33, 2)
for x in range(52, 56):
    for y in range(22, 26):
        iron(x, y, 1 if (x + y) % 2 else 2)
# Cadena entre las muñecas, cruzando las manos de frente
for x in range(44, 52):
    iron(x, 43, 3 if x % 2 else 1)

tex = os.path.join(ROOT, 'assets', 'minecraft', 'textures', 'entity', 'villager', 'profession', 'nitwit.png')
os.makedirs(os.path.dirname(tex), exist_ok=True)
out.save(tex)
print(tex)

if len(sys.argv) > 2:
    # Vista: la textura entera, y de frente (cara, saco con las manos cruzadas encima, piernas)
    S = 8
    sheet = Image.new('RGBA', (64, 64), (70, 70, 70, 255)); sheet.alpha_composite(out)
    front = Image.new('RGBA', (16, 36), (70, 70, 70, 255))
    full = src.copy(); full.alpha_composite(out)
    front.alpha_composite(full.crop((8, 8, 16, 18)), (4, 0))      # cara
    front.alpha_composite(full.crop((26, 2, 28, 6)), (7, 5))      # nariz
    front.alpha_composite(full.crop((4, 26, 8, 38)), (4, 24))     # piernas
    front.alpha_composite(full.crop((4, 26, 8, 38)), (8, 24))
    front.alpha_composite(full.crop((6, 44, 14, 64)), (4, 10))    # saco
    front.alpha_composite(full.crop((44, 42, 52, 46)), (4, 14))   # manos cruzadas
    front.alpha_composite(full.crop((48, 30, 52, 34)), (0, 13))   # puntas de los brazos
    front.alpha_composite(full.crop((48, 30, 52, 34)), (12, 13))
    view = Image.new('RGBA', (64 * S + 16 * S + 20, 64 * S), (40, 40, 40, 255))
    view.alpha_composite(sheet.resize((64 * S, 64 * S), Image.NEAREST))
    view.alpha_composite(front.resize((16 * S, 36 * S), Image.NEAREST), (64 * S + 10, 0))
    view.save(sys.argv[2])
    print(sys.argv[2])
