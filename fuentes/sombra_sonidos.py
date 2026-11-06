"""
Los sonidos propios de la Sombra errante: no los usa nada más del server. Baja de Freesound (solo si la página dice
CC0) la vista previa de cada sonido, elige solo los tramos más fuertes de cada uno (lo que se escucha, no los silencios),
los procesa (más graves, apagados, con eco, a veces al revés) y los guarda como .ogg mono, con los eventos en
assets/terror/sounds.json (sombra.*) y los créditos en CREDITOS.md.
Uso: python fuentes/sombra_sonidos.py   (necesita imageio-ffmpeg)
"""
import array, json, math, os, re, shutil, subprocess, urllib.request
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
CACHE = os.path.join(ROOT, 'fuentes', '_cache_sonidos')
OUT = os.path.join(ROOT, 'assets', 'terror', 'sounds', 'sombra')
UA = {'User-Agent': 'Mozilla/5.0'}

SOURCES = {
    423869: 'https://freesound.org/s/423869/',   # Whispers, 'Schizophrenic' or Ghost-like voices (belarathbone)
    193810: 'https://freesound.org/s/193810/',   # Four_Voices_Whispering_3 (geoneo0)
    466871: 'https://freesound.org/s/466871/',   # Calls Beyond Earth (Resaural)
    276577: 'https://freesound.org/s/276577/',   # Dragons Dying Breath (MickBoere)
    518297: 'https://freesound.org/s/518297/',   # High Quality Monster Screech (NaturesTemper)
    457514: 'https://freesound.org/s/457514/',   # Ghost Scare Vintage (onderwish)
    585783: 'https://freesound.org/s/585783/',   # Creepy static fade out into a low hiss (PantherK)
}

GRAVE = 'asetrate=44100*{f},aresample=44100'
# (evento, archivo, fuente, cuántos tramos, duración de cada tramo, filtros)
CLIPS = [
    # Susurros: varias voces a la vez, graves y apagadas, con un eco corto (como en una habitación cerrada)
    ('susurro', 'susurro', 423869, 4, 3.0, GRAVE.format(f=0.78) + ',lowpass=f=2600,aecho=0.8:0.7:60:0.35'),
    ('susurro', 'voces', 193810, 2, 3.0, GRAVE.format(f=0.72) + ',lowpass=f=2400,aecho=0.8:0.75:90:0.4'),
    # Acecho: llamados de algo que no es de acá, muy graves
    ('acecho', 'llamado', 466871, 3, 2.6, GRAVE.format(f=0.55) + ',lowpass=f=1600,aecho=0.8:0.85:180:0.45'),
    # Respiración: un aliento ronco y lento, pegado
    ('respira', 'aliento', 276577, 2, 2.4, GRAVE.format(f=0.5) + ',lowpass=f=900,aecho=0.8:0.6:40:0.3'),
    # Siseo: estática que se apaga (como cuando la luz parpadea), más grave
    ('siseo', 'estatica', 585783, 2, 2.2, GRAVE.format(f=0.75) + ',lowpass=f=3500'),
    # Grito (le pegaste): un chillido grave, con eco largo
    ('grito', 'chillido', 518297, 3, 1.8, GRAVE.format(f=0.7) + ',aecho=0.8:0.8:140:0.4'),
    # Aparece (la primera vez que la ves cerca): el susto fantasmal, al revés y grave (se te viene encima)
    ('aparece', 'aparece', 457514, 2, 2.5, 'areverse,' + GRAVE.format(f=0.7) + ',aecho=0.8:0.85:200:0.5'),
    # Golpe (te muerde): el comienzo del chillido, cortito, muy grave y apagado
    ('golpe', 'golpe', 518297, 2, 0.5, GRAVE.format(f=0.5) + ',lowpass=f=1200,volume=1.6'),
]


def fetch(sound_id):
    """Baja la vista previa si la licencia es CC0. Devuelve (archivo, título, autor, url)."""
    os.makedirs(CACHE, exist_ok=True)
    html = urllib.request.urlopen(urllib.request.Request(SOURCES[sound_id], headers=UA), timeout=30).read().decode('utf-8', 'replace')
    if 'publicdomain/zero' not in html:
        raise SystemExit(f'{sound_id}: no es CC0, no se usa')
    url = re.search(r'https://cdn\.freesound\.org/previews/[^"]+-hq\.mp3', html).group(0)
    title = re.search(r'<title>Freesound - (.*?) by (.*?)</title>', html, re.S)
    path = os.path.join(CACHE, f'{sound_id}.mp3')
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    name = title.group(1).strip().replace('&#x27;', "'")
    return path, name, title.group(2).strip(), canonical.group(1) if canonical else SOURCES[sound_id]


def loudest(path, count, length):
    """Los {count} tramos de {length} segundos con más volumen, sin pisarse (los segundos donde empiezan)."""
    raw = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', '8000', '-'],
                         capture_output=True, check=True).stdout
    data = array.array('h')
    data.frombytes(raw[:len(raw) // 2 * 2])
    step = 800   # una décima
    energy = [math.sqrt(sum(v * v for v in data[i:i + step]) / step) for i in range(0, len(data) - step, step)]
    win = max(1, int(length * 10))
    scores = [(sum(energy[i:i + win]), i) for i in range(0, max(1, len(energy) - win))]
    scores.sort(reverse=True)
    chosen = []
    for _, i in scores:
        if all(abs(i - j) >= win for j in chosen):
            chosen.append(i)
        if len(chosen) == count:
            break
    return [i / 10 for i in sorted(chosen)]


def main():
    sounds_json = os.path.join(ROOT, 'assets', 'terror', 'sounds.json')
    events = json.load(open(sounds_json, encoding='utf-8'))
    for key in [k for k in events if k.startswith('sombra.')]:
        del events[key]
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)
    credits, info = [], {}
    for event, name, sid, count, length, filters in CLIPS:
        if sid not in info:
            info[sid] = fetch(sid)
        src, title, author, url = info[sid]
        starts = [0.0] if event == 'golpe' else loudest(src, count, length)
        if event == 'golpe':   # el ataque del chillido: los primeros instantes fuertes
            starts = loudest(src, count, length)
        for n, start in enumerate(starts, 1):
            out = os.path.join(OUT, f'{name}{n}.ogg')
            af = filters + ',loudnorm=I=-19:TP=-1.5,afade=t=in:d=0.03,areverse,afade=t=in:d=0.3,areverse'
            subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-ss', str(start), '-t', str(length), '-i', src,
                            '-af', af, '-ac', '1', '-ar', '44100', '-c:a', 'libvorbis', '-q:a', '5', out], check=True)
            entry = events.setdefault('sombra.' + event, {'sounds': [], 'subtitle': 'terror.subtitulo.sombra'})
            entry['sounds'].append({'name': f'terror:sombra/{name}{n}'})
            credits.append(f'| `sombra/{name}{n}.ogg` | {title} | {author} | {url} |')
            print(f'sombra.{event}: {name}{n} (desde {start:.1f} s)')
    json.dump(events, open(sounds_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    creditos = os.path.join(ROOT, 'CREDITOS.md')
    lines = [l for l in open(creditos, encoding='utf-8').read().splitlines() if not l.startswith('| `sombra/')]
    open(creditos, 'w', encoding='utf-8').write('\n'.join(lines + credits) + '\n')


main()
