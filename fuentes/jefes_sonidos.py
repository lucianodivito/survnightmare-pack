"""
Sonidos propios de los jefes de las grietas: cada jefe suena distinto y no repite ninguno de los que ya usa el pack.
Baja de Freesound (solo si la página dice CC0) la vista previa de cada sonido, la recorta y la procesa con ffmpeg
(más grave, eco, al revés, más lento...), la guarda como .ogg mono (para que suene desde un lugar), y deja anotados
los eventos en assets/terror/sounds.json y los créditos en CREDITOS.md.
Uso: python fuentes/jefes_sonidos.py   (necesita imageio-ffmpeg: python -m pip install --user imageio-ffmpeg)
"""
import json, os, re, shutil, subprocess, urllib.request
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
    667199: 'https://freesound.org/people/MBPL/sounds/667199/',                  # Crying baby 1
    582341: 'https://freesound.org/people/Mellun/sounds/582341/',                # baby crying in a dark corridor
    872110: 'https://freesound.org/people/SignatureSoundsOrg/sounds/872110/',    # Child Laughing sound Effects-11
    75162: 'https://freesound.org/people/nigelcoop/sounds/75162/',               # crow.wav
    56234: 'https://freesound.org/people/Q.K./sounds/56234/',                    # Crows_02.wav
    565911: 'https://freesound.org/people/Fenodyrie/sounds/565911/',             # flock of crows
    263483: 'https://freesound.org/people/lwdickens/sounds/263483/',             # crow wings flutter
    525268: 'https://freesound.org/people/TheSupremeMuffinPooter/sounds/525268/',  # Dry Grass Rustle
    767220: 'https://freesound.org/people/Wigglesworth/sounds/767220/',          # Rustling grass
    60024: 'https://freesound.org/people/qubodup/sounds/60024/',                 # swosh swinging sword 37
    788990: 'https://freesound.org/people/Robhog/sounds/788990/',                # SWOOSH Sound Effect
    558969: 'https://freesound.org/people/sandb1ns/sounds/558969/',              # Fluorescent Lightbulb Break
    637658: 'https://freesound.org/people/kyles/sounds/637658/',                 # light bulb glass burst
    616615: 'https://freesound.org/people/TRP/sounds/616615/',                   # Footsteps up stone stairs, slow, echo
    447779: 'https://freesound.org/people/Anthousai/sounds/447779/',             # singing wine glass - full 01
    444166: 'https://freesound.org/people/cloe.king/sounds/444166/',             # Wine Glass Ring
    203368: 'https://freesound.org/people/C_Rogers/sounds/203368/',              # glass-shattering-hit_01
    349905: 'https://freesound.org/people/bevibeldesign/sounds/349905/',         # Slow Motion Glass Shatter
    88449: 'https://freesound.org/people/davidou/sounds/88449/',                 # Baleines
    82325: 'https://freesound.org/people/KEVOY/sounds/82325/',                   # Diving with whales
    529383: 'https://freesound.org/people/calebrankin/sounds/529383/',           # Bubbles In Water
    395556: 'https://freesound.org/people/Kinoton/sounds/395556/',               # Single Water Bubbles
    442773: 'https://freesound.org/people/qubodup/sounds/442773/',               # Big Water Splash
    436792: 'https://freesound.org/people/roboroo/sounds/436792/',               # Large Splash
    545823: 'https://freesound.org/people/benj500/sounds/545823/',               # Water Splosh
    587354: 'https://freesound.org/people/Breviceps/sounds/587354/',             # Jumpscare Scream
    725210: 'https://freesound.org/people/zombieallen/sounds/725210/',           # Evil Screech
    580320: 'https://freesound.org/people/SamsterBirdies/sounds/580320/',        # Scary horror terror shriek
    219597: 'https://freesound.org/people/NoraMeld/sounds/219597/',              # HORROR WHISPER VOICE: ANGRY
    316797: 'https://freesound.org/people/dimbark1/sounds/316797/',              # Ghostly Whispers
    554307: 'https://freesound.org/people/casiba842/sounds/554307/',             # Scared Male Heavy Breathing
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
    # Hechos acá (sin grabación): el tarareo grave, el golpe sordo y la muerte. Con la voz grabada y procesada, el
    # murmullo sonaba a perro gruñendo; y el golpe, a puerta.
    ('inquilino.voz', 'voz1', 'tarareo1', 0.0, 3.6, 'lowpass=f=700,aecho=0.8:0.75:90:0.45,afade=t=in:d=0.3,afade=t=out:st=3:d=0.6'),
    ('inquilino.voz', 'voz2', 'tarareo2', 0.0, 3.6, 'lowpass=f=650,aecho=0.8:0.75:120:0.45,afade=t=in:d=0.3,afade=t=out:st=3:d=0.6'),
    ('inquilino.golpe', 'golpe1', 'golpe', 0.0, 0.7, 'lowpass=f=380,volume=2'),
    ('inquilino.muerte', 'muerte1', 'hundirse', 0.0, 6.0, 'lowpass=f=600,aecho=0.8:0.85:160:0.55,afade=t=out:st=3.5:d=2.5'),
    # El Chico
    ('chico.cajita', 'cajita1', 274379, 2.0, 9.0, 'afade=t=in:d=0.5,afade=t=out:st=8:d=1'),
    ('chico.cajita', 'cajita2', 274379, 20.0, 9.0, 'afade=t=in:d=0.5,afade=t=out:st=8:d=1'),
    ('chico.risa', 'risa1', 872110, 0.0, 2.0, 'aecho=0.8:0.7:90:0.4'),
    ('chico.risa', 'risa2', 872110, 0.0, 2.0, GRAVE.format(f=0.85) + ',atempo=0.9,aecho=0.8:0.8:140:0.45'),
    ('chico.risa', 'risa3', 872110, 0.0, 2.0, 'areverse,aecho=0.8:0.7:110:0.4'),
    ('chico.llanto', 'llanto1', 667199, 0.0, 1.6, GRAVE.format(f=1.2) + ',afade=t=out:st=1.2:d=0.4'),
    ('chico.llanto', 'llanto2', 582341, 1.0, 2.0, GRAVE.format(f=1.1) + ',aecho=0.8:0.6:50:0.3,afade=t=out:st=1.5:d=0.5'),
    ('chico.muerte', 'muerte1', 274379, 30.0, 8.0, GRAVE.format(f=0.6) + ',atempo=0.8,aecho=0.8:0.8:150:0.5,afade=t=out:st=5:d=4'),
    # El Espantapájaros
    ('espanta.cuervo', 'cuervo1', 75162, 0.0, 2.5, GRAVE.format(f=0.9) + ',afade=t=out:st=2:d=0.5'),
    ('espanta.cuervo', 'cuervo2', 56234, 0.0, 2.5, GRAVE.format(f=0.85) + ',afade=t=out:st=2:d=0.5'),
    ('espanta.bandada', 'bandada1', 565911, 0.0, 4.0, 'afade=t=in:d=0.3,afade=t=out:st=3:d=1'),
    ('espanta.bandada', 'bandada2', 263483, 0.0, 3.0, 'afade=t=out:st=2.3:d=0.7'),
    ('espanta.paja', 'paja1', 525268, 0.0, 1.2, 'afade=t=out:st=0.9:d=0.3'),
    ('espanta.paja', 'paja2', 767220, 0.0, 1.2, GRAVE.format(f=0.85) + ',afade=t=out:st=0.9:d=0.3'),
    ('espanta.hoz', 'hoz1', 60024, 0.0, 0.8, GRAVE.format(f=0.9)),
    ('espanta.hoz', 'hoz2', 788990, 0.0, 0.8, GRAVE.format(f=0.8)),
    ('espanta.muerte', 'muerte1', 565911, 4.0, 6.0, GRAVE.format(f=0.7) + ',aecho=0.8:0.8:140:0.5,afade=t=out:st=3.5:d=2.5'),
    # El Farolero: casi todo generado (graves, raros); solo el farol que revienta es grabado
    ('caminante.apagon', 'apagon1', 558969, 0.0, 1.2, GRAVE.format(f=0.8) + ',afade=t=out:st=0.9:d=0.3'),
    ('caminante.apagon', 'apagon2', 637658, 0.0, 1.0, GRAVE.format(f=0.75) + ',afade=t=out:st=0.7:d=0.3'),
    ('caminante.paso', 'paso1', 'boom', 0.0, 1.8, 'lowpass=f=300,aecho=0.8:0.9:400:0.4'),
    ('caminante.llega', 'llega1', 'llega', 0.0, 2.6, 'lowpass=f=180,lowpass=f=180,aecho=0.8:0.85:300:0.4'),
    ('caminante.golpe', 'golpe1', 'tajo', 0.0, 0.6, 'lowpass=f=260,lowpass=f=260,volume=2'),
    ('caminante.salto', 'salto1', 'salto', 0.0, 0.7, 'highpass=f=120,lowpass=f=900'),
    # Nadie
    ('loquehay.grito', 'grito1', 587354, 0.0, 2.7, 'volume=1.6'),
    ('loquehay.chillido', 'chillido1', 725210, 0.0, 4.0, GRAVE.format(f=0.85) + ',aecho=0.8:0.8:120:0.4,afade=t=out:st=3.2:d=0.8'),
    # Graves, apagados y con eco largo: lejanos y monstruosos (cerca y nítidos sonaban a ASMR)
    ('loquehay.susurro', 'susurro1', 219597, 0.0, 3.5, GRAVE.format(f=0.6) + ',lowpass=f=1400,aecho=0.8:0.9:350:0.6,afade=t=in:d=0.3,afade=t=out:st=3:d=0.5'),
    ('loquehay.susurro', 'susurro2', 219597, 8.0, 3.5, GRAVE.format(f=0.55) + ',lowpass=f=1200,aecho=0.8:0.9:450:0.6,afade=t=in:d=0.3,afade=t=out:st=3:d=0.5'),
    ('loquehay.susurro', 'susurro3', 316797, 0.0, 4.0, 'areverse,' + GRAVE.format(f=0.6) + ',lowpass=f=1300,aecho=0.8:0.9:400:0.6,afade=t=in:d=0.3,afade=t=out:st=3.4:d=0.6'),
    ('loquehay.respira', 'respira1', 554307, 0.0, 3.0, GRAVE.format(f=0.45) + ',lowpass=f=700,aecho=0.8:0.85:250:0.5,afade=t=out:st=2.5:d=0.5'),
    ('loquehay.golpe', 'golpe1', 'zarpazo', 0.0, 0.7, 'lowpass=f=900'),
    ('loquehay.muerte', 'muerte1', 580320, 0.0, 8.0, GRAVE.format(f=0.6) + ',aecho=0.8:0.9:300:0.5,afade=t=out:st=5:d=3'),
    # El Fondo
    ('abajo.canto', 'canto1', 88449, 0.0, 5.5, GRAVE.format(f=0.7) + ',aecho=0.8:0.85:300:0.45,afade=t=out:st=4.5:d=1'),
    ('abajo.canto', 'canto2', 82325, 10.0, 7.0, GRAVE.format(f=0.75) + ',aecho=0.8:0.85:300:0.45,afade=t=in:d=0.8,afade=t=out:st=6:d=1'),
    ('abajo.burbujas', 'burbujas1', 529383, 0.0, 3.0, 'afade=t=in:d=0.3,afade=t=out:st=2.4:d=0.6'),
    ('abajo.burbujas', 'burbujas2', 395556, 2.0, 3.0, GRAVE.format(f=0.8) + ',afade=t=in:d=0.3,afade=t=out:st=2.4:d=0.6'),
    ('abajo.surge', 'surge1', 442773, 0.0, 2.0, GRAVE.format(f=0.8)),
    ('abajo.surge', 'surge2', 436792, 0.0, 1.8, GRAVE.format(f=0.75)),
    ('abajo.golpe', 'golpe1', 545823, 0.0, 1.5, GRAVE.format(f=0.7) + ',afade=t=out:st=1.1:d=0.4'),
    ('abajo.arrastre', 'arrastre1', 529383, 10.0, 3.0, GRAVE.format(f=0.6) + ',lowpass=f=800,afade=t=in:d=0.3,afade=t=out:st=2.4:d=0.6'),
    ('abajo.muerte', 'muerte1', 88449, 0.0, 5.5, 'areverse,' + GRAVE.format(f=0.55) + ',aecho=0.8:0.9:400:0.5,afade=t=out:st=4:d=1.5'),
    # El Peldañero (tu reflejo)
    ('reflejo.pasos', 'pasos1', 616615, 0.0, 4.0, 'afade=t=in:d=0.3,afade=t=out:st=3.4:d=0.6'),
    ('reflejo.pasos', 'pasos2', 616615, 4.0, 4.0, GRAVE.format(f=0.92) + ',afade=t=in:d=0.3,afade=t=out:st=3.4:d=0.6'),
    ('reflejo.vidrio', 'vidrio1', 447779, 0.5, 3.5, 'afade=t=in:d=0.6,afade=t=out:st=2.8:d=0.7'),
    ('reflejo.vidrio', 'vidrio2', 444166, 0.0, 3.0, GRAVE.format(f=0.8) + ',aecho=0.8:0.8:120:0.4,afade=t=out:st=2.3:d=0.7'),
    ('reflejo.golpe', 'golpe1', 203368, 0.0, 0.8, GRAVE.format(f=0.6) + ',lowpass=f=2500'),
    ('reflejo.cae', 'cae1', 447779, 0.5, 3.0, 'areverse,' + GRAVE.format(f=0.7) + ',aecho=0.8:0.85:180:0.5'),
    ('reflejo.muerte', 'muerte1', 349905, 0.0, 5.0, 'aecho=0.8:0.8:150:0.4,afade=t=out:st=3.5:d=1.5'),
    ('caminante.muerte', 'muerte1', 'caida', 0.0, 5.5, 'lowpass=f=220,lowpass=f=220,aecho=0.8:0.85:250:0.5,afade=t=out:st=3.5:d=2'),
]


