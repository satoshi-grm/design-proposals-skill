"""Salidas del cuadernillo: design.md por dirección, PDF 16:9, galería navegable y hojas de revisión.

Lo llama build.py; no se usa solo. Lee lo mismo: <carpeta>/fuente/propuesta.json y los PNG de pantallas/.
"""
import glob
import html
import json
import os
import shutil
import subprocess

E = html.escape
SKILL_NOMBRE = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SIN_PIL = []

# Componentes de la biblioteca con sus estados: van a cada design.md para el handoff.
COMPONENTES = [
    ('App shell', 'sidebar expandido y en riel, selector de organización, ítem activo, contador, aviso', 'shell.css'),
    ('Barra de comandos ⌘K', 'cerrada, abierta, con resultados agrupados, ítem resaltado, sin resultados', 'overlays.css'),
    ('Tabla de datos', 'cargando (skeleton), vacía, con filtros, orden asc/desc, fila hover y seleccionada, selección parcial, acciones en lote, error', 'tabla.css'),
    ('Estados vacíos', 'primer uso con CTA, sin resultados de filtro, error con reintento', 'estados.css'),
    ('Skeletons y carga', 'filas, tarjetas, texto, spinner en botón; sin shimmer con movimiento reducido', 'estados.css'),
    ('Toasts', 'éxito, error, con acción «Deshacer», apilados', 'overlays.css'),
    ('Modal y panel lateral', 'abierto, confirmación destructiva, con formulario, cerrando', 'overlays.css'),
    ('Formularios', 'vacío, foco, lleno, error con ícono y texto, éxito, deshabilitado, contador de caracteres, prefijo', 'formularios.css'),
    ('Tabs y segmented', 'seleccionado, hover, foco, con contador', 'base.css'),
    ('Checklist de onboarding', 'paso hecho, actual, pendiente; progreso «2 de 4»', 'paginas.css'),
    ('Página de ajustes', 'secciones con regla, zona de peligro, guardado', 'paginas.css'),
    ('Planes y facturación', 'plan actual, mejora, límite alcanzado, medidores de uso, facturas', 'paginas.css'),
    ('Gráficos en SVG', 'barras, línea, franja de 24 h, sin datos', 'graficos.css'),
    ('Avatares y presencia', 'con iniciales, con foto, en línea, pila', 'base.css'),
    ('Badges de estado', 'activo, pendiente, error, info; siempre con punto y texto', 'base.css'),
    ('Breadcrumbs', 'con enlace, actual, truncado', 'base.css'),
    ('Paginación', 'primera, intermedia, última, deshabilitada', 'tabla.css'),
    ('Modo oscuro', 'mismos componentes con data-mode="dark"; superficies que se aclaran al subir', 'tokens.css'),
]


def _rel(carpeta, p):
    return os.path.relpath(p, carpeta)


