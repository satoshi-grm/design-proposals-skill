#!/usr/bin/env python3
"""Builds a visual-proposals booklet from <folder>/source/proposal.json.

Steps (all, or a subset with --only):
  themes    tokens per direction -> source/.build/themes.css and <dir>/tokens.css (CSS + Tailwind v4 + shadcn)
  screens   every screen x direction -> real-size HTML -> 2x PNG with headless Chrome (screens/)
  catalog   the component library with each direction's theme -> screens/<dir>-components.png
  limits    min text (12 px; 28 px on TV), horizontal scroll and clipping measured in Chrome -> limits.txt
  contrast  WCAG pairs per direction and mode -> contrast.txt (exit 1 if anything fails)
  docs      <dir>/design.md per direction
  pdf       16:9 booklet -> proposals.html and proposals.pdf
  gallery   browsable index.html with a per-direction filter
  review    contact sheets of every PDF page (source/.build/review-N.png) to inspect with vision

Legacy booklets (a <folder>/fuente/ folder) keep their old file names for inputs and outputs.

Usage: build.py <folder> [--only themes,screens] [--dir <id>] [--screen <id>]
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
from types import SimpleNamespace

sys.dont_write_bytecode = True  # no __pycache__ inside the skill
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import booklet  # noqa: E402
from booklet import page_type  # noqa: E402
from contrast import contrast  # noqa: E402
from i18n import t  # noqa: E402

SKILL_NAME = os.path.basename(SKILL)
LUCIDE = None  # set by main() with lucide_dir()
STEPS = ['themes', 'screens', 'catalog', 'limits', 'contrast', 'docs', 'pdf', 'gallery', 'review']
LEGACY_STEPS = {'temas': 'themes', 'pantallas': 'screens', 'catalogo': 'catalog', 'limites': 'limits', 'contraste': 'contrast', 'galeria': 'gallery', 'revision': 'review'}
COMPONENT_ORDER = ['base.css', 'shell.css', 'table.css', 'overlays.css', 'forms.css', 'states.css', 'pages.css', 'charts.css']
# component files renamed in v2: new -> old (looked up both ways)
COMPONENT_ALIASES = {'table.css': 'tabla.css', 'forms.css': 'formularios.css', 'states.css': 'estados.css', 'pages.css': 'paginas.css',
                     'charts.css': 'graficos.css', 'themes-example.css': 'temas-ejemplo.css', 'catalog.html': 'catalogo.html'}
COMPONENT_ALIASES.update({v: k for k, v in list(COMPONENT_ALIASES.items())})

# proposal.json keys renamed in v2: old -> new
KEY_ALIASES = {
    'titulo': 'title', 'proyecto': 'project', 'fecha': 'date', 'contexto': 'context', 'fijo': 'fixed', 'varia': 'varies',
    'como_leer': 'how_to_read', 'datos_ficticios': 'fictional_data', 'componentes_pantallas': 'screen_components',
    'portada_pantalla': 'cover_screen', 'catalogo_alto': 'catalog_height', 'pantallas': 'screens', 'archivo': 'file',
    'ancho': 'width', 'alto': 'height', 'nombre': 'name', 'nota': 'note', 'modo': 'mode', 'pagina': 'page',
    'direcciones': 'directions', 'frase': 'tagline', 'firma': 'signature', 'fuentes': 'fonts', 'referencias': 'references',
    'ejes': 'axes', 'temperatura': 'temperature', 'densidad': 'density', 'tipografia': 'typography', 'forma': 'shape',
    'imagen': 'imagery', 'movimiento': 'motion', 'a_favor': 'pros', 'en_contra': 'cons', 'notas': 'notes',
    'pares_extra': 'extra_pairs', 'apertura_img': 'opening_image', 'apertura_pos': 'opening_position',
    'comparativa': 'comparison', 'columnas': 'columns', 'valores': 'values', 'mezcla_regla': 'mix_rule', 'mezclas': 'mixes',
    'texto': 'text', 'imgs': 'images', 'recomendacion': 'recommendation', 'base_nombre': 'base_name', 'resumen': 'summary',
    'porque': 'why', 'alternativa': 'alternative', 'pasos': 'steps', 'pregunta': 'question',
}
OPAQUE = {'tokens', 'notes', 'values'}  # keys are data (token names, screen ids, direction ids): never renamed


def _alias(x):
    if isinstance(x, list):
        return [_alias(v) for v in x]
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            k = KEY_ALIASES.get(k, k)
            out[k] = v if k in OPAQUE else _alias(v)
        return out
    return x


def booklet_paths(folder):
    """Every input/output path of a booklet; legacy (Spanish) names when <folder>/fuente/ exists."""
    folder = os.path.abspath(folder)
    lg = os.path.isdir(os.path.join(folder, 'fuente'))
    n = (lambda old, new: old if lg else new)  # noqa: E731
    src = os.path.join(folder, n('fuente', 'source'))
    assets = os.path.join(src, 'assets')
    return SimpleNamespace(
        legacy=lg, root=folder, src=src, assets=assets, build=os.path.join(src, '.build'),
        proposal=os.path.join(src, n('propuesta.json', 'proposal.json')),
        components=os.path.join(src, n('componentes', 'components')),
        directions=os.path.join(src, n('direcciones', 'directions')),
        screens_src=os.path.join(src, n('pantallas', 'screens')),
        fonts_css=os.path.join(assets, n('fuentes/fuentes.css', 'fonts/fonts.css')),
        icons=os.path.join(assets, n('iconos', 'icons')), photos=os.path.join(assets, n('fotos', 'photos')),
        themes_css=os.path.join(src, '.build', n('temas.css', 'themes.css')),
        shots_rel=n('pantallas', 'screens'), shots=os.path.join(folder, n('pantallas', 'screens')),
        catalog_id=n('componentes', 'components'), before_after=n('antes-despues.png', 'before-after.png'),
        pdf=n('propuestas.pdf', 'proposals.pdf'), pdf_html=n('propuestas.html', 'proposals.html'),
        contrast=n('contraste.txt', 'contrast.txt'), limits=n('limites.txt', 'limits.txt'),
        review=n('revision', 'review'))


def load_proposal(folder):
    """Reads the booklet's proposal.json (or legacy propuesta.json) with every key in English; returns (props, paths)."""
    P = booklet_paths(folder)
    props = _alias(json.load(open(P.proposal)))
    props.setdefault('lang', 'en')
    return props, P


