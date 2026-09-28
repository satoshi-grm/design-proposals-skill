#!/usr/bin/env python3
"""Arma un cuadernillo de propuestas visuales desde <carpeta>/fuente/propuesta.json.

Pasos (todos o por partes con --solo):
  temas      tokens de cada dirección → fuente/.build/temas.css y <dir>/tokens.css (CSS + Tailwind v4 + shadcn)
  pantallas  cada pantalla × dirección → HTML a tamaño real → PNG 2x con Chrome headless (pantallas/)
  catalogo   la biblioteca de componentes con el tema de cada dirección → pantallas/<dir>-componentes.png
  limites    texto mínimo (12 px; 28 px en TV), scroll horizontal y recortes medidos en Chrome → limites.txt
  contraste  pares WCAG por dirección y modo → contraste.txt (sale con 1 si algo no cumple)
  docs       <dir>/design.md por dirección
  pdf        cuadernillo 16:9 → propuestas.html y propuestas.pdf
  galeria    index.html navegable con filtro por dirección
  revision   hojas de contacto de todas las páginas del PDF en revision/ para mirarlas con visión

Uso: build.py <carpeta> [--solo temas,pantallas] [--dir mesa] [--pantalla editor]
"""
import argparse
import concurrent.futures as cf
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True  # nada de __pycache__ dentro de la skill
AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from contraste import contraste  # noqa: E402

SKILL_NOMBRE = os.path.basename(SKILL)
LUCIDE = None  # lo resuelve main() con lucide_dir()
ORDEN_COMPONENTES = ['base.css', 'shell.css', 'tabla.css', 'overlays.css', 'formularios.css', 'estados.css', 'paginas.css', 'graficos.css']