# ---------------------------------------------------------------- design.md
def docs(carpeta, props):
    proyecto = props.get('proyecto', 'Proyecto')
    pos = props.get('contexto', '') or 'Producto propio; el contenido del usuario es la estrella.'
    for i, d in enumerate(props['direcciones'], 1):
        t, o = d['tokens']['light'], d['tokens']['dark']
        colores = [k for k in t if t[k].startswith('#')]
        fm = ['---', 'version: design-md-1', f'name: "{proyecto} · {d["nombre"]}"', f'source: {SKILL_NOMBRE} {props.get("fecha", "")}',
              f'captured_at: {props.get("fecha", "")}', 'description: |', f'  {d["idea"]}', 'colors:']
        fm += [f'  {k}: "{t[k]}"' for k in colores]
        fm += ['typography:',
               f'  display: {{ fontFamily: "{t["font-display"]}", fontSize: {t.get("text-xl", "28px")}, fontWeight: {t.get("display-weight", 600)}, letterSpacing: {t.get("display-tracking", "0")} }}',
               f'  body: {{ fontFamily: "{t["font-sans"]}", fontSize: {t.get("text-base", "14px")}, fontWeight: 400, lineHeight: 1.5 }}',
               f'  caption-mono: {{ fontFamily: "{t["font-mono"]}", fontSize: 12px, fontWeight: 400 }}',
               'spacing:', '  base: 4px', '  scale: [4, 8, 12, 16, 24, 32, 40, 48]',
               'rounded:', f'  sm: {t.get("radius-sm", "4px")}', f'  md: {t.get("radius", "8px")}', f'  lg: {t.get("radius-lg", "12px")}',
               'components:',
               f'  button-primary: {{ backgroundColor: "{{colors.primary}}", textColor: "{{colors.primary-foreground}}", rounded: "{{rounded.md}}", height: {t.get("control-h", "32px")} }}',
               f'  input: {{ backgroundColor: "{{colors.card}}", border: "1px solid {{colors.input}}", focusRing: "2px solid {{colors.ring}}", rounded: "{{rounded.md}}" }}',
               '  badge: { rounded: 999px, typography: "{typography.caption-mono}" }',
               f'  table-row: {{ height: {t.get("row-h", "44px")}, border: "1px solid {{colors.border}}" }}',
               '  sidebar-item: { backgroundColor: "{colors.sidebar}", textColor: "{colors.sidebar-muted}", rounded: "{rounded.md}" }',
               '---', '']
        filas_color = '\n'.join(f'| `{k}` | {t[k]} | {o.get(k, "—")} | ✅ |' for k in colores)
        comp = '\n'.join(f'| {n} | {e} | `{f}` |' for n, e, f in COMPONENTES)
        pant = '\n'.join(f'- `pantallas/{d["id"]}-{p["id"]}.png`: {p["nombre"]} ({p["nota"]})' for p in props['pantallas'])
        ej = d['ejes']
        grilla = '\n'.join(f'- {p["nombre"]}: {p.get("ancho", "?")}×{p.get("alto", "?")} px ({p.get("nota", "")}).' for p in props['pantallas'])
        nombres = ', '.join(p['nombre'] for p in props['pantallas'])
        cuerpo = f"""# Design Analysis: {proyecto} · {d['nombre']}

> Dirección {i} de {len(props['direcciones'])} del cuadernillo `{SKILL_NOMBRE}` ({props.get('fecha', '')}). Emphasis: design system (prescriptivo: es una propuesta, no el análisis de un sitio existente).

## Source
Propuesta generada con la skill `{SKILL_NOMBRE}`: tokens en `fuente/propuesta.json`, composición en `fuente/direcciones/{d['id']}.css`, pantallas renderizadas con Chrome headless a 2x. Referencias: {d['referencias']}.

## TL;DR
{d['frase']} {d['idea']} Momento firma: {d['firma']}

## 1. Visual identity
### 1.1 Surface description
- Personality: {ej['temperatura']}; densidad {ej['densidad'].lower()}. ✅
- Mood: {d['frase']} ✅
- Stylistic references: {d['referencias']}. ✅
- Information density: {ej['densidad']}. ✅
- Implicit positioning: {pos} ✅

### 1.2 Brand voice / Atmosphere
{d['idea']}

### 1.3 The "ONE brand thing"
- La cosa: {d['firma']}
- Por qué: sale del mundo del cliente, no de cómo se ven las herramientas del rubro.
- Cómo se contiene el resto: un solo acento (`{{colors.primary}}` {t['primary']}), estados siempre con texto o ícono.
- Dónde no aparece: en las superficies que muestran la marca del cliente, manda esa marca; la firma cambia la composición, nunca la marca.

## 2. Design System (tokens)
### 2.1 Colors
| Token | Claro | Oscuro | Confianza |
|---|---|---|---|
{filas_color}

### 2.2 Typography
Fuentes: {', '.join(d['fuentes'])} (Google Fonts, OFL). Escala: 12 (metadatos cortos), {t.get('text-sm', '13px')}, {t.get('text-base', '14px')} (cuerpo del panel), 16, 20, {t.get('text-xl', '28px')} (títulos de página). Interlineado 1,5 en texto y 1,1–1,2 en títulos. Cifras tabulares en tablas, duraciones y horarios con `{{typography.caption-mono}}`.

| Token | Familia | Uso |
|---|---|---|
| `display` | {t['font-display']} | Títulos de página y de sección |
| `body` | {t['font-sans']} | Interfaz y texto |
| `caption-mono` | {t['font-mono']} | Duraciones, códigos, versiones, horarios |

### 2.3 Spacing
Base 4 px. Grupos internos a 8, entre grupos 16–24, entre regiones 32–40. Alto de control {t.get('control-h', '32px')}; filas de tabla {t.get('row-h', '44px')}.

### 2.4 Radii
`sm` {t.get('radius-sm')} · `md` {t.get('radius')} (controles) · `lg` {t.get('radius-lg')} (diálogos y paneles). Los radios anidados se achican hacia adentro. Forma: {ej['forma']}.

### 2.5 Elevation system
| Level | Name | Treatment | Use |
|---|---|---|---|
| 0 | Plano | Sin sombra; separación por regla de 1 px o por tono | Regiones, tablas, paneles |
| 1 | Flotante | `--shadow-float`, sin borde fino a la vez | Menús, ⌘K, toasts, diálogos, el ítem que se arrastra |

### 2.6 Borders
1 px `{{colors.border}}` para separar; `{{colors.input}}` ({t['input']}) en controles (≥ 3:1); foco 2 px `{{colors.ring}}` con separación de 2 px.

### 2.7 Accessibility quick-check
Claro: {d.get('contraste', {}).get('light', 's/d')}. Oscuro: {d.get('contraste', {}).get('dark', 's/d')}. Medido con `contraste.py` (WCAG 2.x) sobre los pares texto/fondo, bordes de control y foco; detalle en `contraste.txt`.

## 3. Components Inventory
### 3.1 Generic components
#### button-primary
Una sola acción principal por pantalla («Guardar», «Crear»). Estados: hover, presionado (escala 0,97), foco, deshabilitado, cargando.
#### input
Label arriba, ayuda o error abajo con ícono; contador cuando hay límite. Estados: vacío, foco, lleno, error, deshabilitado.
#### badge
Punto + texto: Activo, Pendiente, Error. Nunca solo color.
#### table-row
Alto {t.get('row-h', '44px')}, hover, seleccionada con tinte del acento, cifras tabulares a la derecha.
#### sidebar-item
Ícono de 20 px + etiqueta; activo con `{{colors.sidebar-accent}}`; contador en mono.

Biblioteca completa (HTML + CSS con tokens, en la skill `{SKILL_NOMBRE}/templates/componentes/`):

| Componente | Estados | Archivo |
|---|---|---|
{comp}

### 3.2 Signature components
- **{d['firma']}** Aparece en las pantallas del cuadernillo ({nombres}). Imagen: {ej['imagen']}. Movimiento: {ej['movimiento']}.

## 4. Layout & Composition
### 4.1 Grid & containers
Pantallas del cuadernillo (ver `pantallas/`):
{grilla}
Contenedor máximo de 1440 px; sidebar fija o en riel, topbar de 56 px, paneles laterales como hoja sobre el contenido.
### 4.2 Composition patterns
Un punto focal por pantalla; la acción principal a la vista sin scroll; regiones separadas por regla o tono antes que por tarjetas.
### 4.3 Responsive behavior
| Breakpoint | Comportamiento |
|---|---|
| ≥ 1280 | Layout completo; paneles laterales fijos |
| 768–1279 | Paneles laterales como hoja flotante; sidebar en riel |
| < 768 | Una columna; navegación en barra inferior o menú; tablas pasan a lista |
Áreas de toque de 44 px en táctil.
### 4.4 Image behavior
- {ej['imagen']}.
- Imágenes del cliente sin filtros de color; los estados inactivos o con error se marcan con texto, no solo atenuando la imagen.

## 5. Reconstruction Notes
Stack sugerido: Next.js + Tailwind v4 + shadcn/ui. Pegá `tokens.css` en `globals.css`: pisa `:root` y `.dark` de shadcn y agrega `@theme inline`. Quick wins: fuentes con `next/font`, íconos Lucide, badges con punto. Tricky bits: el momento firma (CSS propio en un componente), cifras tabulares en todas las tablas, el foco diseñado.

| Layer | Confidence | Why |
|---|---|---|
| Tokens | ✅ | Definidos y medidos |
| Componentes | ✅ | Biblioteca con estados |
| Firma | ⚠️ | Validar con usuarios reales |

## 6. Do's and Don'ts
### Do
- Reservá `{{colors.primary}}` ({t['primary']}) para la acción principal y la selección.
- Cifras, duraciones y horarios en `{{typography.caption-mono}}` ({t['font-mono'].split(',')[0]}).
- Estados con punto y texto: «Activo», «Error».
- Sombra solo en lo que flota (`--shadow-float`).
- En las superficies que muestran la marca del cliente, esa marca manda.
### Don't
- No sumes un segundo acento de color.
- No uses tarjetas de cifras grandes por defecto: frase de estado y lista de lo que necesita atención.
- No envuelvas cada región en una tarjeta.
- No tapes la marca del cliente donde manda.
- No uses la firma como decoración en todas partes: solo donde la definió el cuadernillo.

## 7. Open Questions
- Validar la dirección con usuarios reales antes de cerrar.
- Logo del producto con esta dirección.

## 8. Companion files
- `tokens.css`: CSS variables (`:root`, `.dark`) + Tailwind v4 `@theme inline`, nombres de shadcn/ui.
- `contraste.txt` (raíz del cuadernillo).
{pant}
- `pantallas/{d['id']}-componentes.png`: catálogo de componentes con este tema.

## Para la especificación (listo para pegar)
**Sistema de diseño: «{d['nombre']}».** {d['idea']} Firma: {d['firma']} Tokens: `docs/propuestas/.../{d['id']}/tokens.css` (shadcn/ui + Tailwind v4). Tipografía: {', '.join(d['fuentes'])}. Forma: {ej['forma']}. Densidad: {ej['densidad']}. Movimiento: {ej['movimiento']}.
**Accesibilidad.** WCAG 2.2 AA; {d.get('contraste', {}).get('light', '')} (claro) y {d.get('contraste', {}).get('dark', '')} (oscuro); límites medidos en limites.txt.
"""
        dest = os.path.join(carpeta, d['id'])
        os.makedirs(dest, exist_ok=True)
        open(os.path.join(dest, 'design.md'), 'w').write('\n'.join(fm) + cuerpo)
    print('docs: design.md ×', len(props['direcciones']))