# Los generados: una fórmula de onda (ffmpeg aevalsrc). Un tarareo con la voz cerrada (una nota y sus armónicos, con
# un vibrato leve) que baja de nota; un golpe sordo (un bombo grave y un poco de ruido que se apaga enseguida); y un
# tarareo que se hunde hasta perderse.
def hum(notes, seconds):
    step = seconds / len(notes)
    f = '+'.join(f'{n}*between(t,{i * step},{(i + 1) * step})' for i, n in enumerate(notes))
    return (f"aevalsrc='(sin(2*PI*({f})*t*(1+0.006*sin(2*PI*5*t)))+0.45*sin(4*PI*({f})*t)+0.2*sin(6*PI*({f})*t))"
            f"*0.35*(0.7+0.3*sin(2*PI*0.8*t))':s=44100:d={seconds}")


SYNTH = {
    'tarareo1': hum([110, 98, 92.5], 3.6),
    'tarareo2': hum([98, 110, 82.4], 3.6),
    'golpe': "aevalsrc='(0.9*sin(2*PI*52*t)+0.5*(random(0)*2-1)*exp(-t*40))*exp(-t*8)':s=44100:d=0.7",
    'hundirse': "aevalsrc='(sin(2*PI*(110*t-9*t*t))+0.4*sin(4*PI*(110*t-9*t*t)))*0.35':s=44100:d=6",
    'parpado': "aevalsrc='(random(0)*2-1)*exp(-t*40)*0.8+(random(0)*2-1)*exp(-pow((t-0.18)*30,2))*0.5':s=44100:d=0.5",
    'zarpazo': "aevalsrc='(random(0)*2-1)*exp(-pow((t-0.08)*18,2))*0.9+(random(0)*2-1)*exp(-t*9)*0.5*between(t,0.12,0.7)':s=44100:d=0.7",
    'boom': "aevalsrc='(sin(2*PI*38*t)+0.6*sin(2*PI*57*t)+0.3*(random(0)*2-1)*exp(-t*12))*exp(-t*2.5)*0.6':s=44100:d=1.8",
    'llega': "aevalsrc='(random(0)*2-1)*pow(min(1,t/2.2),2)*0.8*if(lt(t,2.25),1,exp(-(t-2.25)*12))':s=44100:d=2.6",
    'tajo': "aevalsrc='(random(0)*2-1)*exp(-t*14)*0.9':s=44100:d=0.6",
    'salto': "aevalsrc='(random(0)*2-1)*pow(t/0.7,3)*0.5':s=44100:d=0.7",
    'caida': "aevalsrc='(random(0)*2-1)*(0.5+0.5*sin(2*PI*3*t)*sin(2*PI*1.3*t))*exp(-t*0.6)*0.8':s=44100:d=5.5",
}


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
    bosses = {e.split('.')[0] for e, *_ in CLIPS}
    # Los de los jefes se arman de cero cada vez (si se cambia uno, no queda el viejo colgado)
    for key in [k for k in events if k.split('.')[0] in bosses]:
        del events[key]
    out_dir = os.path.join(ROOT, 'assets', 'terror', 'sounds', 'jefes')
    shutil.rmtree(out_dir, ignore_errors=True)
    credits = []
    info = {}
    for event, name, sid, start, length, filters in CLIPS:
        boss = event.split('.')[0]
        os.makedirs(os.path.join(out_dir, boss), exist_ok=True)
        out = os.path.join(out_dir, boss, name + '.ogg')
        filters += ',loudnorm=I=-20:TP=-1.5'   # todos con un volumen parejo
        if sid in SYNTH:
            source = ['-f', 'lavfi', '-i', SYNTH[sid]]
        else:
            if sid not in info:
                info[sid] = fetch(sid)
            src, title, author, url = info[sid]
            source = ['-ss', str(start), '-t', str(length), '-i', src]
            credits.append(f'| `jefes/{boss}/{name}.ogg` | {title} | {author} | {url} |')
        cmd = [FFMPEG, '-y', '-loglevel', 'error', *source,
               '-af', filters, '-ac', '1', '-ar', '44100', '-c:a', 'libvorbis', '-q:a', '5', out]
        subprocess.run(cmd, check=True)
        entry = events.setdefault(event, {'sounds': [], 'subtitle': 'terror.subtitulo.' + event})
        entry['sounds'].append({'name': f'terror:jefes/{boss}/{name}'})
        print(out)
    json.dump(events, open(sounds_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    # Créditos: se reescriben las filas de los jefes (los generados no llevan)
    creditos = os.path.join(ROOT, 'CREDITOS.md')
    lines = [l for l in open(creditos, encoding='utf-8').read().splitlines() if not l.startswith('| `jefes/')]
    open(creditos, 'w', encoding='utf-8').write('\n'.join(lines + credits) + '\n')


main()
