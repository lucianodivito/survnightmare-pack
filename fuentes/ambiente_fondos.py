"""
Fondos que suenan sin cortes mientras dura un clima: el viento de la niebla y el rumor de la Luna de Sangre.
Se arman de cero con ffmpeg (ruido y tonos filtrados; no se baja nada). Cada archivo dura DURACION segundos, entra
y sale con un fundido de igual potencia (qsin), y el plugin pone el siguiente antes de que termine el anterior: los
dos se cruzan durante el fundido y nunca se nota dónde empieza uno y termina el otro. Hay varias versiones de cada
uno (ráfagas y tonos distintos) para que no se repita. En estéreo: así Minecraft no los ubica en un lugar, se oyen
alrededor, como la música.
Salida: assets/terror/sounds/ambiente/*.ogg y los eventos ambiente.viento y ambiente.luna en sounds.json.
Uso: python fuentes/ambiente_fondos.py   (necesita imageio-ffmpeg)
"""
import array, json, math, os, subprocess
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUT = os.path.join(ROOT, 'assets', 'terror', 'sounds', 'ambiente')
DURACION = 24      # segundos de cada archivo (el plugin los pone cada DURACION - FUNDIDO)
FUNDIDO = 4
RATE = 32000


def wind(seed, rates, whistle):
    """Viento: un fondo grave de ruido marrón con ráfagas lentas, un silbido medio y uno agudo que van y vienen,
    cada uno con su propio ritmo (se cruzan y las ráfagas nunca caen igual)."""
    a, b, c = rates
    gust = f"0.72+0.28*sin(2*PI*t*{a})*sin(2*PI*t*{b}+1.3)"
    hiss = f"0.5+0.5*pow(sin(2*PI*t*{c}+0.4),2)"
    whine = f"0.3+0.7*pow(sin(2*PI*t*{b}*0.7+2.1),4)"
    chans = []
    for ch in range(2):
        s = seed * 10 + ch
        chans.append(
            f"anoisesrc=d={DURACION}:c=brown:r={RATE}:a=0.9:s={s},lowpass=f=420,highpass=f=60,volume='{gust}':eval=frame[g{ch}];"
            f"anoisesrc=d={DURACION}:c=pink:r={RATE}:a=0.5:s={s + 3},bandpass=f={whistle}:width_type=q:w=1.4,volume='{hiss}':eval=frame[h{ch}];"
            f"anoisesrc=d={DURACION}:c=white:r={RATE}:a=0.3:s={s + 7},bandpass=f={whistle * 2.3:.0f}:width_type=q:w=6,volume='{whine}':eval=frame[w{ch}];"
            f"[g{ch}][h{ch}][w{ch}]amix=inputs=3:weights=1 0.55 0.18:normalize=0[c{ch}];")
    return ''.join(chans)


