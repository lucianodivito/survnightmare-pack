"""
Empaqueta el resource pack en dist/SurvNightmare.zip y muestra su SHA-1.
Con --config, además escribe el SHA-1 en las configs del plugin (resource-pack.sha1).
Uso: python build.py [--config]
"""
import hashlib, io, os, re, sys, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'dist', 'SurvNightmare.zip')
CONFIGS = [r'D:\Servers\SurvivalHorror\plugins\Terror\config.yml', r'D:\Servers\_prueba\plugins\Terror\config.yml']
SKIP = {'dist', '.git', 'build.py', 'README.md', '.gitignore', 'fuentes'}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for base, dirs, files in os.walk(ROOT):
        rel = os.path.relpath(base, ROOT)
        top = rel.split(os.sep)[0]
        if top in SKIP:
            dirs[:] = []
            continue
        dirs.sort()
        for name in sorted(files):
            if rel == '.' and name in SKIP:
                continue
            path = os.path.join(base, name)
            arc = os.path.relpath(path, ROOT).replace(os.sep, '/')
            info = zipfile.ZipInfo(arc, date_time=(2020, 1, 1, 0, 0, 0))   # fecha fija: mismo contenido, mismo SHA-1
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(path, 'rb') as f:
                z.writestr(info, f.read())

sha1 = hashlib.sha1(open(OUT, 'rb').read()).hexdigest()
print(OUT)
print('sha1:', sha1)
if '--config' in sys.argv:
    for c in CONFIGS:
        if not os.path.exists(c):
            continue
        t = io.open(c, encoding='utf-8').read()
        t2 = re.sub(r'(?m)^(  sha1: )"[0-9a-f]*"', r'\g<1>"' + sha1 + '"', t)
        if t2 != t:
            io.open(c, 'w', encoding='utf-8', newline='').write(t2)
            print('config:', c)
