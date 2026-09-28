"""Booklet outputs: design.md per direction, 16:9 PDF, browsable gallery and review contact sheets.

Called by build.py (not on its own). Reads the same proposal (already loaded with English keys) and the PNGs in screens/.
Every generated human-language string comes from i18n.py.
"""
import glob
import html
import json
import os
import shutil
import subprocess

from i18n import num, t

E = html.escape
SKILL_NAME = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_NO_PIL = []
OLD_COMPONENT_NAMES = {'table.css': 'tabla.css', 'forms.css': 'formularios.css', 'states.css': 'estados.css', 'pages.css': 'paginas.css', 'charts.css': 'graficos.css'}


def page_type(s):
    """'panel', 'mobile' or 'tv' for a screen: explicit "page" (legacy "movil" = mobile), else by size."""
    p = {'movil': 'mobile'}.get(s.get('page'), s.get('page'))
    if p:
        return p
    if s['width'] < 700:
        return 'mobile'
    return 'tv' if abs(s['width'] / s['height'] - 16 / 9) < 0.01 and s['width'] >= 1900 else 'panel'


def _mode_tokens(d):
    return d['tokens']['dark'] if d.get('mode') == 'dark' else d['tokens']['light']


# ---------------------------------------------------------------- design.md
def docs(P, props):
    lang = props['lang']
    project = props.get('project', t(lang, 'project_default'))
    positioning = props.get('context', '') or t(lang, 'positioning_default')
    na = t(lang, 'na')
    rel = lambda p: os.path.relpath(p, P.root)  # noqa: E731
    for i, d in enumerate(props['directions'], 1):
        tk, dk = d['tokens']['light'], d['tokens']['dark']
        colors = [k for k in tk if tk[k].startswith('#')]
        fm = ['---', 'version: design-md-1', f'name: "{project} · {d["name"]}"', f'source: {SKILL_NAME} {props.get("date", "")}',
              f'captured_at: {props.get("date", "")}', 'description: |', f'  {d["idea"]}', 'colors:']
        fm += [f'  {k}: "{tk[k]}"' for k in colors]
        fm += ['typography:',
               f'  display: {{ fontFamily: "{tk["font-display"]}", fontSize: {tk.get("text-xl", "28px")}, fontWeight: {tk.get("display-weight", 600)}, letterSpacing: {tk.get("display-tracking", "0")} }}',
               f'  body: {{ fontFamily: "{tk["font-sans"]}", fontSize: {tk.get("text-base", "14px")}, fontWeight: 400, lineHeight: 1.5 }}',
               f'  caption-mono: {{ fontFamily: "{tk["font-mono"]}", fontSize: 12px, fontWeight: 400 }}',
               'spacing:', '  base: 4px', '  scale: [4, 8, 12, 16, 24, 32, 40, 48]',
               'rounded:', f'  sm: {tk.get("radius-sm", "4px")}', f'  md: {tk.get("radius", "8px")}', f'  lg: {tk.get("radius-lg", "12px")}',
               'components:',
               f'  button-primary: {{ backgroundColor: "{{colors.primary}}", textColor: "{{colors.primary-foreground}}", rounded: "{{rounded.md}}", height: {tk.get("control-h", "32px")} }}',
               f'  input: {{ backgroundColor: "{{colors.card}}", border: "1px solid {{colors.input}}", focusRing: "2px solid {{colors.ring}}", rounded: "{{rounded.md}}" }}',
               '  badge: { rounded: 999px, typography: "{typography.caption-mono}" }',
               f'  table-row: {{ height: {tk.get("row-h", "44px")}, border: "1px solid {{colors.border}}" }}',
               '  sidebar-item: { backgroundColor: "{colors.sidebar}", textColor: "{colors.sidebar-muted}", rounded: "{rounded.md}" }',
               '---', '']
        comp_file = (lambda f: OLD_COMPONENT_NAMES.get(f, f)) if P.legacy else (lambda f: f)
        ax = d['axes']
        c = d.get('contrast', {})
        body = t(lang, 'design_body',
                 project=project, name=d['name'], i=i, n=len(props['directions']), skill=SKILL_NAME, date=props.get('date', ''),
                 proposal_file=rel(P.proposal), dir_css=rel(os.path.join(P.directions, d['id'] + '.css')), references=d['references'],
                 tagline=d['tagline'], idea=d['idea'], signature=d['signature'], temperature=ax['temperature'],
                 density=ax['density'], density_lower=ax['density'].lower(), positioning=positioning, primary=tk['primary'],
                 color_rows='\n'.join(f'| `{k}` | {tk[k]} | {dk.get(k, "—")} | ✅ |' for k in colors),
                 fonts=', '.join(d['fonts']), text_sm=tk.get('text-sm', '13px'), text_base=tk.get('text-base', '14px'), text_xl=tk.get('text-xl', '28px'),
                 font_display=tk['font-display'], font_sans=tk['font-sans'], font_mono=tk['font-mono'],
                 control_h=tk.get('control-h', '32px'), row_h=tk.get('row-h', '44px'),
                 radius_sm=tk.get('radius-sm'), radius=tk.get('radius'), radius_lg=tk.get('radius-lg'), shape=ax['shape'], input=tk['input'],
                 contrast_light_na=c.get('light', na), contrast_dark_na=c.get('dark', na), contrast_light=c.get('light', ''), contrast_dark=c.get('dark', ''),
                 contrast_file=P.contrast, limits_file=P.limits, components_dir='templates/components',
                 comp_rows='\n'.join(f'| {n} | {e} | `{comp_file(f)}` |' for n, e, f in t(lang, 'components')),
                 screen_names=', '.join(s['name'] for s in props['screens']), imagery=ax['imagery'], motion=ax['motion'],
                 shots_dir=P.shots_rel,
                 grid='\n'.join(t(lang, 'design_grid', name=s['name'], w=s.get('width', '?'), h=s.get('height', '?'), note=s.get('note', '')) for s in props['screens']),
                 mono_first=tk['font-mono'].split(',')[0],
                 screen_list='\n'.join(t(lang, 'design_screen', png=f'{P.shots_rel}/{d["id"]}-{s["id"]}.png', name=s['name'], note=s['note']) for s in props['screens']),
                 catalog_png=f'{P.shots_rel}/{d["id"]}-{P.catalog_id}.png', dir_id=d['id'])
        dest = os.path.join(P.root, d['id'])
        os.makedirs(dest, exist_ok=True)
        open(os.path.join(dest, 'design.md'), 'w').write('\n'.join(fm) + body)
    print('docs: design.md x', len(props['directions']))