def chrome():
    import glob
    playwright = sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-*/chrome')), reverse=True)
    for c in (os.environ.get('CHROME'), shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser'), *playwright):
        if c:
            return c
    sys.exit('No encontré Chrome/Chromium. Instalá Google Chrome o Chromium del sistema, o el de Playwright '
             '(python3 -m playwright install chromium), y si queda fuera del PATH definí CHROME=/ruta/al/binario '
             '(o SHOT_CHROME para chrome-headless-shell).')


def headless_shell():
    """chrome-headless-shell respeta el viewport exacto; Chrome con --headless=new le resta ~87 px de alto."""
    import glob
    for c in [os.environ.get('SHOT_CHROME')] + sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell')), reverse=True) + [shutil.which('chrome-headless-shell')]:
        if c and os.path.exists(c):
            return c
    return None


def correr_chrome(args, binario=None):
    perfil = tempfile.mkdtemp(prefix='pv-')
    try:
        cmd = [binario] if binario else [chrome(), '--headless=new']
        subprocess.run([*cmd, '--no-sandbox', '--disable-gpu', f'--user-data-dir={perfil}',
                        '--hide-scrollbars', '--run-all-compositor-stages-before-draw', *args],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    finally:
        shutil.rmtree(perfil, ignore_errors=True)


def captura(html_path, png, ancho, alto, escala=2):
    shell = headless_shell()
    if not shell:  # respaldo: ventana más alta para compensar la barra que resta --headless=new
        alto += 87
    correr_chrome([f'--window-size={ancho},{alto}', f'--force-device-scale-factor={escala}',
                   '--virtual-time-budget=6000', f'--screenshot={png}', 'file://' + html_path], shell)
    return png


def imprimir_pdf(html_path, pdf):
    correr_chrome(['--virtual-time-budget=20000', '--no-pdf-header-footer', f'--print-to-pdf={pdf}', 'file://' + html_path])


# ---------------------------------------------------------------- íconos
_cache_iconos = {}
_avisos = set()


def lucide_dir(carpeta):
    """LUCIDE_DIR → <cuadernillo>/node_modules → <cuadernillo>/../node_modules; None si no hay ninguno."""
    for c in (os.environ.get('LUCIDE_DIR'), os.path.join(carpeta, 'node_modules/lucide-static/icons'),
              os.path.join(os.path.dirname(carpeta), 'node_modules/lucide-static/icons')):
        if c and os.path.isdir(c):
            return c
    return None


def icono(nombre, clase, carpeta_iconos):
    if nombre not in _cache_iconos:
        local = os.path.join(carpeta_iconos, nombre + '.svg')
        if not os.path.exists(local):
            origen = os.path.join(LUCIDE, nombre + '.svg') if LUCIDE else ''
            if not os.path.exists(origen):
                if not LUCIDE and 'lucide' not in _avisos:
                    _avisos.add('lucide')
                    print('  aviso: sin íconos Lucide. Instalalos con «npm i lucide-static» en la carpeta del cuadernillo '
                          '(o definí LUCIDE_DIR=.../lucide-static/icons); sigo sin íconos.')
                elif LUCIDE and nombre not in _avisos:
                    _avisos.add(nombre)
                    print(f'  aviso: no existe el ícono «{nombre}» en Lucide; va vacío.')
                return ''
            os.makedirs(carpeta_iconos, exist_ok=True)
            shutil.copy(origen, local)
        svg = open(local).read()
        svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S).strip()
        svg = re.sub(r'\s(class|width|height)="[^"]*"', '', svg, count=3)
        _cache_iconos[nombre] = svg
    svg = _cache_iconos[nombre]
    return svg.replace('<svg', f'<svg class="i {clase}" aria-hidden="true"', 1)


def expandir_iconos(texto, carpeta_iconos):
    def rep(m):
        nombre, _, clase = m.group(1).partition('|')
        return icono(nombre, clase, carpeta_iconos)
    return re.sub(r'\{i:([\w-]+(?:\|[\w-]+)?)\}', rep, texto)


# ---------------------------------------------------------------- temas
def css_vars(tokens, sangria='  '):
    return '\n'.join(f'{sangria}--{k}: {v};' for k, v in tokens.items())


def temas_css(props):
    partes = []
    for d in props['direcciones']:
        partes.append(f'[data-theme="{d["id"]}"] {{\n{css_vars(d["tokens"]["light"])}\n}}')
        partes.append(f'[data-theme="{d["id"]}"][data-mode="dark"] {{\n{css_vars(d["tokens"]["dark"])}\n}}')
    return '\n'.join(partes) + '\n'


COLORES_SHADCN = ['background', 'foreground', 'card', 'card-foreground', 'popover', 'popover-foreground', 'primary',
                  'primary-foreground', 'secondary', 'secondary-foreground', 'muted', 'muted-foreground', 'accent',
                  'accent-foreground', 'destructive', 'destructive-foreground', 'border', 'input', 'ring', 'chart-1',
                  'chart-2', 'chart-3', 'chart-4', 'chart-5', 'sidebar', 'sidebar-foreground', 'sidebar-primary',
                  'sidebar-primary-foreground', 'sidebar-accent', 'sidebar-accent-foreground', 'sidebar-border', 'sidebar-ring']


def completar_shadcn(t):
    """Los tokens del contrato + los que shadcn espera y el contrato deriva."""
    t = dict(t)
    for k, v in {'card-foreground': 'foreground', 'popover-foreground': 'foreground', 'secondary': 'muted',
                 'secondary-foreground': 'foreground', 'accent': 'muted', 'accent-foreground': 'foreground',
                 'ring': 'accent-ink', 'sidebar-primary': 'primary', 'sidebar-primary-foreground': 'primary-foreground',
                 'sidebar-ring': 'accent-ink', 'popover': 'card', 'destructive-foreground': None}.items():
        if k not in t:
            t[k] = t.get(v, '#ffffff') if v else '#ffffff'
    return t


def tokens_proyecto(d):
    """tokens.css listo para pegar en un proyecto con shadcn/ui y Tailwind v4."""
    luz, osc = completar_shadcn(d['tokens']['light']), completar_shadcn(d['tokens']['dark'])
    colores = [k for k in luz if not k.startswith(('font-', 'text-', 'radius', 'control-', 'row-', 'gap', 'pad', 'shadow', 'ease', 'dur-', 'display-', 'border-width'))]
    otros = [k for k in luz if k not in colores]
    lineas = [f'/* {d["nombre"]} · tokens para shadcn/ui + Tailwind v4. Generado por {SKILL_NOMBRE}/build.py */',
              f'/* Fuentes: {", ".join(d.get("fuentes", []))} (Google Fonts, OFL) */', '',
              ':root {', css_vars({k: luz[k] for k in colores + otros}), '}', '',
              '.dark {', css_vars({k: osc[k] for k in colores if k in osc}), '}', '',
              '@theme inline {']
    for k in colores:
        lineas.append(f'  --color-{k}: var(--{k});')
    lineas += ['  --font-sans: var(--font-sans);', '  --font-display: var(--font-display);', '  --font-mono: var(--font-mono);',
               '  --radius-sm: var(--radius-sm);', '  --radius-md: var(--radius);', '  --radius-lg: var(--radius-lg);',
               '  --shadow-float: var(--shadow-float);', '  --ease-out: var(--ease-out);', '}', '']
    return '\n'.join(lineas)


# ---------------------------------------------------------------- pantallas
def head_html(carpeta, d, extra_css=(), props=None):
    props = props or {}
    f = os.path.join(carpeta, 'fuente')
    rel = lambda p: os.path.relpath(p, os.path.join(f, '.build'))  # noqa: E731
    hojas = [os.path.join(f, 'assets/fuentes/fuentes.css')]
    comp = os.path.join(f, 'componentes')
    usar = props.get('componentes_pantallas', ORDEN_COMPONENTES)
    hojas += [os.path.join(comp, c) for c in usar if os.path.exists(os.path.join(comp, c))]
    hojas += [os.path.join(f, '.build/temas.css'), *[os.path.join(f, c) for c in extra_css]]
    dcss = os.path.join(f, 'direcciones', d['id'] + '.css')
    if os.path.exists(dcss):
        hojas.append(dcss)
    return '<meta name="viewport" content="width=device-width">' + ''.join(f'<link rel="stylesheet" href="{rel(h)}">' for h in hojas)


def latidos():
    b = []
    for i in range(48):
        c = 'no' if i >= 46 else ('med' if i in (17, 18, 31) else '')
        b.append(f'<i class="{c}"></i>' if c else '<i></i>')
    return ''.join(b)


def armar_pantalla(carpeta, props, d, p):
    f = os.path.join(carpeta, 'fuente')
    iconos = os.path.join(f, 'assets/iconos')
    src = open(os.path.join(f, p['archivo'])).read()
    parciales = {'SLIDE': 'pantallas/_slide.html'}
    for k, v in parciales.items():
        if '{{' + k + '}}' in src:
            src = src.replace('{{' + k + '}}', open(os.path.join(f, v)).read())
    qr = open(os.path.join(f, 'assets/qr.svg')).read() if os.path.exists(os.path.join(f, 'assets/qr.svg')) else ''
    modo = p.get('modo', d.get('modo', 'light'))
    src = (src.replace('{{ATTRS}}', f'data-theme="{d["id"]}" data-mode="{modo}" data-dir="{d["id"]}" data-pantalla="{p["id"]}"')
              .replace('{{HEAD}}', head_html(carpeta, d, props.get('css', []), props)
                       + f'<style>:root{{--vw:{p["ancho"]}px;--vh:{p["alto"]}px}}html,body{{width:{p["ancho"]}px;height:{p["alto"]}px}}</style>')
              .replace('{{NOMBRE}}', html.escape(d['nombre']))
              .replace('{{QR}}', qr).replace('{{LATIDOS}}', latidos())
              .replace('{{A}}', os.path.relpath(os.path.join(f, 'assets'), os.path.join(f, '.build'))))
    src = expandir_iconos(src, iconos)
    out = os.path.join(f, '.build', f'{d["id"]}-{p["id"]}.html')
    open(out, 'w').write(src)
    return out


def paso_pantallas(carpeta, props, solo_dir=None, solo_pantalla=None):
    os.makedirs(os.path.join(carpeta, 'pantallas'), exist_ok=True)
    trabajos = []
    for d in props['direcciones']:
        if solo_dir and d['id'] not in solo_dir:
            continue
        for p in props['pantallas']:
            if solo_pantalla and p['id'] not in solo_pantalla:
                continue
            h = armar_pantalla(carpeta, props, d, p)
            png = os.path.join(carpeta, 'pantallas', f'{d["id"]}-{p["id"]}.png')
            trabajos.append((h, png, p['ancho'], p['alto']))
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for png in ex.map(lambda t: captura(*t), trabajos):
            print('  ', os.path.relpath(png, carpeta))
    return [t[1] for t in trabajos]


def paso_catalogo(carpeta, props, solo_dir=None):
    f = os.path.join(carpeta, 'fuente')
    cat = os.path.join(f, 'componentes', 'catalogo.html')
    if not os.path.exists(cat):
        print('  (sin catalogo.html en fuente/componentes: salteo)')
        return []
    base = open(cat).read()
    trabajos = []
    for d in props['direcciones']:
        if solo_dir and d['id'] not in solo_dir:
            continue
        src = re.sub(r'<html([^>]*)data-theme="[^"]*"', f'<html\\1data-theme="{d["id"]}"', base)
        src = re.sub(r'data-mode="[^"]*"', f'data-mode="{d.get("modo", "light")}"', src, count=1)
        comp = os.path.relpath(os.path.join(f, 'componentes'), os.path.join(f, '.build'))
        src = re.sub(r'href="(?!https?:|/|\.\./)([^"]+\.css)"', lambda m: f'href="{comp}/{m.group(1)}"', src)
        extra = (f'<link rel="stylesheet" href="../assets/fuentes/fuentes.css"><link rel="stylesheet" href="temas.css">'
                 f'<link rel="stylesheet" href="../direcciones/{d["id"]}.css">')
        src = src.replace('<!-- TEMAS -->', extra)
        out = os.path.join(f, '.build', f'{d["id"]}-componentes.html')
        open(out, 'w').write(src)
        alto = props.get('catalogo_alto', 2700)
        trabajos.append((out, os.path.join(carpeta, 'pantallas', f'{d["id"]}-componentes.png'), 1440, alto, 2))
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(lambda t: captura(*t), trabajos))
    return [t[1] for t in trabajos]