def moon(seed, root, beat):
    """Luna de Sangre: un zumbido grave que late despacio (dos tonos casi iguales), una quinta disonante que aparece
    y se va, retumbo de tierra y un coro hueco (ruido por un filtro muy angosto) que crece y se apaga."""
    swell = f"0.55+0.45*pow(sin(2*PI*t*{0.045 + seed * 0.01:.3f}+{seed}),2)"
    choir = f"0.45+0.55*pow(sin(2*PI*t*{0.06 + seed * 0.013:.3f}+{seed * 2}),4)"
    chans = []
    for ch in range(2):
        s = seed * 10 + ch
        det = 0.15 * ch
        chans.append(
            f"sine=f={root}:r={RATE}:d={DURACION}[s1{ch}];sine=f={root + beat + det}:r={RATE}:d={DURACION}[s2{ch}];"
            f"sine=f={root * 2}:r={RATE}:d={DURACION}[s3{ch}];sine=f={root * 3 + det}:r={RATE}:d={DURACION}[s5{ch}];"
            f"sine=f={root * 1.41:.2f}:r={RATE}:d={DURACION},volume='{swell}':eval=frame[s4{ch}];"
            f"anoisesrc=d={DURACION}:c=brown:r={RATE}:a=0.8:s={s},lowpass=f=140,volume='{swell}':eval=frame[n{ch}];"
            f"anoisesrc=d={DURACION}:c=pink:r={RATE}:a=0.6:s={s + 5},bandpass=f={root * 8 + ch * 3}:width_type=q:w=40,"
            f"bandpass=f={root * 8 + ch * 3}:width_type=q:w=40,volume='{choir}':eval=frame[k{ch}];"
            f"anoisesrc=d={DURACION}:c=pink:r={RATE}:a=0.6:s={s + 8},bandpass=f={root * 5 + ch * 2}:width_type=q:w=30,"
            f"bandpass=f={root * 5 + ch * 2}:width_type=q:w=30,volume='{swell}':eval=frame[q{ch}];"
            f"[s1{ch}][s2{ch}][s3{ch}][s4{ch}][s5{ch}][n{ch}][k{ch}][q{ch}]amix=inputs=8:weights=0.30 0.30 0.22 0.12 0.10 0.7 1.6 1.3:normalize=0[c{ch}];")
    return ''.join(chans)


def render(graph, name, gain):
    path = os.path.join(OUT, name + '.ogg')
    # Fuerte y parejo (como los sonidos del juego): normalizado a -14 LUFS antes de los fundidos
    tail = (f"[c0][c1]join=inputs=2:channel_layout=stereo,volume={gain},loudnorm=I=-14:TP=-1.5:LRA=6,aresample={RATE},"
            f"afade=t=in:d={FUNDIDO}:curve=qsin,afade=t=out:st={DURACION - FUNDIDO}:d={FUNDIDO}:curve=qsin,"
            f"alimiter=limit=0.9[out]")
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-filter_complex', graph + tail, '-map', '[out]',
                    '-c:a', 'libvorbis', '-q:a', '3', path], check=True)
    return path


def level(path):
    """Nivel (RMS, de 0 a 1) cada segundo, para revisar que no haya saltos ni silencios."""
    raw = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', '8000', '-'],
                         capture_output=True, check=True).stdout
    data = array.array('h')
    data.frombytes(raw[:len(raw) // 2 * 2])
    out = []
    for i in range(0, len(data) - 8000 + 1, 8000):
        part = data[i:i + 8000]
        out.append(math.sqrt(sum(v * v for v in part) / len(part)) / 32768)
    return out


os.makedirs(OUT, exist_ok=True)
FILES = {
    'viento1': (wind(1, (0.031, 0.083, 0.11), 520), 1.6),
    'viento2': (wind(2, (0.043, 0.067, 0.09), 610), 2.4),
    'viento3': (wind(3, (0.025, 0.097, 0.13), 450), 1.6),
    'luna1': (moon(1, 73.4, 0.55), 1.1),
    'luna2': (moon(2, 65.4, 0.7), 1.1),
}
for name, (graph, gain) in FILES.items():
    path = render(graph, name, gain)
    lv = level(path)
    mid = lv[FUNDIDO:len(lv) - FUNDIDO]
    print(f"{name}: {os.path.getsize(path) // 1024} KB  medio {sum(mid) / len(mid):.3f}  min {min(mid):.3f}  max {max(mid):.3f}  "
          + ' '.join(f"{v:.2f}" for v in lv))

sj = os.path.join(ROOT, 'assets', 'terror', 'sounds.json')
events = json.load(open(sj, encoding='utf-8'))
events['ambiente.viento'] = {'sounds': [{'name': f'terror:ambiente/viento{i}', 'stream': True} for i in (1, 2, 3)]}
events['ambiente.luna'] = {'sounds': [{'name': f'terror:ambiente/luna{i}', 'stream': True} for i in (1, 2)]}
json.dump(events, open(sj, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('sounds.json listo')
