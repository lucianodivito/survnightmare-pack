"""
Sonidos propios de los jefes de las grietas: cada jefe suena distinto y no repite ninguno de los que ya usa el pack.
Baja de Freesound (solo si la página dice CC0) la vista previa de cada sonido, la recorta y la procesa con ffmpeg
(más grave, eco, al revés, más lento...), la guarda como .ogg mono (para que suene desde un lugar), y deja anotados
los eventos en assets/terror/sounds.json y los créditos en CREDITOS.md.
Uso: python fuentes/jefes_sonidos.py   (necesita imageio-ffmpeg: python -m pip install --user imageio-ffmpeg)
"""
import json, os, re, subprocess, urllib.request
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
CACHE = os.path.join(ROOT, 'fuentes', '_cache_sonidos')
UA = {'User-Agent': 'Mozilla/5.0'}

# Fuentes: id de Freesound -> página
SOURCES = {
    346267: 'https://freesound.org/s/346267/',                                    # stib, Door Creak
    502504: 'https://freesound.org/people/Rudmer_Rotteveel/sounds/502504/',      # Wood Creak Single V2
    506660: 'https://freesound.org/people/Rudmer_Rotteveel/sounds/506660/',      # Wood Creak Single V5
    232447: 'https://freesound.org/people/mmaruska/sounds/232447/',              # Lights Flicker On
    157564: 'https://freesound.org/people/husky70/sounds/157564/',               # Grumpy Old Man
    274379: 'https://freesound.org/people/Modification1089/sounds/274379/',      # creepy music box
    397333: 'https://freesound.org/people/Splushionsindasky/sounds/397333/',     # barefoot hall running
    667199: 'https://freesound.org/people/MBPL/sounds/667199/',                  # Crying baby 1
    582341: 'https://freesound.org/people/Mellun/sounds/582341/',                # baby crying in a dark corridor
    872110: 'https://freesound.org/people/SignatureSoundsOrg/sounds/872110/',    # Child Laughing sound Effects-11
}

# Cada sonido: (evento, archivo, id de fuente, desde, duración, filtros de ffmpeg)
GRAVE = 'asetrate=44100*{f},aresample=44100'
CLIPS = [
    # El Inquilino
    ('inquilino.puerta', 'puerta1', 346267, 0.0, 3.0, 'volume=1.4'),
    ('inquilino.puerta', 'puerta2', 346267, 3.0, 3.0, GRAVE.format(f=0.85) + ',volume=1.4'),
    ('inquilino.paso', 'paso1', 502504, 0.0, 1.0, GRAVE.format(f=0.8)),
    ('inquilino.paso', 'paso2', 506660, 0.0, 1.0, GRAVE.format(f=0.75)),
    ('inquilino.parpadeo', 'parpadeo1', 232447, 0.0, 2.2, 'volume=1.3'),
    ('inquilino.voz', 'voz1', 157564, 0.0, 4.0, GRAVE.format(f=0.7) + ',aecho=0.8:0.7:60:0.4'),
    ('inquilino.voz', 'voz2', 157564, 4.0, 4.0, GRAVE.format(f=0.65) + ',aecho=0.8:0.7:80:0.4'),
    ('inquilino.golpe', 'golpe1', 346267, 6.0, 1.2, GRAVE.format(f=0.5) + ',volume=2'),
    ('inquilino.muerte', 'muerte1', 157564, 0.0, 6.0, 'areverse,' + GRAVE.format(f=0.55) + ',aecho=0.8:0.8:120:0.5,afade=t=out:st=4:d=2'),
    # El Chico
    ('chico.cajita', 'cajita1', 274379, 2.0, 9.0, 'afade=t=in:d=0.5,afade=t=out:st=8:d=1'),
    ('chico.cajita', 'cajita2', 274379, 20.0, 9.0, 'afade=t=in:d=0.5,afade=t=out:st=8:d=1'),
    ('chico.corre', 'corre1', 397333, 0.0, 3.0, GRAVE.format(f=1.15)),
    ('chico.risa', 'risa1', 872110, 0.0, 2.0, 'aecho=0.8:0.7:90:0.4'),
    ('chico.risa', 'risa2', 872110, 0.0, 2.0, GRAVE.format(f=0.85) + ',atempo=0.9,aecho=0.8:0.8:140:0.45'),
    ('chico.risa', 'risa3', 872110, 0.0, 2.0, 'areverse,aecho=0.8:0.7:110:0.4'),
    ('chico.llanto', 'llanto1', 667199, 0.0, 1.6, GRAVE.format(f=1.2) + ',afade=t=out:st=1.2:d=0.4'),
    ('chico.llanto', 'llanto2', 582341, 1.0, 2.0, GRAVE.format(f=1.1) + ',aecho=0.8:0.6:50:0.3,afade=t=out:st=1.5:d=0.5'),
    ('chico.muerte', 'muerte1', 274379, 30.0, 8.0, GRAVE.format(f=0.6) + ',atempo=0.8,aecho=0.8:0.8:150:0.5,afade=t=out:st=5:d=4'),
]