# ---------------------------------------------------------------- contraste
PARES = [
    ('foreground', 'background', 'texto'), ('muted-foreground', 'background', 'texto'), ('foreground', 'card', 'texto'),
    ('muted-foreground', 'card', 'texto'), ('primary-foreground', 'primary', 'texto'), ('accent-ink', 'card', 'texto'),
    ('accent-ink', 'background', 'texto'), ('destructive', 'background', 'texto'), ('success', 'background', 'texto'),
    ('warning', 'background', 'texto'), ('destructive', 'card', 'texto'), ('success', 'card', 'texto'),
    ('sidebar-foreground', 'sidebar', 'texto'), ('sidebar-muted', 'sidebar', 'texto'),
    ('sidebar-accent-foreground', 'sidebar-accent', 'texto'), ('input', 'card', 'borde'), ('ring', 'background', 'borde'),
]


def resolver(t, k):
    if k.startswith('#'):
        return k
    v = t.get(k)
    for _ in range(4):
        if isinstance(v, str) and v.startswith('var(--'):
            v = t.get(v[6:-1])
    return v


def paso_contraste(carpeta, props):
    lineas, fallas = [], 0
    for d in props['direcciones']:
        d['contraste'] = {}
        for modo in ('light', 'dark'):
            t = completar_shadcn(d['tokens'][modo])
            ok = total = 0
            minimo = 99
            for fg, bg, tipo in PARES + [tuple(x) for x in d.get('pares_extra', [])]:
                a, b = resolver(t, fg), resolver(t, bg)
                if not (a and b and a.startswith('#') and b.startswith('#')):
                    continue
                r = contraste(a, b)
                cumple = r >= (4.5 if tipo == 'texto' else 3.0)
                total += 1
                ok += cumple
                if tipo == 'texto':
                    minimo = min(minimo, r)
                if not cumple:
                    fallas += 1
                    lineas.append(f'NO  {d["id"]} {modo}: {fg} {a} sobre {bg} {b} [{tipo}] {r:.2f}:1')
            res = f'{ok}/{total} pares cumplen AA · texto mínimo {minimo:.2f}:1'.replace('.', ',')
            d['contraste'][modo] = res
            lineas.append(f'{d["id"]:<10} {modo:<5} {res}')
    open(os.path.join(carpeta, 'contraste.txt'), 'w').write('\n'.join(lineas) + '\n')
    print('\n'.join(lineas))
    return fallas