def component_file(P, name):
    """Path of a component file in the booklet, trying the old/new alias; None when neither exists."""
    for c in (name, COMPONENT_ALIASES.get(name)):
        if c and os.path.exists(os.path.join(P.components, c)):
            return os.path.join(P.components, c)
    return None


def chrome():
    import glob
    playwright = sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-*/chrome')), reverse=True)
    for c in (os.environ.get('CHROME'), shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser'), *playwright):
        if c:
            return c
    sys.exit('Chrome/Chromium not found. Install Google Chrome or the system Chromium, or the Playwright one '
             '(python3 -m playwright install chromium), and if it is outside PATH set CHROME=/path/to/binary '
             '(or SHOT_CHROME for chrome-headless-shell).')


def headless_shell():
    """chrome-headless-shell honors the exact viewport; Chrome with --headless=new takes ~87 px off the height."""
    import glob
    for c in [os.environ.get('SHOT_CHROME')] + sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell')), reverse=True) + [shutil.which('chrome-headless-shell')]:
        if c and os.path.exists(c):
            return c
    return None


def run_chrome(args, binary=None):
    profile = tempfile.mkdtemp(prefix='pv-')
    try:
        cmd = [binary] if binary else [chrome(), '--headless=new']
        subprocess.run([*cmd, '--no-sandbox', '--disable-gpu', f'--user-data-dir={profile}',
                        '--hide-scrollbars', '--run-all-compositor-stages-before-draw', *args],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def screenshot(html_path, png, width, height, scale=2):
    shell = headless_shell()
    if not shell:  # fallback: a higher window to make up for the bar --headless=new takes
        height += 87
    run_chrome([f'--window-size={width},{height}', f'--force-device-scale-factor={scale}',
                '--virtual-time-budget=6000', f'--screenshot={png}', 'file://' + html_path], shell)
    return png


def print_pdf(html_path, pdf):
    run_chrome(['--virtual-time-budget=20000', '--no-pdf-header-footer', f'--print-to-pdf={pdf}', 'file://' + html_path])


# ---------------------------------------------------------------- icons
_icon_cache = {}
_warned = set()


def lucide_dir(folder):
    """LUCIDE_DIR -> <booklet>/node_modules -> <booklet>/../node_modules; None if none exists."""
    for c in (os.environ.get('LUCIDE_DIR'), os.path.join(folder, 'node_modules/lucide-static/icons'),
              os.path.join(os.path.dirname(folder), 'node_modules/lucide-static/icons')):
        if c and os.path.isdir(c):
            return c
    return None


def icon(name, cls, icons_dir):
    if name not in _icon_cache:
        local = os.path.join(icons_dir, name + '.svg')
        if not os.path.exists(local):
            origin = os.path.join(LUCIDE, name + '.svg') if LUCIDE else ''
            if not os.path.exists(origin):
                if not LUCIDE and 'lucide' not in _warned:
                    _warned.add('lucide')
                    print('  warning: no Lucide icons. Install them with "npm i lucide-static" in the booklet folder '
                          '(or set LUCIDE_DIR=.../lucide-static/icons); continuing without icons.')
                elif LUCIDE and name not in _warned:
                    _warned.add(name)
                    print(f'  warning: icon "{name}" does not exist in Lucide; left empty.')
                return ''
            os.makedirs(icons_dir, exist_ok=True)
            shutil.copy(origin, local)
        svg = open(local).read()
        svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S).strip()
        svg = re.sub(r'\s(class|width|height)="[^"]*"', '', svg, count=3)
        _icon_cache[name] = svg
    return _icon_cache[name].replace('<svg', f'<svg class="i {cls}" aria-hidden="true"', 1)


def expand_icons(text, icons_dir):
    def rep(m):
        name, _, cls = m.group(1).partition('|')
        return icon(name, cls, icons_dir)
    return re.sub(r'\{i:([\w-]+(?:\|[\w-]+)?)\}', rep, text)


# ---------------------------------------------------------------- themes
def css_vars(tokens, indent='  '):
    return '\n'.join(f'{indent}--{k}: {v};' for k, v in tokens.items())


def themes_css(props):
    parts = []
    for d in props['directions']:
        parts.append(f'[data-theme="{d["id"]}"] {{\n{css_vars(d["tokens"]["light"])}\n}}')
        parts.append(f'[data-theme="{d["id"]}"][data-mode="dark"] {{\n{css_vars(d["tokens"]["dark"])}\n}}')
    return '\n'.join(parts) + '\n'


def complete_shadcn(tk):
    """The contract tokens + the ones shadcn expects, derived from the contract."""
    tk = dict(tk)
    for k, v in {'card-foreground': 'foreground', 'popover-foreground': 'foreground', 'secondary': 'muted',
                 'secondary-foreground': 'foreground', 'accent': 'muted', 'accent-foreground': 'foreground',
                 'ring': 'accent-ink', 'sidebar-primary': 'primary', 'sidebar-primary-foreground': 'primary-foreground',
                 'sidebar-ring': 'accent-ink', 'popover': 'card', 'destructive-foreground': None}.items():
        if k not in tk:
            tk[k] = tk.get(v, '#ffffff') if v else '#ffffff'
    return tk


def project_tokens(d, lang):
    """tokens.css ready to paste into a project with shadcn/ui and Tailwind v4."""
    light, dark = complete_shadcn(d['tokens']['light']), complete_shadcn(d['tokens']['dark'])
    colors = [k for k in light if not k.startswith(('font-', 'text-', 'radius', 'control-', 'row-', 'gap', 'pad', 'shadow', 'ease', 'dur-', 'display-', 'border-width'))]
    others = [k for k in light if k not in colors]
    lines = [t(lang, 'tokens_header', name=d['name'], skill=SKILL_NAME), t(lang, 'tokens_fonts', fonts=', '.join(d.get('fonts', []))), '',
             ':root {', css_vars({k: light[k] for k in colors + others}), '}', '',
             '.dark {', css_vars({k: dark[k] for k in colors if k in dark}), '}', '',
             '@theme inline {']
    lines += [f'  --color-{k}: var(--{k});' for k in colors]
    lines += ['  --font-sans: var(--font-sans);', '  --font-display: var(--font-display);', '  --font-mono: var(--font-mono);',
              '  --radius-sm: var(--radius-sm);', '  --radius-md: var(--radius);', '  --radius-lg: var(--radius-lg);',
              '  --shadow-float: var(--shadow-float);', '  --ease-out: var(--ease-out);', '}', '']
    return '\n'.join(lines)


# ---------------------------------------------------------------- screens
def head_html(P, d, props):
    rel = lambda p: os.path.relpath(p, P.build)  # noqa: E731
    sheets = [P.fonts_css]
    sheets += [f for f in (component_file(P, c) for c in props.get('screen_components', COMPONENT_ORDER)) if f]
    sheets += [P.themes_css, *[os.path.join(P.src, c) for c in props.get('css', [])]]
    dcss = os.path.join(P.directions, d['id'] + '.css')
    if os.path.exists(dcss):
        sheets.append(dcss)
    return '<meta name="viewport" content="width=device-width">' + ''.join(f'<link rel="stylesheet" href="{rel(h)}">' for h in sheets)


def beats():
    b = []
    for i in range(48):
        c = 'no' if i >= 46 else ('med' if i in (17, 18, 31) else '')
        b.append(f'<i class="{c}"></i>' if c else '<i></i>')
    return ''.join(b)


def build_screen(P, props, d, s):
    src = open(os.path.join(P.src, s['file'])).read()
    if '{{SLIDE}}' in src:
        src = src.replace('{{SLIDE}}', open(os.path.join(P.screens_src, '_slide.html')).read())
    qr_path = os.path.join(P.assets, 'qr.svg')
    qr = open(qr_path).read() if os.path.exists(qr_path) else ''
    mode = s.get('mode', d.get('mode', 'light'))
    name = html.escape(d['name'])
    src = (src.replace('{{ATTRS}}', f'data-theme="{d["id"]}" data-mode="{mode}" data-dir="{d["id"]}" data-screen="{s["id"]}" data-pantalla="{s["id"]}"')
              .replace('{{HEAD}}', head_html(P, d, props)
                       + f'<style>:root{{--vw:{s["width"]}px;--vh:{s["height"]}px}}html,body{{width:{s["width"]}px;height:{s["height"]}px}}</style>')
              .replace('{{NAME}}', name).replace('{{NOMBRE}}', name)
              .replace('{{QR}}', qr).replace('{{BEATS}}', beats()).replace('{{LATIDOS}}', beats())
              .replace('{{A}}', os.path.relpath(P.assets, P.build)))
    src = expand_icons(src, P.icons)
    out = os.path.join(P.build, f'{d["id"]}-{s["id"]}.html')
    open(out, 'w').write(src)
    return out


def step_screens(P, props, only_dir=None, only_screen=None):
    os.makedirs(P.shots, exist_ok=True)
    jobs = []
    for d in props['directions']:
        if only_dir and d['id'] not in only_dir:
            continue
        for s in props['screens']:
            if only_screen and s['id'] not in only_screen:
                continue
            h = build_screen(P, props, d, s)
            jobs.append((h, os.path.join(P.shots, f'{d["id"]}-{s["id"]}.png'), s['width'], s['height']))
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for png in ex.map(lambda j: screenshot(*j), jobs):
            print('  ', os.path.relpath(png, P.root))
    return [j[1] for j in jobs]


def step_catalog(P, props, only_dir=None):
    cat = component_file(P, 'catalog.html')
    if not cat:
        print(f'  (no catalog.html in {os.path.relpath(P.components, P.root)}: skipped)')
        return []
    base = open(cat).read()
    comp = os.path.relpath(P.components, P.build)

    def href(m):
        f = m.group(1)
        if not os.path.exists(os.path.join(P.components, f)) and COMPONENT_ALIASES.get(f):
            f = COMPONENT_ALIASES[f]
        return f'href="{comp}/{f}"'
    jobs = []
    for d in props['directions']:
        if only_dir and d['id'] not in only_dir:
            continue
        src = re.sub(r'<html([^>]*)data-theme="[^"]*"', f'<html\\1data-theme="{d["id"]}"', base)
        src = re.sub(r'data-mode="[^"]*"', f'data-mode="{d.get("mode", "light")}"', src, count=1)
        src = re.sub(r'href="(?!https?:|/|\.\./)([^"]+\.css)"', href, src)
        rel = lambda p: os.path.relpath(p, P.build)  # noqa: E731
        extra = (f'<link rel="stylesheet" href="{rel(P.fonts_css)}"><link rel="stylesheet" href="{rel(P.themes_css)}">'
                 f'<link rel="stylesheet" href="{rel(os.path.join(P.directions, d["id"] + ".css"))}">')
        src = src.replace('<!-- THEMES -->', extra).replace('<!-- TEMAS -->', extra)
        out = os.path.join(P.build, f'{d["id"]}-{P.catalog_id}.html')
        open(out, 'w').write(src)
        jobs.append((out, os.path.join(P.shots, f'{d["id"]}-{P.catalog_id}.png'), 1440, props.get('catalog_height', 2700), 2))
    os.makedirs(P.shots, exist_ok=True)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(lambda j: screenshot(*j), jobs))
    return [j[1] for j in jobs]