# ---------------------------------------------------------------- 16:9 PDF
CSS_PDF = """
@page { size: 1600px 900px; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; background: #0e0e0d; }
body { font-family: 'Geist', 'Instrument Sans', system-ui, sans-serif; color: #1a1a18; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.pg { position: relative; width: 1600px; height: 900px; overflow: hidden; page-break-after: always; break-after: page; background: #f3f2ee; }
.pg:last-child { page-break-after: auto; }
.mono { font-family: 'Geist Mono', ui-monospace, monospace; font-variant-numeric: tabular-nums; }
.pie { position: absolute; left: 56px; right: 56px; bottom: 26px; display: flex; justify-content: space-between; font: 500 13px/1 'Geist Mono', monospace; color: #6b6a64; }
h1, h2, h3, p { margin: 0; }
/* cover */
.portada { background: #111110; color: #f3f2ee; display: grid; grid-template-columns: 560px 1fr; }
.portada .txt { padding: 64px 56px; display: flex; flex-direction: column; }
.portada h1 { font: 600 64px/1.02 'Geist', sans-serif; letter-spacing: -0.035em; margin-top: 28px; }
.portada .ctx { margin-top: 26px; font-size: 18px; line-height: 1.5; color: #c9c7bf; max-width: 440px; }
.portada .meta { margin-top: auto; font: 500 13px/1.6 'Geist Mono', monospace; color: #9a988f; }
.mosaico { display: grid; grid-template-columns: repeat(2, 1fr); grid-template-rows: repeat(3, 1fr); gap: 6px; padding: 6px; }
.mosaico figure { margin: 0; position: relative; overflow: hidden; background: #222; }
.mosaico img { width: 100%; height: 100%; object-fit: cover; object-position: top left; }
.mosaico figcaption { position: absolute; left: 10px; bottom: 10px; background: #111110; color: #f3f2ee; padding: 7px 10px; font: 500 14px/1 'Geist', sans-serif; }
.mosaico figcaption b { font-family: 'Geist Mono', monospace; font-weight: 500; color: #9a988f; margin-right: 8px; }
/* text pages */
.cols { position: absolute; inset: 56px 56px 70px; display: grid; gap: 48px; }
.eyebrow { font: 500 14px/1 'Geist Mono', monospace; color: #6b6a64; }
.titulo { font: 600 44px/1.05 'Geist', sans-serif; letter-spacing: -0.03em; margin-top: 14px; }
.lead { font-size: 19px; line-height: 1.5; color: #3b3a36; margin-top: 18px; max-width: 620px; }
ul.lista { margin: 18px 0 0; padding: 0; list-style: none; display: grid; gap: 10px; font-size: 16px; line-height: 1.45; }
ul.lista li { padding-left: 18px; position: relative; }
ul.lista li::before { content: ''; position: absolute; left: 0; top: 9px; width: 7px; height: 7px; background: #1a1a18; }
/* direction opening */
.apertura { display: grid; grid-template-columns: 600px 1fr; background: var(--bg); color: var(--fg); }
.apertura .txt { padding: 52px 48px 40px 56px; display: flex; flex-direction: column; gap: 18px; }
.apertura .num { font: 500 15px/1 'Geist Mono', monospace; color: var(--mfg); }
.apertura h2 { font-family: var(--fd); font-weight: var(--dw); font-size: 76px; line-height: 0.98; letter-spacing: var(--dt); }
.apertura .frase { font-size: 21px; line-height: 1.35; font-family: var(--fs); }
.apertura .idea { font-size: 15.5px; line-height: 1.55; color: var(--mfg); font-family: var(--fs); }
.apertura .firma { font-size: 15px; line-height: 1.5; font-family: var(--fs); padding-top: 14px; border-top: 1px solid var(--bd); }
.apertura .firma b { display: block; font: 500 12.5px/1 'Geist Mono', monospace; color: var(--mfg); margin-bottom: 8px; }
.ejes { display: grid; grid-template-columns: 118px 1fr; gap: 7px 14px; font-size: 14px; font-family: var(--fs); padding-top: 14px; border-top: 1px solid var(--bd); }
.ejes dt { font: 500 12.5px/1.6 'Geist Mono', monospace; color: var(--mfg); }
.ejes dd { margin: 0; line-height: 1.45; }
.swatches { display: flex; gap: 0; margin-top: auto; height: 46px; }
.swatches span { flex: 1; position: relative; }
.swatches span:first-child { flex: 2; }
.contraste { font: 500 12.5px/1.4 'Geist Mono', monospace; color: var(--mfg); }
.apertura .img { position: relative; overflow: hidden; }
.apertura .img img { width: 100%; height: 100%; object-fit: cover; }
/* large screen */
.pantalla { background: #e9e8e3; display: grid; grid-template-columns: 1440px 160px; }
.pantalla > img { width: 1440px; height: 900px; display: block; }
.leyenda { padding: 26px 18px 26px 20px; display: flex; flex-direction: column; gap: 12px; font-size: 13.5px; line-height: 1.45; color: #3b3a36; background: #f3f2ee; }
.leyenda .n { font: 500 12.5px/1.3 'Geist Mono', monospace; color: #6b6a64; }
.leyenda h3 { font: 600 19px/1.15 'Geist', sans-serif; letter-spacing: -0.015em; color: #1a1a18; }
.leyenda .sz { font: 500 12.5px/1.3 'Geist Mono', monospace; color: #6b6a64; margin-top: auto; }
/* phone + components */
.movil { display: grid; grid-template-columns: 470px 1fr; background: #e9e8e3; }
.movil .tel { display: grid; place-items: center; background: var(--bg); }
.movil .tel img { height: 812px; width: auto; border-radius: 18px; box-shadow: 0 0 0 1px rgb(0 0 0 / 0.08); }
.movil .cat { position: relative; overflow: hidden; }
.movil .cat img { width: 100%; display: block; }
.movil .cat .rot { position: absolute; left: 0; right: 0; bottom: 0; padding: 14px 24px; background: #111110; color: #f3f2ee; font: 500 13.5px/1.3 'Geist', sans-serif; display: flex; gap: 18px; }
.movil .cat .rot span { color: #9a988f; font-family: 'Geist Mono', monospace; }
/* 16:9 full bleed */
.plena { background: #000; }
.plena img { width: 1600px; height: 900px; display: block; }
.plena .rot { position: absolute; left: 20px; bottom: 16px; background: rgb(0 0 0 / 0.72); color: #f3f2ee; padding: 7px 11px; font: 500 13px/1 'Geist Mono', monospace; }
/* tables */
table.cmp { width: 100%; border-collapse: collapse; font-size: 17px; margin-top: 34px; }
table.cmp th, table.cmp td { text-align: left; padding: 18px 14px; border-bottom: 1px solid #d8d6ce; vertical-align: top; line-height: 1.35; }
table.cmp th { font: 500 13.5px/1.25 'Geist Mono', monospace; color: #6b6a64; }
table.cmp td.dots { font-family: 'Geist Mono', monospace; letter-spacing: 2px; white-space: nowrap; font-size: 18px; }
table.cmp tr.elegida td { background: #fff; font-weight: 600; }
table.cmp td .sw { display: inline-block; width: 12px; height: 12px; margin-right: 8px; vertical-align: -1px; }
.mezclas { display: flex; flex-wrap: wrap; gap: 18px 22px; margin-top: 22px; }
.mezcla { width: 481px; height: 250px; background: #fff; overflow: hidden; }
.mezcla .imgs { display: flex; gap: 2px; height: 128px; }
.mezcla .imgs i { flex: 1; height: 128px; background-size: cover; background-position: top left; }
.mezcla h3 { font: 600 17px/1.2 'Geist', sans-serif; margin: 12px 16px 4px; }
.mezcla p { font-size: 14px; line-height: 1.4; color: #3b3a36; margin: 0 16px; }
.rec { background: #111110; color: #f3f2ee; }
.rec .titulo { color: #f3f2ee; }
.rec .lead { color: #c9c7bf; font-size: 21px; }
.rec ul.lista { font-size: 18px; gap: 14px; }
.rec ul.lista li::before { top: 11px; }
.rec ul.lista li::before { background: #f3f2ee; }
.rec .eyebrow { color: #9a988f; }
.antes img { position: absolute; }
"""


