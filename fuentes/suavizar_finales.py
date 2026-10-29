"""
Busca los sonidos del pack que terminan de golpe (todavía con volumen en las últimas centésimas) y les pone un fundido
al final, en el mismo archivo. Los que ya terminan en silencio no se tocan, así que se puede correr las veces que haga
falta. Uso: python fuentes/suavizar_finales.py [--revisar]   (--revisar: solo lista, no cambia nada)
"""
import array, math, os, subprocess, sys
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS = os.path.join(ROOT, 'assets', 'terror', 'sounds')
TAIL = 0.05       # segundos del final que se miden
ABRUPT = 0.03     # si el final todavía suena más que esto (respecto del máximo del sonido), está cortado
FADE_OUT = 0.35


def samples(path):
    raw = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', '22050', '-'],
                         capture_output=True, check=True).stdout
    data = array.array('h')
    data.frombytes(raw[:len(raw) // 2 * 2])
    return data


def abrupt(path):
    data = samples(path)
    if not data:
        return False, 0
    peak = max(abs(v) for v in data) or 1
    tail = data[-max(1, int(22050 * TAIL)):]
    rms = math.sqrt(sum(v * v for v in tail) / len(tail))
    return rms / peak > ABRUPT, rms / peak


def soften(path):
    tmp = path + '.tmp.ogg'
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', path,
                    '-af', 'afade=t=in:d=0.02,areverse,afade=t=in:d=' + str(FADE_OUT) + ',areverse',
                    '-c:a', 'libvorbis', '-q:a', '5', tmp], check=True)
    os.replace(tmp, path)


only_check = '--revisar' in sys.argv
fixed = 0
for folder, _, files in os.walk(SOUNDS):
    if os.path.relpath(folder, SOUNDS).split(os.sep)[0] == 'jefes':
        continue   # esos ya salen con fundido de jefes_sonidos.py
    for name in sorted(files):
        if not name.endswith('.ogg'):
            continue
        path = os.path.join(folder, name)
        cut, level = abrupt(path)
        if not cut:
            continue
        print(('cortado ' if only_check else 'suavizado ') + os.path.relpath(path, SOUNDS) + f'  (final al {level:.0%})')
        if not only_check:
            soften(path)
        fixed += 1
print(f'{fixed} sonidos ' + ('cortados' if only_check else 'suavizados'))