# ---------------------------------------------------------------- contrast
PAIRS = [
    ('foreground', 'background', 'text'), ('muted-foreground', 'background', 'text'), ('foreground', 'card', 'text'),
    ('muted-foreground', 'card', 'text'), ('primary-foreground', 'primary', 'text'), ('accent-ink', 'card', 'text'),
    ('accent-ink', 'background', 'text'), ('destructive', 'background', 'text'), ('success', 'background', 'text'),
    ('warning', 'background', 'text'), ('destructive', 'card', 'text'), ('success', 'card', 'text'),
    ('sidebar-foreground', 'sidebar', 'text'), ('sidebar-muted', 'sidebar', 'text'),
    ('sidebar-accent-foreground', 'sidebar-accent', 'text'), ('input', 'card', 'border'), ('ring', 'background', 'border'),
]
KINDS = {'texto': 'text', 'borde': 'border', 'grande': 'large'}


def resolve(tk, k):
    if k.startswith('#'):
        return k
    v = tk.get(k)
    for _ in range(4):
        if isinstance(v, str) and v.startswith('var(--'):
            v = tk.get(v[6:-1])
    return v


def step_contrast(P, props):
    lang = props['lang']
    lines, fails = [], 0
    for d in props['directions']:
        d['contrast'] = {}
        for mode in ('light', 'dark'):
            tk = complete_shadcn(d['tokens'][mode])
            ok = total = 0
            lowest = 99
            for fg, bg, kind in PAIRS + [tuple(x) for x in d.get('extra_pairs', [])]:
                kind = KINDS.get(kind, kind)
                a, b = resolve(tk, fg), resolve(tk, bg)
                if not (a and b and a.startswith('#') and b.startswith('#')):
                    continue
                r = contrast(a, b)
                passes = r >= (4.5 if kind == 'text' else 3.0)
                total += 1
                ok += passes
                if kind == 'text':
                    lowest = min(lowest, r)
                if not passes:
                    fails += 1
                    lines.append(t(lang, 'contrast_fail', dir=d['id'], mode=mode, fg=fg, a=a, bg=bg, b=b, kind=t(lang, 'kind_' + kind), ratio=f'{r:.2f}'))
            res = t(lang, 'contrast_summary', ok=ok, total=total, min=f'{lowest:.2f}'.replace('.', t(lang, 'decimal')))
            d['contrast'][mode] = res
            lines.append(f'{d["id"]:<10} {mode:<5} {res}')
    open(os.path.join(P.root, P.contrast), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return fails


# ---------------------------------------------------------------- measured hard limits
CHECK_JS = """<script>addEventListener('load', async () => { await document.fonts.ready;
 const tv = !!document.querySelector('.tv'); const r = {min: 99, text: '', clipped: [], scrollX: document.documentElement.scrollWidth > innerWidth + 1};
 const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
 while (w.nextNode()) { const t = w.currentNode, el = t.parentElement; if (!t.textContent.trim()) continue;
  const cs = getComputedStyle(el); const b = el.getBoundingClientRect();
  if (cs.visibility === 'hidden' || b.width === 0 || b.height === 0 || b.right < 0 || b.left > innerWidth || b.bottom < 0 || b.top > innerHeight) continue;
  if (!tv && el.closest('.slide-wrap')) continue;
  const fs = parseFloat(cs.fontSize); if (fs === 0) continue; if (fs < r.min) { r.min = fs; r.text = t.textContent.trim().slice(0, 40); }
  if (el.scrollWidth > el.clientWidth + 1 && cs.textOverflow !== 'ellipsis' && cs.overflow !== 'visible' && el.children.length === 0) r.clipped.push(t.textContent.trim().slice(0, 40)); }
 for (const el of document.body.querySelectorAll('*')) { if (!tv && el.closest('.slide-wrap')) continue; const b = el.getBoundingClientRect(); if (b.width === 0 && b.height === 0) continue;
  for (const ps of ['::before', '::after']) { const c = getComputedStyle(el, ps); const txt = (c.content || '').replace(/^["']|["']$/g, '');
   if (!txt || txt === 'none' || txt === 'normal' || !/[0-9A-Za-z\\u00C0-\\u024F]/.test(txt) || c.display === 'none' || c.visibility === 'hidden') continue;
   const fs = parseFloat(c.fontSize); if (fs > 0 && fs < r.min) { r.min = fs; r.text = ps + ' ' + txt.slice(0, 40); } } }
 document.body.insertAdjacentHTML('beforeend', '<pre id="check">' + JSON.stringify(r) + '</pre>'); });</script>"""


def step_limits(P, props):
    """Min text (12 px; 28 px on TV), horizontal scroll and text clipped without ellipsis, per screen."""
    lang = props['lang']
    jobs = []
    for d in props['directions']:
        for s in props['screens']:
            h = os.path.join(P.build, f'{d["id"]}-{s["id"]}.html')
            if not os.path.exists(h):
                continue
            c = h.replace('.html', '.check.html')
            open(c, 'w').write(open(h).read().replace('</body>', CHECK_JS + '</body>'))
            jobs.append((d['id'], s, c))

    def measure(j):
        _, s, c = j
        profile = tempfile.mkdtemp(prefix='pv-')
        try:
            out = subprocess.run([headless_shell() or chrome(), *([] if headless_shell() else ['--headless=new']), '--no-sandbox', '--disable-gpu',
                                  f'--user-data-dir={profile}', f'--window-size={s["width"]},{s["height"]}', '--virtual-time-budget=6000',
                                  '--dump-dom', 'file://' + c], capture_output=True, text=True, timeout=120).stdout
        finally:
            shutil.rmtree(profile, ignore_errors=True)
        m = re.search(r'<pre id="check">(\{.*?\})</pre>', out, re.S)
        return json.loads(html.unescape(m.group(1))) if m else None

    lines, fails = [], 0
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for (did, s, _), r in zip(jobs, ex.map(measure, jobs)):
            sid = f'{did}-{s["id"]}'
            if r is None:
                lines.append(t(lang, 'limits_none', id=sid))
                fails += 1
                continue
            req = 28 if s['id'] == 'tv' or page_type(s) == 'tv' else 12
            ok = r['min'] >= req - 0.01 and not r['scrollX'] and not r['clipped']
            fails += not ok
            lines.append(t(lang, 'limits_line', status='OK ' if ok else 'NO ', id=sid, min=f'{r["min"]:.1f}', req=req, text=r['text'],
                           scroll=t(lang, 'yes' if r['scrollX'] else 'no'), clipped=len(r['clipped']), sample=r['clipped'][:3] if r['clipped'] else ''))
    open(os.path.join(P.root, P.limits), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return fails


def main(argv):
    ap = argparse.ArgumentParser(description='Build a visual-proposals booklet.')
    ap.add_argument('folder')
    ap.add_argument('--only', '--solo', dest='only', default=','.join(STEPS), help='comma-separated steps: ' + ','.join(STEPS))
    ap.add_argument('--dir', default=None, help='only these direction ids (comma-separated)')
    ap.add_argument('--screen', '--pantalla', dest='screen', default=None, help='only these screen ids (comma-separated)')
    a = ap.parse_args(argv)
    folder = os.path.abspath(a.folder)
    global LUCIDE
    LUCIDE = lucide_dir(folder)
    if not os.path.exists(booklet_paths(folder).proposal):
        sys.exit(f'Missing {booklet_paths(folder).proposal} (copy templates/example/ to start)')
    props, P = load_proposal(folder)
    steps = [LEGACY_STEPS.get(s.strip(), s.strip()) for s in a.only.split(',') if s.strip()]
    unknown = [s for s in steps if s not in STEPS]
    if unknown:
        ap.error(f'unknown steps: {",".join(unknown)} (valid: {",".join(STEPS)})')
    only_dir = a.dir.split(',') if a.dir else None
    only_screen = a.screen.split(',') if a.screen else None
    os.makedirs(P.build, exist_ok=True)
    if not os.path.exists(P.components):
        shutil.copytree(os.path.join(SKILL, 'templates', 'components'), P.components)
    # themes always: every other step needs them
    open(P.themes_css, 'w').write(themes_css(props))
    if 'themes' in steps:
        for d in props['directions']:
            os.makedirs(os.path.join(folder, d['id']), exist_ok=True)
            open(os.path.join(folder, d['id'], 'tokens.css'), 'w').write(project_tokens(d, props['lang']))
        print('themes: ok')
    if 'screens' in steps:
        print('screens:')
        step_screens(P, props, only_dir, only_screen)
    if 'catalog' in steps:
        print('catalog:')
        step_catalog(P, props, only_dir)
    fails = 0
    if 'limits' in steps:
        print('limits:')
        fails += step_limits(P, props)
    if {'contrast', 'docs', 'pdf'} & set(steps):
        fails += step_contrast(P, props)
    if 'docs' in steps:
        booklet.docs(P, props)
    if 'pdf' in steps:
        booklet.pdf(P, props, print_pdf)
    if 'gallery' in steps:
        booklet.gallery(P, props)
    if 'review' in steps:
        booklet.review(P, props)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
