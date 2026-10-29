"""
El logo del server para el tab: "SURVIVAL" chico y espaciado en gris, y "NIGHTMARE" grande en rojo sangre (degradé de
arriba hacia abajo, con sombra). Pixel art con una letra propia de 5x7, sin calaveras. Va como un carácter de la fuente
por defecto (\\ue100), que el plugin pone en el encabezado del tab.
Uso: python fuentes/logo.py [vista.png]
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = ''
HEIGHT = 32      # alto en el juego (píxeles de la interfaz)
ASCENT = 7

FONT = {
    'S': ['.###.', '#...#', '#....', '.###.', '....#', '#...#', '.###.'],
    'U': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'R': ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
    'V': ['#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '..#..'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'N': ['#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'],
    'G': ['.###.', '#...#', '#....', '#.###', '#...#', '#...#', '.###.'],
    'H': ['#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
    'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####'],
}


def word_pixels(word, scale, gap):
    """Los píxeles encendidos de una palabra: (x, y, fila de la letra) con la escala y el espacio entre letras."""
    out, x = [], 0
    for ch in word:
        glyph = FONT[ch]
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell == '#':
                    for dy in range(scale):
                        for dx in range(scale):
                            out.append((x + gx * scale + dx, gy * scale + dy, gy))
        x += len(glyph[0]) * scale + gap
    return out, x - gap


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


big, big_w = word_pixels('NIGHTMARE', 3, 3)
small, small_w = word_pixels('SURVIVAL', 1, 3)
SHADOW = 2
width = max(big_w, small_w) + SHADOW
img = Image.new('RGBA', (width, HEIGHT), (0, 0, 0, 0))

# SURVIVAL: arriba, centrado, gris claro
top = 0
sx = (big_w - small_w) // 2
for x, y, _ in small:
    img.putpixel((sx + x, top + y), (200, 200, 200, 255))

# NIGHTMARE: debajo, rojo que se oscurece hacia abajo, con sombra
by = top + 7 + 2
for x, y, _ in big:
    img.putpixel((x + SHADOW, by + y + SHADOW), (28, 0, 6, 255))
for x, y, _ in big:
    t = y / (7 * 3 - 1)
    img.putpixel((x, by + y), lerp((236, 70, 88), (122, 0, 16), t) + (255,))

tex = os.path.join(ROOT, 'assets', 'terror', 'textures', 'font', 'logo.png')
os.makedirs(os.path.dirname(tex), exist_ok=True)
img.save(tex)

# La fuente por defecto: agrega (o reemplaza) el carácter del logo
font_path = os.path.join(ROOT, 'assets', 'minecraft', 'font', 'default.json')
font = json.load(open(font_path, encoding='utf-8'))
font['providers'] = [p for p in font['providers'] if CHAR not in ''.join(p.get('chars', []))]
font['providers'].append({'type': 'bitmap', 'file': 'terror:font/logo.png', 'ascent': ASCENT, 'height': HEIGHT, 'chars': [CHAR]})
json.dump(font, open(font_path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print(tex, f'{width}x{HEIGHT}')
if len(sys.argv) > 1:
    view = Image.new('RGBA', img.size, (40, 40, 40, 255))
    view.alpha_composite(img)
    view.resize((img.width * 5, img.height * 5), Image.NEAREST).save(sys.argv[1])