# ---------------------------------------------------------------- PDF 16:9
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
/* portada */
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
/* texto */
.cols { position: absolute; inset: 56px 56px 70px; display: grid; gap: 48px; }
.eyebrow { font: 500 14px/1 'Geist Mono', monospace; color: #6b6a64; }
.titulo { font: 600 44px/1.05 'Geist', sans-serif; letter-spacing: -0.03em; margin-top: 14px; }
.lead { font-size: 19px; line-height: 1.5; color: #3b3a36; margin-top: 18px; max-width: 620px; }
ul.lista { margin: 18px 0 0; padding: 0; list-style: none; display: grid; gap: 10px; font-size: 16px; line-height: 1.45; }
ul.lista li { padding-left: 18px; position: relative; }
ul.lista li::before { content: ''; position: absolute; left: 0; top: 9px; width: 7px; height: 7px; background: #1a1a18; }
/* apertura de dirección */
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
/* pantalla grande */
.pantalla { background: #e9e8e3; display: grid; grid-template-columns: 1440px 160px; }
.pantalla > img { width: 1440px; height: 900px; display: block; }
.leyenda { padding: 26px 18px 26px 20px; display: flex; flex-direction: column; gap: 12px; font-size: 13.5px; line-height: 1.45; color: #3b3a36; background: #f3f2ee; }
.leyenda .n { font: 500 12.5px/1.3 'Geist Mono', monospace; color: #6b6a64; }
.leyenda h3 { font: 600 19px/1.15 'Geist', sans-serif; letter-spacing: -0.015em; color: #1a1a18; }
.leyenda .sz { font: 500 12.5px/1.3 'Geist Mono', monospace; color: #6b6a64; margin-top: auto; }
/* celular + componentes */
.movil { display: grid; grid-template-columns: 470px 1fr; background: #e9e8e3; }
.movil .tel { display: grid; place-items: center; background: var(--bg); }
.movil .tel img { height: 812px; width: auto; border-radius: 18px; box-shadow: 0 0 0 1px rgb(0 0 0 / 0.08); }
.movil .cat { position: relative; overflow: hidden; }
.movil .cat img { width: 100%; display: block; }
.movil .cat .rot { position: absolute; left: 0; right: 0; bottom: 0; padding: 14px 24px; background: #111110; color: #f3f2ee; font: 500 13.5px/1.3 'Geist', sans-serif; display: flex; gap: 18px; }
.movil .cat .rot span { color: #9a988f; font-family: 'Geist Mono', monospace; }
/* 16:9 a pantalla completa */
.plena { background: #000; }
.plena img { width: 1600px; height: 900px; display: block; }
.plena .rot { position: absolute; left: 20px; bottom: 16px; background: rgb(0 0 0 / 0.72); color: #f3f2ee; padding: 7px 11px; font: 500 13px/1 'Geist Mono', monospace; }
/* tablas */
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


def _img(carpeta, nombre, ancho=None):
    """JPEG 2x para el PDF: los PNG sin pérdida lo llevan a decenas de MB."""
    png = os.path.join(carpeta, 'pantallas', nombre + '.png')
    rel = f'fuente/.build/pdf/{nombre}.jpg'
    jpg = os.path.join(carpeta, rel)
    if not os.path.exists(png):
        return f'pantallas/{nombre}.png'
    if not os.path.exists(jpg) or os.path.getmtime(jpg) < os.path.getmtime(png):
        try:
            from PIL import Image
        except ImportError:
            if not _SIN_PIL:
                _SIN_PIL.append(1)
                print('pdf: sin Pillow: el PDF usa PNG y pesa más (pip install pillow en un venv)')
            return f'pantallas/{nombre}.png'
        os.makedirs(os.path.dirname(jpg), exist_ok=True)
        im = Image.open(png).convert('RGB')
        if ancho and im.width > ancho:
            im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
        im.save(jpg, quality=85, optimize=True, progressive=True)
    return rel


def _vars(d):
    t, dk = d['tokens']['light'], d['tokens']['dark']
    m = dk if d.get('modo') == 'dark' else t
    return (f'--bg:{m["background"]};--fg:{m["foreground"]};--mfg:{m["muted-foreground"]};--bd:{m["border"]};'
            f'--fd:{t["font-display"]};--fs:{t["font-sans"]};--dw:{t.get("display-weight", 600)};--dt:{t.get("display-tracking", "0")}')


_NUM = ['cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho']


def _pal(n, fem=False):
    return ('una' if fem else 'uno') if n == 1 else _NUM[n] if 0 <= n <= 8 else str(n)


def pdf(carpeta, props, imprimir):
    P = props
    dirs = P['direcciones']
    n, np_ = len(dirs), len(P['pantallas'])
    proyecto = P.get('proyecto', 'Proyecto')
    pags = []
    pie = lambda txt: f'<div class="pie"><span>{E(proyecto)} · direcciones visuales {E(P.get("version", ""))}</span><span>{E(txt)}</span></div>'  # noqa: E731
    rec_id = P.get('recomendacion', {}).get('base', '')
    # Portada
    portada = P.get('portada_pantalla') or (P['pantallas'][0]['id'] if P['pantallas'] else 'componentes')
    mos = ''.join(f'<figure><img src="{_img(carpeta, d["id"] + "-" + portada)}"><figcaption><b>{i:02d}</b>{E(d["nombre"])}</figcaption></figure>'
                  for i, d in enumerate(dirs, 1))
    pags.append(f'''<section class="pg portada"><div class="txt"><div class="mono" style="color:#9a988f;font-size:14px">{E(proyecto)} · {E(P.get("fecha", ""))}</div>
      <h1>{E(P.get("titulo", proyecto))}</h1><p class="ctx">{E(P.get("contexto", ""))}</p>
      <div class="meta">{n} {"dirección" if n == 1 else "direcciones"} · {np_} {"pantalla" if np_ == 1 else "pantallas"} cada una · mismos datos{"<br>Recomendada: " + E(P["recomendacion"]["base_nombre"]) if P.get("recomendacion", {}).get("base_nombre") else ""}</div></div>
      <div class="mosaico">{mos}</div></section>''')
    # Antes y después
    if os.path.exists(os.path.join(carpeta, 'antes-despues.png')):
        pags.append(f'''<section class="pg" style="background:#111110"><img src="antes-despues.png" style="position:absolute;inset:0;width:1600px;height:900px;object-fit:contain"></section>''')
    # Qué queda fijo
    fijo = ''.join(f'<li>{E(x)}</li>' for x in P.get('fijo', []))
    varia = ''.join(f'<li>{E(x)}</li>' for x in P.get('varia', []))
    caracteres = 'un carácter' if n == 1 else f'{_pal(n)} caracteres'
    las_pant = 'La pantalla' if np_ == 1 else f'Las {_pal(np_, True)} pantallas'
    ficticios = P.get('datos_ficticios', 'Datos inventados para comparar; los mismos en todas las direcciones.')
    pant = ''.join(f'<li><b>{E(p["nombre"])}</b> · <span class="mono" style="font-size:14px">{E(p["nota"])}</span></li>' for p in P['pantallas'])
    pags.append(f'''<section class="pg"><div class="cols" style="grid-template-columns:1fr 1fr 1fr">
      <div><div class="eyebrow">Cómo leer esto</div><h2 class="titulo">Mismo producto, {caracteres}</h2><p class="lead" style="font-size:17px">{E(P.get("como_leer", ""))}</p></div>
      <div><div class="eyebrow">Queda fijo en todas</div><ul class="lista">{fijo}</ul><div class="eyebrow" style="margin-top:34px">Cambia entre direcciones</div><ul class="lista">{varia}</ul></div>
      <div><div class="eyebrow">{las_pant}</div><ul class="lista">{pant}</ul><div class="eyebrow" style="margin-top:34px">Datos ficticios</div><p class="lead" style="font-size:16px;margin-top:12px">{E(ficticios)}</p></div>
      </div>{pie("Qué se compara")}</section>''')
    for i, d in enumerate(dirs, 1):
        t = d['tokens']['dark'] if d.get('modo') == 'dark' else d['tokens']['light']
        sw = ''.join(f'<span style="background:{t[k]}" title="{k}"></span>' for k in ('background', 'card', 'foreground', 'muted-foreground', 'primary', 'border', 'success', 'destructive') if k in t)
        ejes = ''.join(f'<dt>{E(k.capitalize() if k != "tipografia" else "Tipografía")}</dt><dd>{E(v)}</dd>' for k, v in d['ejes'].items())
        c = d.get('contraste', {})
        pags.append(f'''<section class="pg apertura" style="{_vars(d)}"><div class="txt">
          <div class="num">{i:02d} / {n:02d}</div><h2>{E(d["nombre"])}</h2><p class="frase">{E(d["frase"])}</p><p class="idea">{E(d["idea"])}</p>
          <div class="firma"><b>Momento firma</b>{E(d["firma"])}</div><dl class="ejes">{ejes}</dl>
          <div class="contraste">AA claro {E(c.get("light", ""))}<br>AA oscuro {E(c.get("dark", ""))}</div>
          <div class="swatches">{sw}</div></div>
          <div class="img"><img src="{_img(carpeta, d.get("apertura_img", d["id"] + "-" + P["pantallas"][0]["id"]))}" style="object-position:{E(d.get("apertura_pos", "left top"))}"></div></section>''')
        notas = d.get('notas', {})
        cat = os.path.join(carpeta, 'pantallas', d['id'] + '-componentes.png')
        catimg = f'<img src="{_img(carpeta, d["id"] + "-componentes")}">' if os.path.exists(cat) else ''
        for p in P['pantallas']:
            tipo = p.get('pagina') or ('movil' if p['ancho'] < 700 else 'tv' if abs(p['ancho'] / p['alto'] - 16 / 9) < 0.01 else 'panel')
            src = d['id'] + '-' + p['id']
            if tipo == 'panel':
                nota = ''.join(f'<p>{E(x)}</p>' for x in notas.get(p['id'], []))
                pags.append(f'''<section class="pg pantalla"><img src="{_img(carpeta, src)}" style="object-fit:contain;object-position:top left"><div class="leyenda">
              <div class="n">{i:02d} · {E(d["nombre"])}</div><h3>{E(p["nombre"])}</h3>{nota}<div class="sz">{E(p["nota"])}<br>captura 2x</div></div></section>''')
            elif tipo == 'movil':
                pags.append(f'''<section class="pg movil" style="{_vars(d)}"><div class="tel"><img src="{_img(carpeta, src)}"></div>
          <div class="cat">{catimg}<div class="rot">{i:02d} · {E(d["nombre"])} <span>{E(p["nombre"])} · {E(p["nota"])} · a la izquierda</span><span>Componentes con este tema · a la derecha</span></div></div></section>''')
            else:
                pags.append(f'''<section class="pg plena"><img src="{_img(carpeta, src, 3200)}"><div class="rot">{i:02d} · {E(d["nombre"])} · {E(p["nombre"])} · {E(p["nota"])}</div></section>''')
    # Comparativa
    C = P.get('comparativa') or {}
    cols = C.get('columnas', [])
    filas = ''
    for d in dirs:
        v = C.get('valores', {}).get(d['id'], [])
        t = d['tokens']['dark'] if d.get('modo') == 'dark' else d['tokens']['light']
        rec = ' class="elegida"' if d['id'] == rec_id else ''
        celdas = ''.join(f'<td class="dots">{"●" * x}{"○" * (5 - x)}</td>' if isinstance(x, int) else f'<td>{E(x)}</td>' for x in v)
        filas += f'<tr{rec}><td><span class="sw" style="background:{t["primary"]}"></span><b>{E(d["nombre"])}</b></td>{celdas}<td class="mono" style="font-size:12.5px">{E(d.get("contraste", {}).get("light", "").split(" ·")[0])}</td></tr>'
    head = ''.join(f'<th>{E(c)}</th>' for c in cols)
    pags.append(f'''<section class="pg"><div class="cols" style="grid-template-columns:1fr"><div>
      <div class="eyebrow">Comparación</div><h2 class="titulo">{"La dirección, sola" if n == 1 else f"Las {_pal(n, True)}, lado a lado"}</h2>
      <table class="cmp"><tr><th>Dirección</th>{head}<th>Contraste AA</th></tr>{filas}</table>
      <p class="lead" style="font-size:15px;max-width:none;margin-top:16px">{E(C.get("nota", ""))}</p></div></div>{pie("Comparación")}</section>''')
    # Mezclas
    mz = ''
    for m in P.get('mezclas', []):
        a, b = m['imgs']
        mz += f'<div class="mezcla"><div class="imgs"><i style="background-image:url({_img(carpeta, a)})"></i><i style="background-image:url({_img(carpeta, b)})"></i></div><h3>{E(m["titulo"])}</h3><p>{E(m["texto"])}</p></div>'
    if mz:
        pags.append(f'''<section class="pg"><div class="cols" style="grid-template-columns:1fr"><div>
      <div class="eyebrow">Guía de mezcla</div><h2 class="titulo" style="font-size:38px">Tomar X de A y Y de B</h2>
      <p class="lead" style="font-size:16px;max-width:1200px;margin-top:12px">{E(P.get("mezcla_regla", ""))}</p><div class="mezclas">{mz}</div></div></div>{pie("Mezclas")}</section>''')
    # Recomendación
    R = P.get('recomendacion', {})
    porque = ''.join(f'<li>{E(x)}</li>' for x in R.get('porque', []))
    pasos = ''.join(f'<li>{E(x)}</li>' for x in R.get('pasos', []))
    if R:
        pags.append(f'''<section class="pg rec"><div class="cols" style="grid-template-columns:1.1fr 1fr">
      <div><div class="eyebrow">Recomendación</div><h2 class="titulo" style="font-size:52px">{E(R.get("titulo", ""))}</h2><p class="lead">{E(R.get("resumen", ""))}</p><ul class="lista">{porque}</ul>
        <p class="lead" style="font-size:16px;margin-top:22px"><b style="color:#f3f2ee">Si cambia la prioridad:</b> {E(R.get("alternativa", ""))}</p></div>
      <div><div class="eyebrow">Cómo se implementa</div><ul class="lista">{pasos}</ul>
        <p class="lead" style="font-size:18px;margin-top:30px;color:#f3f2ee">{E(R.get("pregunta", ""))}</p></div>
      </div><div class="pie" style="color:#9a988f"><span>{E(proyecto)} · direcciones visuales {E(P.get("version", ""))}</span><span>Recomendación</span></div></section>''')
    doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{E(P.get("titulo", proyecto))}</title>
<link rel="stylesheet" href="fuente/assets/fuentes/fuentes.css"><style>{CSS_PDF}</style></head><body>{"".join(pags)}</body></html>'''
    ruta = os.path.join(carpeta, 'propuestas.html')
    open(ruta, 'w').write(doc)
    imprimir(ruta, os.path.join(carpeta, 'propuestas.pdf'))
    print('pdf:', len(pags), 'páginas →', os.path.join(carpeta, 'propuestas.pdf'))


# ---------------------------------------------------------------- galería
def galeria(carpeta, props):
    items = []
    for i, d in enumerate(props['direcciones'], 1):
        for p in props['pantallas'] + [{'id': 'componentes', 'nombre': 'Componentes', 'nota': 'Catálogo · 1440'}]:
            f = f'pantallas/{d["id"]}-{p["id"]}.png'
            if os.path.exists(os.path.join(carpeta, f)):
                items.append({'dir': d['id'], 'n': f'{i:02d}', 'nombre': d['nombre'], 'pant': p['id'], 'titulo': p['nombre'], 'nota': p['nota'], 'src': f})
    dirs = [{'id': d['id'], 'nombre': d['nombre'], 'frase': d['frase'], 'color': (d['tokens']['dark'] if d.get('modo') == 'dark' else d['tokens']['light'])['primary']} for d in props['direcciones']]
    pants = [{'id': p['id'], 'nombre': p['nombre']} for p in props['pantallas']] + [{'id': 'componentes', 'nombre': 'Componentes'}]
    doc = GALERIA.replace('__TITULO__', E(props.get('titulo', props.get('proyecto', 'Proyecto')))).replace('__DATOS__', json.dumps({'items': items, 'dirs': dirs, 'pants': pants, 'rec': props.get('recomendacion', {}).get('base', '')}, ensure_ascii=False))
    open(os.path.join(carpeta, 'index.html'), 'w').write(doc)
    print('galeria: index.html con', len(items), 'imágenes')


GALERIA = r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITULO__</title>
<link rel="stylesheet" href="fuente/assets/fuentes/fuentes.css">
<style>
:root { --bg:#f3f2ee; --fg:#1a1a18; --mfg:#5f5e58; --bd:#d9d7cf; --card:#fff; }
@media (prefers-color-scheme: dark) { :root { --bg:#111110; --fg:#f0efea; --mfg:#a3a199; --bd:#2c2b28; --card:#1a1a19; } }
* { box-sizing: border-box; } body { margin:0; background:var(--bg); color:var(--fg); font:15px/1.5 'Geist', system-ui, sans-serif; }
header { position:sticky; top:0; z-index:5; background:var(--bg); border-bottom:1px solid var(--bd); padding:16px 24px; display:flex; flex-wrap:wrap; gap:12px 24px; align-items:center; }
h1 { font-size:20px; letter-spacing:-0.02em; margin:0; font-weight:600; }
.links { display:flex; gap:16px; font-size:14px; } .links a { color:var(--fg); }
.filtros { display:flex; flex-wrap:wrap; gap:6px; width:100%; }
.filtros button { height:34px; padding:0 12px; border:1px solid var(--bd); background:var(--card); color:var(--fg); border-radius:8px; font:500 14px 'Geist', sans-serif; cursor:pointer; display:inline-flex; align-items:center; gap:8px; }
.filtros button[aria-pressed="true"] { background:var(--fg); color:var(--bg); border-color:var(--fg); }
.filtros .sw { width:10px; height:10px; border-radius:2px; }
.filtros .sep { width:1px; background:var(--bd); margin:0 6px; }
main { padding:24px; display:grid; grid-template-columns:repeat(auto-fill, minmax(min(100%, 520px), 1fr)); gap:28px 24px; }
figure { margin:0; cursor:zoom-in; }
figure .marco { position:relative; background:var(--card); border:1px solid var(--bd); aspect-ratio:16/10; overflow:hidden; }
figure .marco img { position:absolute; inset:0; width:100%; height:100%; object-fit:contain; display:block; }
figure[data-pant="componentes"] .marco img { object-fit:cover; object-position:top; }
figcaption { display:flex; gap:10px; align-items:baseline; margin-top:8px; font-size:14px; }
figcaption b { font-weight:600; } figcaption span { color:var(--mfg); font:13px 'Geist Mono', monospace; }
.caja { position:fixed; inset:0; background:rgb(0 0 0 / 0.92); display:none; z-index:10; }
.caja[open] { display:grid; grid-template-rows:auto 1fr; }
.caja .barra { display:flex; gap:12px; align-items:center; padding:12px 16px; color:#f0efea; font-size:14px; }
.caja .barra button { height:36px; min-width:44px; border:1px solid #444; background:#1a1a19; color:#f0efea; border-radius:8px; cursor:pointer; font:500 14px 'Geist', sans-serif; }
.caja .vista { overflow:auto; display:grid; place-items:center; padding:0 16px 16px; }
.caja .vista img { max-width:100%; max-height:calc(100vh - 80px); }
.caja .vista.real img { max-width:none; max-height:none; }
</style></head><body>
<header><h1>__TITULO__</h1><nav class="links"><a href="propuestas.pdf">Cuadernillo en PDF</a><a href="README.md">README</a><a href="contraste.txt">Contraste</a></nav>
<div class="filtros" id="fd"></div><div class="filtros" id="fp"></div></header>
<main id="grid"></main>
<div class="caja" id="caja" role="dialog" aria-label="Pantalla ampliada"><div class="barra"><button id="prev" aria-label="Anterior">←</button><button id="next" aria-label="Siguiente">→</button><span id="cap"></span><span style="flex:1"></span><button id="zoom">Tamaño real</button><button id="close">Cerrar</button></div><div class="vista" id="vista"><img id="big" alt=""></div></div>
<script>
const D = __DATOS__;
let fDir = 'todas', fPant = 'todas', vis = [], idx = 0;
const $ = s => document.querySelector(s);
function boton(cont, id, txt, color, grupo) {
  const b = document.createElement('button'); b.dataset.id = id; b.setAttribute('aria-pressed', id === 'todas');
  b.innerHTML = (color ? `<span class="sw" style="background:${color}"></span>` : '') + txt;
  b.onclick = () => { if (grupo === 'd') fDir = id; else fPant = id; cont.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x.dataset.id === id)); pintar(); };
  cont.appendChild(b);
}
boton($('#fd'), 'todas', 'Todas las direcciones', null, 'd');
D.dirs.forEach((d, i) => boton($('#fd'), d.id, `${String(i + 1).padStart(2, '0')} ${d.nombre}${d.id === D.rec ? ' · recomendada' : ''}`, d.color, 'd'));
boton($('#fp'), 'todas', 'Todas las pantallas', null, 'p');
D.pants.forEach(p => boton($('#fp'), p.id, p.nombre, null, 'p'));
function pintar() {
  vis = D.items.filter(x => (fDir === 'todas' || x.dir === fDir) && (fPant === 'todas' || x.pant === fPant));
  $('#grid').innerHTML = vis.map((x, i) => `<figure data-i="${i}" data-pant="${x.pant}"><div class="marco"><img loading="lazy" src="${x.src}" alt="${x.nombre}: ${x.titulo}"></div><figcaption><b>${x.n} ${x.nombre}</b>${x.titulo}<span>${x.nota}</span></figcaption></figure>`).join('');
  document.querySelectorAll('figure').forEach(f => f.onclick = () => abrir(+f.dataset.i));
}
function abrir(i) { idx = (i + vis.length) % vis.length; const x = vis[idx]; $('#big').src = x.src; $('#cap').textContent = `${x.n} ${x.nombre} · ${x.titulo} · ${x.nota}`; $('#caja').setAttribute('open', ''); }
$('#prev').onclick = () => abrir(idx - 1); $('#next').onclick = () => abrir(idx + 1);
$('#close').onclick = () => $('#caja').removeAttribute('open');
$('#zoom').onclick = () => $('#vista').classList.toggle('real');
document.addEventListener('keydown', e => { if (!$('#caja').hasAttribute('open')) return; if (e.key === 'Escape') $('#close').click(); if (e.key === 'ArrowLeft') abrir(idx - 1); if (e.key === 'ArrowRight') abrir(idx + 1); });
pintar();
</script></body></html>'''


# ---------------------------------------------------------------- revisión con visión
def revision(carpeta):
    pdf_ = os.path.join(carpeta, 'propuestas.pdf')
    if not os.path.exists(pdf_):
        return
    tmp = os.path.join(carpeta, 'fuente', '.build', 'rev')
    os.makedirs(tmp, exist_ok=True)
    for f in glob.glob(os.path.join(tmp, '*.png')):
        os.remove(f)
    if not shutil.which('pdftoppm'):
        print('revision: sin pdftoppm (poppler-utils); salteo las hojas de revisión')
        return
    subprocess.run(['pdftoppm', '-r', '36', '-png', pdf_, os.path.join(tmp, 'p')], check=True)
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print('revision: sin Pillow; mirá las páginas en', tmp)
        return
    fs = sorted(glob.glob(os.path.join(tmp, 'p-*.png')))
    out = os.path.join(carpeta, 'fuente', '.build')
    for h in range(0, len(fs), 12):
        grupo = [Image.open(f) for f in fs[h:h + 12]]
        w, hh = grupo[0].size
        hoja = Image.new('RGB', (3 * w + 4 * 10, 4 * (hh + 24) + 10), '#777')
        dr = ImageDraw.Draw(hoja)
        for k, im in enumerate(grupo):
            x, y = 10 + (k % 3) * (w + 10), 10 + (k // 3) * (hh + 24)
            hoja.paste(im, (x, y + 18))
            dr.text((x, y + 2), f'p. {h + k + 1}', fill='white')
        hoja.save(os.path.join(out, f'revision-{h // 12 + 1}.png'))
    print('revision: hojas en', out, '(mirarlas con visión; criterios en references/revision.md)')