def page(sound_id):
    req = urllib.request.Request(SOURCES[sound_id], headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')


def fetch(sound_id):
    """Baja la vista previa si la licencia es CC0. Devuelve (archivo, título, autor, url de la página)."""
    os.makedirs(CACHE, exist_ok=True)
    html = page(sound_id)
    if 'publicdomain/zero' not in html:
        raise SystemExit(f'{sound_id}: no es CC0, no se usa')
    url = re.search(r'https://cdn\.freesound\.org/previews/[^"]+-hq\.mp3', html).group(0)
    title = re.search(r'<title>Freesound - (.*?) by (.*?)</title>', html, re.S)
    path = os.path.join(CACHE, f'{sound_id}.mp3')
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    return path, title.group(1).strip(), title.group(2).strip(), canonical.group(1) if canonical else SOURCES[sound_id]


def main():
    sounds_json = os.path.join(ROOT, 'assets', 'terror', 'sounds.json')
    events = json.load(open(sounds_json, encoding='utf-8'))
    credits = []
    info = {}
    out_dir = os.path.join(ROOT, 'assets', 'terror', 'sounds', 'jefes')
    os.makedirs(out_dir, exist_ok=True)
    for event, name, sid, start, length, filters in CLIPS:
        if sid not in info:
            info[sid] = fetch(sid)
        src, title, author, url = info[sid]
        boss = event.split('.')[0]
        os.makedirs(os.path.join(out_dir, boss), exist_ok=True)
        out = os.path.join(out_dir, boss, name + '.ogg')
        filters += ',loudnorm=I=-20:TP=-1.5'   # todos con un volumen parejo
        cmd = [FFMPEG, '-y', '-loglevel', 'error', '-ss', str(start), '-t', str(length), '-i', src,
               '-af', filters, '-ac', '1', '-ar', '44100', '-c:a', 'libvorbis', '-q:a', '5', out]
        subprocess.run(cmd, check=True)
        entry = events.setdefault(event, {'sounds': [], 'subtitle': 'terror.subtitulo.' + event})
        ref = f'terror:jefes/{boss}/{name}'
        if all(s['name'] != ref for s in entry['sounds']):
            entry['sounds'].append({'name': ref})
        credits.append(f'| `jefes/{boss}/{name}.ogg` | {title} | {author} | {url} |')
        print(out)
    json.dump(events, open(sounds_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    creditos = os.path.join(ROOT, 'CREDITOS.md')
    text = open(creditos, encoding='utf-8').read()
    new = [c for c in credits if c.split('|')[1].strip() not in text]
    if new:
        open(creditos, 'a', encoding='utf-8').write('\n'.join(new) + '\n')


main()