def _img(P, name, width=None):
    """2x JPEG for the PDF: lossless PNGs push it to tens of MB."""
    png = os.path.join(P.shots, name + '.png')
    rel = os.path.relpath(os.path.join(P.build, 'pdf', name + '.jpg'), P.root)
    jpg = os.path.join(P.root, rel)
    if not os.path.exists(png):
        return f'{P.shots_rel}/{name}.png'
    if not os.path.exists(jpg) or os.path.getmtime(jpg) < os.path.getmtime(png):
        try:
            from PIL import Image
        except ImportError:
            if not _NO_PIL:
                _NO_PIL.append(1)
                print('pdf: no Pillow: the PDF uses PNGs and gets heavier (pip install pillow in a venv)')
            return f'{P.shots_rel}/{name}.png'
        os.makedirs(os.path.dirname(jpg), exist_ok=True)
        im = Image.open(png).convert('RGB')
        if width and im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(jpg, quality=85, optimize=True, progressive=True)
    return rel


def _vars(d):
    tk, m = d['tokens']['light'], _mode_tokens(d)
    return (f'--bg:{m["background"]};--fg:{m["foreground"]};--mfg:{m["muted-foreground"]};--bd:{m["border"]};'
            f'--fd:{tk["font-display"]};--fs:{tk["font-sans"]};--dw:{tk.get("display-weight", 600)};--dt:{tk.get("display-tracking", "0")}')


