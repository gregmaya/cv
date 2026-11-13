"""Convierte un export de GoatCounter (zip) en dos JSON para el dashboard del CV.

Uso: python3 procesar_export.py <export.zip> <carpeta_salida>

hits.json          una fila por (código, tipo de evento, hora UTC): cuántas visitas o clics
dispositivos.json  una fila por (código, día, dimensión, valor): sistema, navegador, pantalla, país, idioma
"""
import json, sys, zipfile, re
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
code_text = Path(__file__).read_text()

z = zipfile.ZipFile(src)
def jl(name):
    f = [n for n in z.namelist() if n.endswith('/' + name) or n == name][0]
    return [json.loads(l) for l in z.read(f).decode().splitlines() if l.strip()]

paths = {p['id']: p for p in jl('paths.jsonl')}
systems = {s['id']: f"{s['name']} {s['version']}".strip() for s in jl('systems.jsonl')}
browsers = {b['id']: f"{b['name']} {b['version']}".strip() for b in jl('browsers.jsonl')}
locations = {(l['country'], l['region']): l for l in jl('locations.jsonl')}

def parse(path):
    """'/cv/r/k7' -> ('visita','k7'); 'pdf/r/ep' -> ('pdf','ep'); '/cv/sin-codigo' -> ('visita','(sin código)')"""
    p = path.strip('/')
    m = re.match(r'^d/([a-z0-9_.-]+)/([a-z0-9_-]+)$', p)   # huella de una apertura: d/<código>/<so>-<nav>-<ancho>-<idioma>-<zona>
    if m:
        return 'huella', ('(sin código)' if m.group(1) == 'sin-codigo' else m.group(1)) + '|' + m.group(2)
    if p == 'cv/sin-codigo':
        return 'visita', '(sin código)'
    m = re.match(r'^(cv|pdf|whatsapp|email|linkedin|github|share|healthy-transport|zpae)/r/([a-z0-9_.-]+)$', p)
    if not m:
        m2 = re.match(r'^(pdf|whatsapp|email|linkedin|github|share|healthy-transport|zpae)/sin-codigo$', p)
        return (m2.group(1), '(sin código)') if m2 else (None, None)
    tipo = 'visita' if m.group(1) == 'cv' else m.group(1)
    return tipo, m.group(2)

hits = []
for h in jl('hit_stats.jsonl'):
    tipo, code = parse(paths[h['path_id']]['path'])
    if tipo == 'huella':
        code, hu = code.split('|')
        so, nav, ancho, idioma, zona = (hu.split('-') + ['?'] * 5)[:5]
        hits.append({'codigo': code, 'tipo': 'huella', 'hora_utc': h['hour'], 'n': h['count'],
                     'so': so, 'navegador': nav, 'pantalla': ancho, 'idioma': idioma, 'zona': zona})
    elif tipo:
        hits.append({'codigo': code, 'tipo': tipo, 'hora_utc': h['hour'], 'n': h['count']})

disp = []
dims = [('system_stats.jsonl', 'sistema', lambda r: systems.get(r['system_id'], '?')),
        ('browser_stats.jsonl', 'navegador', lambda r: browsers.get(r['browser_id'], '?')),
        ('size_stats.jsonl', 'pantalla', lambda r: str(r['width'])),
        ('location_stats.jsonl', 'pais', lambda r: r['location']),
        ('language_stats.jsonl', 'idioma', lambda r: r['language'])]
for fname, dim, val in dims:
    for r in jl(fname):
        tipo, code = parse(paths[r['path_id']]['path'])
        if tipo == 'visita':
            disp.append({'codigo': code, 'dia': r['day'], 'dimension': dim, 'valor': val(r), 'n': r['count']})

info = json.loads(z.read([n for n in z.namelist() if n.endswith('info.json')][0]))
meta = [{'label': 'procesar_export.py', 'value': code_text, 'type': 'code', 'lang': 'python'},
        {'label': 'Input', 'value': src.name},
        {'label': 'Export creado', 'value': info.get('created_at', '')}]
(out / 'hits.json').write_text(json.dumps({'rows': sorted(hits, key=lambda r: r['hora_utc']), 'meta': meta}, ensure_ascii=False))
(out / 'dispositivos.json').write_text(json.dumps({'rows': disp, 'meta': meta}, ensure_ascii=False))
print(len(hits), 'hits ·', len(disp), 'filas de dispositivo')
