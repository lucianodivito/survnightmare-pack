"""
El Peldañero (jefe de La Escalera): skin de jugador de 64x64 (brazos anchos). Una figura de porcelana blanca, como las
escaleras de cuarzo: lisa, con rajaduras negras; la cara sin rasgos, salvo dos agujeros negros y una grieta que la
cruza; una túnica blanca larga y las manos y los pies grises, de estatua. Al morir se rompe como vidrio.
El plugin la usa con terror:entity/quebaja (assets/terror/textures/entity/quebaja.png).
Uso: python fuentes/quebaja.py [vista.png]
"""
import os, random, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(777)
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

PORCELAIN = (232, 230, 224)
PORCELAIN_SHADE = (204, 202, 196)
ROBE = (222, 220, 212)
ROBE_FOLD = (196, 194, 186)
STONE = (150, 150, 148)
CRACK = (24, 22, 24)


def noisy(c, amount=4):
    n = rnd.randint(-amount, amount)
    return tuple(max(0, min(255, v + n)) for v in c) + (255,)


def fill(x0, y0, x1, y1, color, amount=4):
    for y in range(y0, y1):
        for x in range(x0, x1):
            img.putpixel((x, y), noisy(color, amount))


def px(x, y, color):
    img.putpixel((x, y), tuple(color[:3]) + (255,))


def crack(x, y, x0, y0, x1, y1, steps):
    """Una rajadura que camina torcida, sin salirse de la cara (x0..x1, y0..y1)."""
    for _ in range(steps):
        if x0 <= x < x1 and y0 <= y < y1:
            px(x, y, CRACK)
        x += rnd.choice((-1, 0, 1))
        y += rnd.choice((0, 1, 1))


# ---- Cabeza: porcelana, un poco más sombreada arriba y atrás
fill(0, 8, 32, 16, PORCELAIN)
fill(8, 0, 24, 8, PORCELAIN_SHADE)
fill(24, 8, 32, 16, PORCELAIN_SHADE)
# Cara (8..15 x 8..15): dos agujeros negros y una grieta que baja desde la frente por un ojo
for x in (9, 10, 13, 14):
    for y in (11, 12):
        px(x, y, CRACK)
for x, y in ((12, 8), (12, 9), (13, 10), (13, 13), (12, 14), (12, 15)):
    px(x, y, CRACK)
crack(1, 9, 0, 8, 8, 16, 6)      # costado derecho
crack(18, 9, 16, 8, 24, 16, 6)   # costado izquierdo
crack(26, 8, 24, 8, 32, 16, 7)   # atrás

# ---- Cuerpo: túnica blanca larga, con pliegues verticales y alguna rajadura
fill(16, 20, 40, 32, ROBE)
fill(20, 16, 36, 20, ROBE)
for x in (18, 21, 26, 30, 34, 37):
    for y in range(22, 32):
        if rnd.random() < 0.8:
            px(x, y, noisy(ROBE_FOLD, 3)[:3])
crack(23, 20, 20, 20, 28, 32, 8)

# ---- Brazos: mangas de la túnica; manos grises de piedra, con una rajadura
fill(40, 20, 56, 32, ROBE)
fill(44, 16, 52, 20, ROBE)
fill(32, 52, 48, 64, ROBE)
fill(36, 48, 44, 52, ROBE)
fill(40, 28, 56, 32, STONE)
fill(32, 60, 48, 64, STONE)
fill(48, 16, 52, 20, STONE)
fill(40, 48, 44, 52, STONE)
crack(45, 28, 44, 28, 48, 32, 3)
crack(37, 60, 36, 60, 40, 64, 3)

# ---- Piernas: la túnica llega a los tobillos; pies grises, descalzos
fill(0, 20, 16, 30, ROBE)
fill(16, 52, 32, 62, ROBE)
fill(0, 30, 16, 32, STONE)
fill(16, 62, 32, 64, STONE)
fill(4, 16, 12, 20, ROBE)
fill(20, 48, 28, 52, ROBE)
fill(8, 16, 12, 20, STONE)
fill(24, 48, 28, 52, STONE)
for x in (2, 6, 10, 14):
    for y in range(21, 30):
        if rnd.random() < 0.7:
            px(x, y, noisy(ROBE_FOLD, 3)[:3])
for x in (18, 22, 26, 30):
    for y in range(53, 62):
        if rnd.random() < 0.7:
            px(x, y, noisy(ROBE_FOLD, 3)[:3])

out = os.path.join(ROOT, 'assets', 'terror', 'textures', 'entity', 'quebaja.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print(out)
if len(sys.argv) > 1:
    S = 12
    front = Image.new('RGBA', (16, 32), (150, 160, 175, 255))
    front.alpha_composite(img.crop((8, 8, 16, 16)), (4, 0))
    front.alpha_composite(img.crop((20, 20, 28, 32)), (4, 8))
    front.alpha_composite(img.crop((44, 20, 48, 32)), (0, 8))
    front.alpha_composite(img.crop((36, 52, 40, 64)), (12, 8))
    front.alpha_composite(img.crop((4, 20, 8, 32)), (4, 20))
    front.alpha_composite(img.crop((20, 52, 24, 64)), (8, 20))
    sheet = Image.new('RGBA', (64, 64), (70, 70, 70, 255)); sheet.alpha_composite(img)
    view = Image.new('RGBA', (64 * 8 + 16 * S + 20, max(64 * 8, 32 * S)), (40, 40, 40, 255))
    view.alpha_composite(sheet.resize((64 * 8, 64 * 8), Image.NEAREST))
    view.alpha_composite(front.resize((16 * S, 32 * S), Image.NEAREST), (64 * 8 + 10, 0))
    view.save(sys.argv[1])