def pdf(P, props, print_pdf):
    lang = props['lang']
    L = lambda key, **kw: E(t(lang, key, **kw))  # noqa: E731
    dirs, screens = props['directions'], props['screens']
    n, ns = len(dirs), len(screens)
    project = props.get('project', t(lang, 'project_default'))
    pages = []
    footer_left = L('footer', project=project, version=props.get('version', ''))
    footer = lambda txt: f'<div class="pie"><span>{footer_left}</span><span>{E(txt)}</span></div>'  # noqa: E731
    R = props.get('recommendation', {})
    rec_id = R.get('base', '')
    # Cover
    cover = props.get('cover_screen') or (screens[0]['id'] if screens else P.catalog_id)
    mos = ''.join(f'<figure><img src="{_img(P, d["id"] + "-" + cover)}"><figcaption><b>{i:02d}</b>{E(d["name"])}</figcaption></figure>'
                  for i, d in enumerate(dirs, 1))
    meta = L('cover_meta', n=n, dirs=t(lang, 'direction_one' if n == 1 else 'direction_many'), ns=ns, screens=t(lang, 'screen_one' if ns == 1 else 'screen_many'))
    rec_line = '<br>' + L('cover_recommended') + E(R['base_name']) if R.get('base_name') else ''
    pages.append(f'''<section class="pg portada"><div class="txt"><div class="mono" style="color:#9a988f;font-size:14px">{E(project)} · {E(props.get("date", ""))}</div>
      <h1>{E(props.get("title", project))}</h1><p class="ctx">{E(props.get("context", ""))}</p>
      <div class="meta">{meta}{rec_line}</div></div>
      <div class="mosaico">{mos}</div></section>''')
    # Before and after
    if os.path.exists(os.path.join(P.root, P.before_after)):
        pages.append(f'''<section class="pg" style="background:#111110"><img src="{P.before_after}" style="position:absolute;inset:0;width:1600px;height:900px;object-fit:contain"></section>''')
    # What stays fixed
    fixed = ''.join(f'<li>{E(x)}</li>' for x in props.get('fixed', []))
    varies = ''.join(f'<li>{E(x)}</li>' for x in props.get('varies', []))
    chars = t(lang, 'chars_one') if n == 1 else t(lang, 'chars_many', w=num(lang, n))
    the_screens = t(lang, 'the_screen_one') if ns == 1 else t(lang, 'the_screen_many', w=num(lang, ns, True))
    fictional = props.get('fictional_data', t(lang, 'fictional_default'))
    scr = ''.join(f'<li><b>{E(s["name"])}</b> · <span class="mono" style="font-size:14px">{E(s["note"])}</span></li>' for s in screens)
    pages.append(f'''<section class="pg"><div class="cols" style="grid-template-columns:1fr 1fr 1fr">
      <div><div class="eyebrow">{L("how_to_read")}</div><h2 class="titulo">{L("same_product", chars=chars)}</h2><p class="lead" style="font-size:17px">{E(props.get("how_to_read", ""))}</p></div>
      <div><div class="eyebrow">{L("fixed_in_all")}</div><ul class="lista">{fixed}</ul><div class="eyebrow" style="margin-top:34px">{L("varies")}</div><ul class="lista">{varies}</ul></div>
      <div><div class="eyebrow">{E(the_screens)}</div><ul class="lista">{scr}</ul><div class="eyebrow" style="margin-top:34px">{L("fictional_data")}</div><p class="lead" style="font-size:16px;margin-top:12px">{E(fictional)}</p></div>
      </div>{footer(t(lang, "what_compared"))}</section>''')
    axis_names = t(lang, 'axes')
    for i, d in enumerate(dirs, 1):
        tk = _mode_tokens(d)
        sw = ''.join(f'<span style="background:{tk[k]}" title="{k}"></span>' for k in ('background', 'card', 'foreground', 'muted-foreground', 'primary', 'border', 'success', 'destructive') if k in tk)
        axes = ''.join(f'<dt>{E(axis_names.get(k, k.capitalize()))}</dt><dd>{E(v)}</dd>' for k, v in d['axes'].items())
        c = d.get('contrast', {})
        pages.append(f'''<section class="pg apertura" style="{_vars(d)}"><div class="txt">
          <div class="num">{i:02d} / {n:02d}</div><h2>{E(d["name"])}</h2><p class="frase">{E(d["tagline"])}</p><p class="idea">{E(d["idea"])}</p>
          <div class="firma"><b>{L("signature_moment")}</b>{E(d["signature"])}</div><dl class="ejes">{axes}</dl>
          <div class="contraste">{L("aa_light")} {E(c.get("light", ""))}<br>{L("aa_dark")} {E(c.get("dark", ""))}</div>
          <div class="swatches">{sw}</div></div>
          <div class="img"><img src="{_img(P, d.get("opening_image", d["id"] + "-" + screens[0]["id"]))}" style="object-position:{E(d.get("opening_position", "left top"))}"></div></section>''')
        notes = d.get('notes', {})
        cat = os.path.join(P.shots, f'{d["id"]}-{P.catalog_id}.png')
        catimg = f'<img src="{_img(P, d["id"] + "-" + P.catalog_id)}">' if os.path.exists(cat) else ''
        for s in screens:
            kind = page_type(s)
            src = d['id'] + '-' + s['id']
            if kind == 'panel':
                note = ''.join(f'<p>{E(x)}</p>' for x in notes.get(s['id'], []))
                pages.append(f'''<section class="pg pantalla"><img src="{_img(P, src)}" style="object-fit:contain;object-position:top left"><div class="leyenda">
              <div class="n">{i:02d} · {E(d["name"])}</div><h3>{E(s["name"])}</h3>{note}<div class="sz">{E(s["note"])}<br>{L("capture_2x")}</div></div></section>''')
            elif kind == 'mobile':
                pages.append(f'''<section class="pg movil" style="{_vars(d)}"><div class="tel"><img src="{_img(P, src)}"></div>
          <div class="cat">{catimg}<div class="rot">{i:02d} · {E(d["name"])} <span>{L("mobile_left", name=s["name"], note=s["note"])}</span><span>{L("mobile_right")}</span></div></div></section>''')
            else:
                pages.append(f'''<section class="pg plena"><img src="{_img(P, src, 3200)}"><div class="rot">{i:02d} · {E(d["name"])} · {E(s["name"])} · {E(s["note"])}</div></section>''')
    # Comparison
    C = props.get('comparison') or {}
    rows = ''
    for d in dirs:
        v = C.get('values', {}).get(d['id'], [])
        chosen = ' class="elegida"' if d['id'] == rec_id else ''
        cells = ''.join(f'<td class="dots">{"●" * x}{"○" * (5 - x)}</td>' if isinstance(x, int) else f'<td>{E(x)}</td>' for x in v)
        rows += f'<tr{chosen}><td><span class="sw" style="background:{_mode_tokens(d)["primary"]}"></span><b>{E(d["name"])}</b></td>{cells}<td class="mono" style="font-size:12.5px">{E(d.get("contrast", {}).get("light", "").split(" ·")[0])}</td></tr>'
    head = ''.join(f'<th>{E(c)}</th>' for c in C.get('columns', []))
    cmp_title = t(lang, 'cmp_title_one') if n == 1 else t(lang, 'cmp_title_many', w=num(lang, n, True))
    pages.append(f'''<section class="pg"><div class="cols" style="grid-template-columns:1fr"><div>
      <div class="eyebrow">{L("comparison")}</div><h2 class="titulo">{E(cmp_title)}</h2>
      <table class="cmp"><tr><th>{L("direction")}</th>{head}<th>{L("contrast_aa")}</th></tr>{rows}</table>
      <p class="lead" style="font-size:15px;max-width:none;margin-top:16px">{E(C.get("note", ""))}</p></div></div>{footer(t(lang, "comparison"))}</section>''')
    # Mixes
    mz = ''
    for m in props.get('mixes', []):
        a, b = m['images']
        mz += f'<div class="mezcla"><div class="imgs"><i style="background-image:url({_img(P, a)})"></i><i style="background-image:url({_img(P, b)})"></i></div><h3>{E(m["title"])}</h3><p>{E(m["text"])}</p></div>'
    if mz:
        pages.append(f'''<section class="pg"><div class="cols" style="grid-template-columns:1fr"><div>
      <div class="eyebrow">{L("mix_guide")}</div><h2 class="titulo" style="font-size:38px">{L("mix_title")}</h2>
      <p class="lead" style="font-size:16px;max-width:1200px;margin-top:12px">{E(props.get("mix_rule", ""))}</p><div class="mezclas">{mz}</div></div></div>{footer(t(lang, "mixes"))}</section>''')
    # Recommendation
    why = ''.join(f'<li>{E(x)}</li>' for x in R.get('why', []))
    steps = ''.join(f'<li>{E(x)}</li>' for x in R.get('steps', []))
    if R:
        pages.append(f'''<section class="pg rec"><div class="cols" style="grid-template-columns:1.1fr 1fr">
      <div><div class="eyebrow">{L("recommendation")}</div><h2 class="titulo" style="font-size:52px">{E(R.get("title", ""))}</h2><p class="lead">{E(R.get("summary", ""))}</p><ul class="lista">{why}</ul>
        <p class="lead" style="font-size:16px;margin-top:22px"><b style="color:#f3f2ee">{L("if_priority")}</b> {E(R.get("alternative", ""))}</p></div>
      <div><div class="eyebrow">{L("how_implemented")}</div><ul class="lista">{steps}</ul>
        <p class="lead" style="font-size:18px;margin-top:30px;color:#f3f2ee">{E(R.get("question", ""))}</p></div>
      </div><div class="pie" style="color:#9a988f"><span>{footer_left}</span><span>{L("recommendation")}</span></div></section>''')
    doc = f'''<!doctype html><html lang="{E(lang)}"><head><meta charset="utf-8"><title>{E(props.get("title", project))}</title>
<link rel="stylesheet" href="{os.path.relpath(P.fonts_css, P.root)}"><style>{CSS_PDF}</style></head><body>{"".join(pages)}</body></html>'''
    path = os.path.join(P.root, P.pdf_html)
    open(path, 'w').write(doc)
    print_pdf(path, os.path.join(P.root, P.pdf))
    print('pdf:', len(pages), 'pages ->', os.path.join(P.root, P.pdf))