# ---------------------------------------------------------------- límites duros medidos
CHEQUEO_JS = """<script>addEventListener('load', async () => { await document.fonts.ready;
 const tv = !!document.querySelector('.tv'); const r = {min: 99, texto: '', recortes: [], scrollX: document.documentElement.scrollWidth > innerWidth + 1};
 const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
 while (w.nextNode()) { const t = w.currentNode, el = t.parentElement; if (!t.textContent.trim()) continue;
  const cs = getComputedStyle(el); const b = el.getBoundingClientRect();
  if (cs.visibility === 'hidden' || b.width === 0 || b.height === 0 || b.right < 0 || b.left > innerWidth || b.bottom < 0 || b.top > innerHeight) continue;
  if (!tv && el.closest('.slide-wrap')) continue;
  const fs = parseFloat(cs.fontSize); if (fs === 0) continue; if (fs < r.min) { r.min = fs; r.texto = t.textContent.trim().slice(0, 40); }
  if (el.scrollWidth > el.clientWidth + 1 && cs.textOverflow !== 'ellipsis' && cs.overflow !== 'visible' && el.children.length === 0) r.recortes.push(t.textContent.trim().slice(0, 40)); }
 for (const el of document.body.querySelectorAll('*')) { if (!tv && el.closest('.slide-wrap')) continue; const b = el.getBoundingClientRect(); if (b.width === 0 && b.height === 0) continue;
  for (const ps of ['::before', '::after']) { const c = getComputedStyle(el, ps); const txt = (c.content || '').replace(/^["']|["']$/g, '');
   if (!txt || txt === 'none' || txt === 'normal' || !/[0-9A-Za-zÁÉÍÓÚáéíóúñ]/.test(txt) || c.display === 'none' || c.visibility === 'hidden') continue;
   const fs = parseFloat(c.fontSize); if (fs > 0 && fs < r.min) { r.min = fs; r.texto = ps + ' ' + txt.slice(0, 40); } } }
 document.body.insertAdjacentHTML('beforeend', '<pre id="chequeo">' + JSON.stringify(r) + '</pre>'); });</script>"""


def paso_limites(carpeta, props):
    """Texto mínimo (12 px; 28 px en TV), scroll horizontal y texto recortado sin elipsis, por pantalla."""
    b = os.path.join(carpeta, 'fuente', '.build')
    trabajos = []
    for d in props['direcciones']:
        for p in props['pantallas']:
            h = os.path.join(b, f'{d["id"]}-{p["id"]}.html')
            if not os.path.exists(h):
                continue
            c = h.replace('.html', '.chequeo.html')
            open(c, 'w').write(open(h).read().replace('</body>', CHEQUEO_JS + '</body>'))
            trabajos.append((d['id'], p, c))

    def medir(t):
        _, p, c = t
        perfil = tempfile.mkdtemp(prefix='pv-')
        try:
            out = subprocess.run([headless_shell() or chrome(), *([] if headless_shell() else ['--headless=new']), '--no-sandbox', '--disable-gpu',
                                  f'--user-data-dir={perfil}', f'--window-size={p["ancho"]},{p["alto"]}', '--virtual-time-budget=6000',
                                  '--dump-dom', 'file://' + c], capture_output=True, text=True, timeout=120).stdout
        finally:
            shutil.rmtree(perfil, ignore_errors=True)
        m = re.search(r'<pre id="chequeo">(\{.*?\})</pre>', out, re.S)
        return json.loads(html.unescape(m.group(1))) if m else None

    lineas, fallas = [], 0
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for (did, p, _), r in zip(trabajos, ex.map(medir, trabajos)):
            if r is None:
                lineas.append(f'??  {did}-{p["id"]}: sin resultado')
                fallas += 1
                continue
            minimo = 28 if p['id'] == 'tv' or abs(p['ancho'] / p['alto'] - 16 / 9) < 0.01 and p['ancho'] >= 1900 else 12
            ok = r['min'] >= minimo - 0.01 and not r['scrollX'] and not r['recortes']
            fallas += not ok
            lineas.append(f'{"OK " if ok else "NO "} {did}-{p["id"]}: texto mínimo {r["min"]:.1f} px (≥ {minimo}) «{r["texto"]}» · scroll horizontal: {"sí" if r["scrollX"] else "no"} · recortes: {len(r["recortes"])} {r["recortes"][:3] if r["recortes"] else ""}')
    open(os.path.join(carpeta, 'limites.txt'), 'w').write('\n'.join(lineas) + '\n')
    print('\n'.join(lineas))
    return fallas


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('carpeta')
    ap.add_argument('--solo', default='temas,pantallas,catalogo,limites,contraste,docs,pdf,galeria,revision')
    ap.add_argument('--dir', default=None)
    ap.add_argument('--pantalla', default=None)
    a = ap.parse_args(argv)
    carpeta = os.path.abspath(a.carpeta)
    global LUCIDE
    LUCIDE = lucide_dir(carpeta)
    props = json.load(open(os.path.join(carpeta, 'fuente', 'propuesta.json')))
    pasos = a.solo.split(',')
    solo_dir = a.dir.split(',') if a.dir else None
    solo_p = a.pantalla.split(',') if a.pantalla else None
    os.makedirs(os.path.join(carpeta, 'fuente', '.build'), exist_ok=True)
    comp_dest = os.path.join(carpeta, 'fuente', 'componentes')
    if not os.path.exists(comp_dest):
        shutil.copytree(os.path.join(SKILL, 'templates', 'componentes'), comp_dest)
    # los temas siempre: el resto de los pasos los necesita
    open(os.path.join(carpeta, 'fuente', '.build', 'temas.css'), 'w').write(temas_css(props))
    if 'temas' in pasos:
        for d in props['direcciones']:
            os.makedirs(os.path.join(carpeta, d['id']), exist_ok=True)
            open(os.path.join(carpeta, d['id'], 'tokens.css'), 'w').write(tokens_proyecto(d))
        print('temas: ok')
    if 'pantallas' in pasos:
        print('pantallas:')
        paso_pantallas(carpeta, props, solo_dir, solo_p)
    if 'catalogo' in pasos:
        print('catalogo:')
        paso_catalogo(carpeta, props, solo_dir)
    fallas = 0
    if 'limites' in pasos:
        print('limites:')
        fallas += paso_limites(carpeta, props)
    if 'contraste' in pasos or 'docs' in pasos or 'pdf' in pasos:
        fallas += paso_contraste(carpeta, props)
    try:
        import cuadernillo
    except ImportError:
        cuadernillo = None
    if cuadernillo:
        if 'docs' in pasos:
            cuadernillo.docs(carpeta, props)
        if 'pdf' in pasos:
            cuadernillo.pdf(carpeta, props, imprimir_pdf)
        if 'galeria' in pasos:
            cuadernillo.galeria(carpeta, props)
        if 'revision' in pasos:
            cuadernillo.revision(carpeta)
    return 1 if fallas else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