# ---------------------------------------------------------------- gallery
def gallery(P, props):
    lang = props['lang']
    items = []
    for i, d in enumerate(props['directions'], 1):
        for s in props['screens'] + [{'id': P.catalog_id, 'name': t(lang, 'g_components'), 'note': t(lang, 'g_catalog_note')}]:
            f = f'{P.shots_rel}/{d["id"]}-{s["id"]}.png'
            if os.path.exists(os.path.join(P.root, f)):
                items.append({'dir': d['id'], 'n': f'{i:02d}', 'name': d['name'], 'screen': s['id'], 'title': s['name'], 'note': s['note'], 'src': f})
    dirs = [{'id': d['id'], 'name': d['name'], 'tagline': d['tagline'], 'color': _mode_tokens(d)['primary']} for d in props['directions']]
    scr = [{'id': s['id'], 'name': s['name']} for s in props['screens']] + [{'id': P.catalog_id, 'name': t(lang, 'g_components')}]
    labels = {k[2:]: t(lang, k) for k in ('g_all_dirs', 'g_all_screens', 'g_recommended')}
    data = {'items': items, 'dirs': dirs, 'screens': scr, 'rec': props.get('recommendation', {}).get('base', ''), 't': labels, 'catalog': P.catalog_id}
    doc = (GALLERY.replace('__LANG__', E(lang)).replace('__TITLE__', E(props.get('title', props.get('project', t(lang, 'project_default')))))
           .replace('__FONTS__', os.path.relpath(P.fonts_css, P.root)).replace('__PDF__', P.pdf).replace('__CONTRAST__', P.contrast)
           .replace('__DATA__', json.dumps(data, ensure_ascii=False)))
    for k in ('g_pdf', 'g_contrast', 'g_enlarged', 'g_prev', 'g_next', 'g_real_size', 'g_close'):
        doc = doc.replace(f'__{k.upper()}__', E(t(lang, k)))
    open(os.path.join(P.root, 'index.html'), 'w').write(doc)
    print('gallery: index.html with', len(items), 'images')


GALLERY = r'''<!doctype html><html lang="__LANG__"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link rel="stylesheet" href="__FONTS__">
<style>
:root { --bg:#f3f2ee; --fg:#1a1a18; --mfg:#5f5e58; --bd:#d9d7cf; --card:#fff; }
@media (prefers-color-scheme: dark) { :root { --bg:#111110; --fg:#f0efea; --mfg:#a3a199; --bd:#2c2b28; --card:#1a1a19; } }
* { box-sizing: border-box; } body { margin:0; background:var(--bg); color:var(--fg); font:15px/1.5 'Geist', system-ui, sans-serif; }
header { position:sticky; top:0; z-index:5; background:var(--bg); border-bottom:1px solid var(--bd); padding:16px 24px; display:flex; flex-wrap:wrap; gap:12px 24px; align-items:center; }
h1 { font-size:20px; letter-spacing:-0.02em; margin:0; font-weight:600; }
.links { display:flex; gap:16px; font-size:14px; } .links a { color:var(--fg); }
.filters { display:flex; flex-wrap:wrap; gap:6px; width:100%; }
.filters button { height:34px; padding:0 12px; border:1px solid var(--bd); background:var(--card); color:var(--fg); border-radius:8px; font:500 14px 'Geist', sans-serif; cursor:pointer; display:inline-flex; align-items:center; gap:8px; }
.filters button[aria-pressed="true"] { background:var(--fg); color:var(--bg); border-color:var(--fg); }
.filters .sw { width:10px; height:10px; border-radius:2px; }
main { padding:24px; display:grid; grid-template-columns:repeat(auto-fill, minmax(min(100%, 520px), 1fr)); gap:28px 24px; }
figure { margin:0; cursor:zoom-in; }
figure .frame { position:relative; background:var(--card); border:1px solid var(--bd); aspect-ratio:16/10; overflow:hidden; }
figure .frame img { position:absolute; inset:0; width:100%; height:100%; object-fit:contain; display:block; }
figure.catalog .frame img { object-fit:cover; object-position:top; }
figcaption { display:flex; gap:10px; align-items:baseline; margin-top:8px; font-size:14px; }
figcaption b { font-weight:600; } figcaption span { color:var(--mfg); font:13px 'Geist Mono', monospace; }
.box { position:fixed; inset:0; background:rgb(0 0 0 / 0.92); display:none; z-index:10; }
.box[open] { display:grid; grid-template-rows:auto 1fr; }
.box .bar { display:flex; gap:12px; align-items:center; padding:12px 16px; color:#f0efea; font-size:14px; }
.box .bar button { height:36px; min-width:44px; border:1px solid #444; background:#1a1a19; color:#f0efea; border-radius:8px; cursor:pointer; font:500 14px 'Geist', sans-serif; }
.box .view { overflow:auto; display:grid; place-items:center; padding:0 16px 16px; }
.box .view img { max-width:100%; max-height:calc(100vh - 80px); }
.box .view.real img { max-width:none; max-height:none; }
</style></head><body>
<header><h1>__TITLE__</h1><nav class="links"><a href="__PDF__">__G_PDF__</a><a href="README.md">README</a><a href="__CONTRAST__">__G_CONTRAST__</a></nav>
<div class="filters" id="fd"></div><div class="filters" id="fs"></div></header>
<main id="grid"></main>
<div class="box" id="box" role="dialog" aria-label="__G_ENLARGED__"><div class="bar"><button id="prev" aria-label="__G_PREV__">←</button><button id="next" aria-label="__G_NEXT__">→</button><span id="cap"></span><span style="flex:1"></span><button id="zoom">__G_REAL_SIZE__</button><button id="close">__G_CLOSE__</button></div><div class="view" id="view"><img id="big" alt=""></div></div>
<script>
const D = __DATA__, ALL = '*';
let fDir = ALL, fScreen = ALL, vis = [], idx = 0;
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
function button(cont, id, txt, color, group) {
  const b = document.createElement('button'); b.dataset.id = id; b.setAttribute('aria-pressed', id === ALL);
  b.innerHTML = (color ? `<span class="sw" style="background:${color}"></span>` : '') + esc(txt);
  b.onclick = () => { if (group === 'd') fDir = id; else fScreen = id; cont.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x.dataset.id === id)); paint(); };
  cont.appendChild(b);
}
button($('#fd'), ALL, D.t.all_dirs, null, 'd');
D.dirs.forEach((d, i) => button($('#fd'), d.id, `${String(i + 1).padStart(2, '0')} ${d.name}${d.id === D.rec ? ' · ' + D.t.recommended : ''}`, d.color, 'd'));
button($('#fs'), ALL, D.t.all_screens, null, 's');
D.screens.forEach(s => button($('#fs'), s.id, s.name, null, 's'));
function paint() {
  vis = D.items.filter(x => (fDir === ALL || x.dir === fDir) && (fScreen === ALL || x.screen === fScreen));
  $('#grid').innerHTML = vis.map((x, i) => `<figure data-i="${i}"${x.screen === D.catalog ? ' class="catalog"' : ''}><div class="frame"><img loading="lazy" src="${x.src}" alt="${esc(x.name)}: ${esc(x.title)}"></div><figcaption><b>${x.n} ${esc(x.name)}</b>${esc(x.title)}<span>${esc(x.note)}</span></figcaption></figure>`).join('');
  document.querySelectorAll('figure').forEach(f => f.onclick = () => open_(+f.dataset.i));
}
function open_(i) { idx = (i + vis.length) % vis.length; const x = vis[idx]; $('#big').src = x.src; $('#cap').textContent = `${x.n} ${x.name} · ${x.title} · ${x.note}`; $('#box').setAttribute('open', ''); }
$('#prev').onclick = () => open_(idx - 1); $('#next').onclick = () => open_(idx + 1);
$('#close').onclick = () => $('#box').removeAttribute('open');
$('#zoom').onclick = () => $('#view').classList.toggle('real');
document.addEventListener('keydown', e => { if (!$('#box').hasAttribute('open')) return; if (e.key === 'Escape') $('#close').click(); if (e.key === 'ArrowLeft') open_(idx - 1); if (e.key === 'ArrowRight') open_(idx + 1); });
paint();
</script></body></html>'''


# ---------------------------------------------------------------- review with vision
def review(P, props):
    pdf_ = os.path.join(P.root, P.pdf)
    if not os.path.exists(pdf_):
        return
    tmp = os.path.join(P.build, 'rev')
    os.makedirs(tmp, exist_ok=True)
    for f in glob.glob(os.path.join(tmp, '*.png')):
        os.remove(f)
    if not shutil.which('pdftoppm'):
        print('review: no pdftoppm (poppler-utils); skipping the review sheets')
        return
    subprocess.run(['pdftoppm', '-r', '36', '-png', pdf_, os.path.join(tmp, 'p')], check=True)
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print('review: no Pillow; look at the pages in', tmp)
        return
    fs = sorted(glob.glob(os.path.join(tmp, 'p-*.png')))
    for h in range(0, len(fs), 12):
        group = [Image.open(f) for f in fs[h:h + 12]]
        w, hh = group[0].size
        sheet = Image.new('RGB', (3 * w + 4 * 10, 4 * (hh + 24) + 10), '#777')
        dr = ImageDraw.Draw(sheet)
        for k, im in enumerate(group):
            x, y = 10 + (k % 3) * (w + 10), 10 + (k // 3) * (hh + 24)
            sheet.paste(im, (x, y + 18))
            dr.text((x, y + 2), t(props['lang'], 'review_page', n=h + k + 1), fill='white')
        sheet.save(os.path.join(P.build, f'{P.review}-{h // 12 + 1}.png'))
    print('review: sheets in', P.build, '(inspect them with vision; criteria in references/review.md)')
