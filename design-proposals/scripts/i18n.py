"""Every human-language string that build.py and booklet.py put in generated files.

t(lang, key, **kw) looks up TEXTOS[lang][key] (falling back to "en") and formats it with kw.
This is the only file in scripts/ that holds non-English text.
"""

DESIGN_EN = """# Design Analysis: {project} · {name}

> Direction {i} of {n} in the `{skill}` booklet ({date}). Emphasis: design system (prescriptive: this is a proposal, not the analysis of an existing site).

## Source
Proposal generated with the `{skill}` skill: tokens in `{proposal_file}`, composition in `{dir_css}`, screens rendered with headless Chrome at 2x. References: {references}.

## TL;DR
{tagline} {idea} Signature moment: {signature}

## 1. Visual identity
### 1.1 Surface description
- Personality: {temperature}; {density_lower} density. ✅
- Mood: {tagline} ✅
- Stylistic references: {references}. ✅
- Information density: {density}. ✅
- Implicit positioning: {positioning} ✅

### 1.2 Brand voice / Atmosphere
{idea}

### 1.3 The "ONE brand thing"
- The thing: {signature}
- Why: it comes from the client's world, not from how the tools of the trade look.
- How the rest holds back: a single accent (`{{colors.primary}}` {primary}), states always with text or icon.
- Where it does not appear: on surfaces that show the client's brand, that brand rules; the signature changes composition, never the brand.

## 2. Design System (tokens)
### 2.1 Colors
| Token | Light | Dark | Confidence |
|---|---|---|---|
{color_rows}

### 2.2 Typography
Fonts: {fonts} (Google Fonts, OFL). Scale: 12 (short metadata), {text_sm}, {text_base} (panel body), 16, 20, {text_xl} (page titles). Line height 1.5 for text and 1.1-1.2 for headings. Tabular figures in tables, durations and times with `{{typography.caption-mono}}`.

| Token | Family | Use |
|---|---|---|
| `display` | {font_display} | Page and section titles |
| `body` | {font_sans} | Interface and text |
| `caption-mono` | {font_mono} | Durations, codes, versions, times |

### 2.3 Spacing
Base 4 px. Inner groups at 8, between groups 16-24, between regions 32-40. Control height {control_h}; table rows {row_h}.

### 2.4 Radii
`sm` {radius_sm} · `md` {radius} (controls) · `lg` {radius_lg} (dialogs and panels). Nested radii shrink inward. Shape: {shape}.

### 2.5 Elevation system
| Level | Name | Treatment | Use |
|---|---|---|---|
| 0 | Flat | No shadow; separation by a 1 px rule or by tone | Regions, tables, panels |
| 1 | Floating | `--shadow-float`, never together with a hairline border | Menus, ⌘K, toasts, dialogs, the item being dragged |

### 2.6 Borders
1 px `{{colors.border}}` to separate; `{{colors.input}}` ({input}) on controls (≥ 3:1); focus 2 px `{{colors.ring}}` with a 2 px offset.

### 2.7 Accessibility quick-check
Light: {contrast_light_na}. Dark: {contrast_dark_na}. Measured with `contrast.py` (WCAG 2.x) on text/background pairs, control borders and focus; details in `{contrast_file}`.

## 3. Components Inventory
### 3.1 Generic components
#### button-primary
A single main action per screen ("Save", "Create"). States: hover, pressed (scale 0.97), focus, disabled, loading.
#### input
Label above, help or error below with an icon; counter when there is a limit. States: empty, focus, filled, error, disabled.
#### badge
Dot + text: Active, Pending, Error. Never color alone.
#### table-row
Height {row_h}, hover, selected with an accent tint, tabular figures aligned right.
#### sidebar-item
20 px icon + label; active with `{{colors.sidebar-accent}}`; counter in mono.

Full library (HTML + CSS with tokens, in the `{skill}/{components_dir}/` skill folder):

| Component | States | File |
|---|---|---|
{comp_rows}

### 3.2 Signature components
- **{signature}** Appears in the booklet screens ({screen_names}). Imagery: {imagery}. Motion: {motion}.

## 4. Layout & Composition
### 4.1 Grid & containers
Booklet screens (see `{shots_dir}/`):
{grid}
Max container 1440 px; fixed or rail sidebar, 56 px topbar, side panels as a sheet over the content.
### 4.2 Composition patterns
One focal point per screen; the main action visible without scrolling; regions separated by rule or tone rather than by cards.
### 4.3 Responsive behavior
| Breakpoint | Behavior |
|---|---|
| ≥ 1280 | Full layout; fixed side panels |
| 768-1279 | Side panels as a floating sheet; rail sidebar |
| < 768 | One column; navigation in a bottom bar or menu; tables become lists |
44 px touch targets on touch devices.
### 4.4 Image behavior
- {imagery}.
- Client images without color filters; inactive or error states are marked with text, not only by dimming the image.

## 5. Reconstruction Notes
Suggested stack: Next.js + Tailwind v4 + shadcn/ui. Paste `tokens.css` into `globals.css`: it overrides shadcn's `:root` and `.dark` and adds `@theme inline`. Quick wins: fonts with `next/font`, Lucide icons, badges with a dot. Tricky bits: the signature moment (its own CSS in one component), tabular figures in every table, the designed focus.

| Layer | Confidence | Why |
|---|---|---|
| Tokens | ✅ | Defined and measured |
| Components | ✅ | Library with states |
| Signature | ⚠️ | Validate with real users |

## 6. Do's and Don'ts
### Do
- Reserve `{{colors.primary}}` ({primary}) for the main action and selection.
- Figures, durations and times in `{{typography.caption-mono}}` ({mono_first}).
- States with a dot and text: "Active", "Error".
- Shadow only on what floats (`--shadow-float`).
- On surfaces that show the client's brand, that brand rules.
### Don't
- Do not add a second accent color.
- Do not default to big-number cards: a status sentence and a list of what needs attention.
- Do not wrap every region in a card.
- Do not cover the client's brand where it rules.
- Do not use the signature as decoration everywhere: only where the booklet defined it.

## 7. Open Questions
- Validate the direction with real users before closing.
- Product logo in this direction.

## 8. Companion files
- `tokens.css`: CSS variables (`:root`, `.dark`) + Tailwind v4 `@theme inline`, shadcn/ui names.
- `{contrast_file}` (booklet root).
{screen_list}
- `{catalog_png}`: component catalog with this theme.

## For the SPEC (ready to paste)
**Design system: "{name}".** {idea} Signature: {signature} Tokens: `docs/proposals/.../{dir_id}/tokens.css` (shadcn/ui + Tailwind v4). Typography: {fonts}. Shape: {shape}. Density: {density}. Motion: {motion}.
**Accessibility.** WCAG 2.2 AA; {contrast_light} (light) and {contrast_dark} (dark); limits measured in {limits_file}.
"""

DESIGN_ES = """# Design Analysis: {project} · {name}

> Dirección {i} de {n} del cuadernillo `{skill}` ({date}). Emphasis: design system (prescriptivo: es una propuesta, no el análisis de un sitio existente).

## Source
Propuesta generada con la skill `{skill}`: tokens en `{proposal_file}`, composición en `{dir_css}`, pantallas renderizadas con Chrome headless a 2x. Referencias: {references}.

## TL;DR
{tagline} {idea} Momento firma: {signature}

## 1. Visual identity
### 1.1 Surface description
- Personality: {temperature}; densidad {density_lower}. ✅
- Mood: {tagline} ✅
- Stylistic references: {references}. ✅
- Information density: {density}. ✅
- Implicit positioning: {positioning} ✅

### 1.2 Brand voice / Atmosphere
{idea}

### 1.3 The "ONE brand thing"
- La cosa: {signature}
- Por qué: sale del mundo del cliente, no de cómo se ven las herramientas del rubro.
- Cómo se contiene el resto: un solo acento (`{{colors.primary}}` {primary}), estados siempre con texto o ícono.
- Dónde no aparece: en las superficies que muestran la marca del cliente, manda esa marca; la firma cambia la composición, nunca la marca.

## 2. Design System (tokens)
### 2.1 Colors
| Token | Claro | Oscuro | Confianza |
|---|---|---|---|
{color_rows}

### 2.2 Typography
Fuentes: {fonts} (Google Fonts, OFL). Escala: 12 (metadatos cortos), {text_sm}, {text_base} (cuerpo del panel), 16, 20, {text_xl} (títulos de página). Interlineado 1,5 en texto y 1,1–1,2 en títulos. Cifras tabulares en tablas, duraciones y horarios con `{{typography.caption-mono}}`.

| Token | Familia | Uso |
|---|---|---|
| `display` | {font_display} | Títulos de página y de sección |
| `body` | {font_sans} | Interfaz y texto |
| `caption-mono` | {font_mono} | Duraciones, códigos, versiones, horarios |

### 2.3 Spacing
Base 4 px. Grupos internos a 8, entre grupos 16–24, entre regiones 32–40. Alto de control {control_h}; filas de tabla {row_h}.

### 2.4 Radii
`sm` {radius_sm} · `md` {radius} (controles) · `lg` {radius_lg} (diálogos y paneles). Los radios anidados se achican hacia adentro. Forma: {shape}.

### 2.5 Elevation system
| Level | Name | Treatment | Use |
|---|---|---|---|
| 0 | Plano | Sin sombra; separación por regla de 1 px o por tono | Regiones, tablas, paneles |
| 1 | Flotante | `--shadow-float`, sin borde fino a la vez | Menús, ⌘K, toasts, diálogos, el ítem que se arrastra |

### 2.6 Borders
1 px `{{colors.border}}` para separar; `{{colors.input}}` ({input}) en controles (≥ 3:1); foco 2 px `{{colors.ring}}` con separación de 2 px.

### 2.7 Accessibility quick-check
Claro: {contrast_light_na}. Oscuro: {contrast_dark_na}. Medido con `contrast.py` (WCAG 2.x) sobre los pares texto/fondo, bordes de control y foco; detalle en `{contrast_file}`.

## 3. Components Inventory
### 3.1 Generic components
#### button-primary
Una sola acción principal por pantalla («Guardar», «Crear»). Estados: hover, presionado (escala 0,97), foco, deshabilitado, cargando.
#### input
Label arriba, ayuda o error abajo con ícono; contador cuando hay límite. Estados: vacío, foco, lleno, error, deshabilitado.
#### badge
Punto + texto: Activo, Pendiente, Error. Nunca solo color.
#### table-row
Alto {row_h}, hover, seleccionada con tinte del acento, cifras tabulares a la derecha.
#### sidebar-item
Ícono de 20 px + etiqueta; activo con `{{colors.sidebar-accent}}`; contador en mono.

Biblioteca completa (HTML + CSS con tokens, en la skill `{skill}/{components_dir}/`):

| Componente | Estados | Archivo |
|---|---|---|
{comp_rows}

### 3.2 Signature components
- **{signature}** Aparece en las pantallas del cuadernillo ({screen_names}). Imagen: {imagery}. Movimiento: {motion}.

## 4. Layout & Composition
### 4.1 Grid & containers
Pantallas del cuadernillo (ver `{shots_dir}/`):
{grid}
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
- {imagery}.
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
- Reservá `{{colors.primary}}` ({primary}) para la acción principal y la selección.
- Cifras, duraciones y horarios en `{{typography.caption-mono}}` ({mono_first}).
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
- `{contrast_file}` (raíz del cuadernillo).
{screen_list}
- `{catalog_png}`: catálogo de componentes con este tema.

## Para la especificación (listo para pegar)
**Sistema de diseño: «{name}».** {idea} Firma: {signature} Tokens: `docs/propuestas/.../{dir_id}/tokens.css` (shadcn/ui + Tailwind v4). Tipografía: {fonts}. Forma: {shape}. Densidad: {density}. Movimiento: {motion}.
**Accesibilidad.** WCAG 2.2 AA; {contrast_light} (claro) y {contrast_dark} (oscuro); límites medidos en {limits_file}.
"""

TEXTOS = {
    'en': {
        # numbers (index = value); *_f = feminine forms, same in English
        'numbers': ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight'],
        'numbers_f': ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight'],
        'decimal': '.',
        'project_default': 'Project',
        'positioning_default': "Own product; the user's content is the star.",
        'na': 'n/a',
        # tokens.css
        'tokens_header': '/* {name} · tokens for shadcn/ui + Tailwind v4. Generated by {skill}/build.py */',
        'tokens_fonts': '/* Fonts: {fonts} (Google Fonts, OFL) */',
        # contrast.txt / limits.txt
        'kind_text': 'text', 'kind_border': 'border', 'kind_large': 'large',
        'contrast_fail': 'NO  {dir} {mode}: {fg} {a} on {bg} {b} [{kind}] {ratio}:1',
        'contrast_summary': '{ok}/{total} pairs pass AA · min text {min}:1',
        'limits_none': '??  {id}: no result',
        'limits_line': '{status} {id}: min text {min} px (≥ {req}) "{text}" · horizontal scroll: {scroll} · clipped: {clipped} {sample}',
        'yes': 'yes', 'no': 'no',
        # design.md
        'design_body': DESIGN_EN,
        'design_grid': '- {name}: {w}×{h} px ({note}).',
        'design_screen': '- `{png}`: {name} ({note})',
        'components': [
            ('App shell', 'sidebar expanded and as a rail, organization switcher, active item, counter, notice', 'shell.css'),
            ('Command bar ⌘K', 'closed, open, grouped results, highlighted item, no results', 'overlays.css'),
            ('Data table', 'loading (skeleton), empty, with filters, sort asc/desc, hover and selected row, partial selection, bulk actions, error', 'table.css'),
            ('Empty states', 'first use with CTA, no filter results, error with retry', 'states.css'),
            ('Skeletons and loading', 'rows, cards, text, spinner in button; no shimmer with reduced motion', 'states.css'),
            ('Toasts', 'success, error, with an "Undo" action, stacked', 'overlays.css'),
            ('Modal and side panel', 'open, destructive confirmation, with form, closing', 'overlays.css'),
            ('Forms', 'empty, focus, filled, error with icon and text, success, disabled, character counter, prefix', 'forms.css'),
            ('Tabs and segmented', 'selected, hover, focus, with counter', 'base.css'),
            ('Onboarding checklist', 'step done, current, pending; progress "2 of 4"', 'pages.css'),
            ('Settings page', 'sections with rule, danger zone, saved', 'pages.css'),
            ('Plans and billing', 'current plan, upgrade, limit reached, usage meters, invoices', 'pages.css'),
            ('SVG charts', 'bars, line, 24 h strip, no data', 'charts.css'),
            ('Avatars and presence', 'initials, photo, online, stack', 'base.css'),
            ('Status badges', 'active, pending, error, info; always with dot and text', 'base.css'),
            ('Breadcrumbs', 'with link, current, truncated', 'base.css'),
            ('Pagination', 'first, middle, last, disabled', 'table.css'),
            ('Dark mode', 'same components with data-mode="dark"; surfaces get lighter as they rise', 'tokens.css'),
        ],
        # PDF
        'footer': '{project} · visual directions {version}',
        'cover_meta': '{n} {dirs} · {ns} {screens} each · same data',
        'direction_one': 'direction', 'direction_many': 'directions',
        'screen_one': 'screen', 'screen_many': 'screens',
        'cover_recommended': 'Recommended: ',
        'chars_one': 'one personality', 'chars_many': '{w} personalities',
        'same_product': 'Same product, {chars}',
        'the_screen_one': 'The screen', 'the_screen_many': 'The {w} screens',
        'how_to_read': 'How to read this',
        'fixed_in_all': 'Fixed in all of them',
        'varies': 'Changes between directions',
        'fictional_data': 'Fictional data',
        'fictional_default': 'Made-up data for comparison; the same in every direction.',
        'what_compared': 'What is compared',
        'axes': {'temperature': 'Temperature', 'density': 'Density', 'typography': 'Typography', 'shape': 'Shape', 'imagery': 'Imagery', 'motion': 'Motion'},
        'signature_moment': 'Signature moment',
        'aa_light': 'AA light', 'aa_dark': 'AA dark',
        'capture_2x': '2x capture',
        'mobile_left': '{name} · {note} · on the left',
        'mobile_right': 'Components with this theme · on the right',
        'comparison': 'Comparison',
        'cmp_title_one': 'The direction, on its own', 'cmp_title_many': 'All {w}, side by side',
        'direction': 'Direction', 'contrast_aa': 'AA contrast',
        'mix_guide': 'Mixing guide', 'mix_title': 'Take X from A and Y from B', 'mixes': 'Mixes',
        'recommendation': 'Recommendation', 'if_priority': 'If the priority changes:', 'how_implemented': 'How to implement it',
        # gallery
        'g_pdf': 'PDF booklet', 'g_contrast': 'Contrast', 'g_enlarged': 'Enlarged screen', 'g_prev': 'Previous', 'g_next': 'Next',
        'g_real_size': 'Actual size', 'g_close': 'Close', 'g_all_dirs': 'All directions', 'g_all_screens': 'All screens',
        'g_recommended': 'recommended', 'g_components': 'Components', 'g_catalog_note': 'Catalog · 1440',
        # review sheets
        'review_page': 'p. {n}',
    },
    'es': {
        'numbers': ['cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho'],
        'numbers_f': ['cero', 'una', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho'],
        'decimal': ',',
        'project_default': 'Proyecto',
        'positioning_default': 'Producto propio; el contenido del usuario es la estrella.',
        'na': 's/d',
        'tokens_header': '/* {name} · tokens para shadcn/ui + Tailwind v4. Generado por {skill}/build.py */',
        'tokens_fonts': '/* Fuentes: {fonts} (Google Fonts, OFL) */',
        'kind_text': 'texto', 'kind_border': 'borde', 'kind_large': 'grande',
        'contrast_fail': 'NO  {dir} {mode}: {fg} {a} sobre {bg} {b} [{kind}] {ratio}:1',
        'contrast_summary': '{ok}/{total} pares cumplen AA · texto mínimo {min}:1',
        'limits_none': '??  {id}: sin resultado',
        'limits_line': '{status} {id}: texto mínimo {min} px (≥ {req}) «{text}» · scroll horizontal: {scroll} · recortes: {clipped} {sample}',
        'yes': 'sí', 'no': 'no',
        'design_body': DESIGN_ES,
        'design_grid': '- {name}: {w}×{h} px ({note}).',
        'design_screen': '- `{png}`: {name} ({note})',
        'components': [
            ('App shell', 'sidebar expandido y en riel, selector de organización, ítem activo, contador, aviso', 'shell.css'),
            ('Barra de comandos ⌘K', 'cerrada, abierta, con resultados agrupados, ítem resaltado, sin resultados', 'overlays.css'),
            ('Tabla de datos', 'cargando (skeleton), vacía, con filtros, orden asc/desc, fila hover y seleccionada, selección parcial, acciones en lote, error', 'table.css'),
            ('Estados vacíos', 'primer uso con CTA, sin resultados de filtro, error con reintento', 'states.css'),
            ('Skeletons y carga', 'filas, tarjetas, texto, spinner en botón; sin shimmer con movimiento reducido', 'states.css'),
            ('Toasts', 'éxito, error, con acción «Deshacer», apilados', 'overlays.css'),
            ('Modal y panel lateral', 'abierto, confirmación destructiva, con formulario, cerrando', 'overlays.css'),
            ('Formularios', 'vacío, foco, lleno, error con ícono y texto, éxito, deshabilitado, contador de caracteres, prefijo', 'forms.css'),
            ('Tabs y segmented', 'seleccionado, hover, foco, con contador', 'base.css'),
            ('Checklist de onboarding', 'paso hecho, actual, pendiente; progreso «2 de 4»', 'pages.css'),
            ('Página de ajustes', 'secciones con regla, zona de peligro, guardado', 'pages.css'),
            ('Planes y facturación', 'plan actual, mejora, límite alcanzado, medidores de uso, facturas', 'pages.css'),
            ('Gráficos en SVG', 'barras, línea, franja de 24 h, sin datos', 'charts.css'),
            ('Avatares y presencia', 'con iniciales, con foto, en línea, pila', 'base.css'),
            ('Badges de estado', 'activo, pendiente, error, info; siempre con punto y texto', 'base.css'),
            ('Breadcrumbs', 'con enlace, actual, truncado', 'base.css'),
            ('Paginación', 'primera, intermedia, última, deshabilitada', 'table.css'),
            ('Modo oscuro', 'mismos componentes con data-mode="dark"; superficies que se aclaran al subir', 'tokens.css'),
        ],
        'footer': '{project} · direcciones visuales {version}',
        'cover_meta': '{n} {dirs} · {ns} {screens} cada una · mismos datos',
        'direction_one': 'dirección', 'direction_many': 'direcciones',
        'screen_one': 'pantalla', 'screen_many': 'pantallas',
        'cover_recommended': 'Recomendada: ',
        'chars_one': 'un carácter', 'chars_many': '{w} caracteres',
        'same_product': 'Mismo producto, {chars}',
        'the_screen_one': 'La pantalla', 'the_screen_many': 'Las {w} pantallas',
        'how_to_read': 'Cómo leer esto',
        'fixed_in_all': 'Queda fijo en todas',
        'varies': 'Cambia entre direcciones',
        'fictional_data': 'Datos ficticios',
        'fictional_default': 'Datos inventados para comparar; los mismos en todas las direcciones.',
        'what_compared': 'Qué se compara',
        'axes': {'temperature': 'Temperatura', 'density': 'Densidad', 'typography': 'Tipografía', 'shape': 'Forma', 'imagery': 'Imagen', 'motion': 'Movimiento'},
        'signature_moment': 'Momento firma',
        'aa_light': 'AA claro', 'aa_dark': 'AA oscuro',
        'capture_2x': 'captura 2x',
        'mobile_left': '{name} · {note} · a la izquierda',
        'mobile_right': 'Componentes con este tema · a la derecha',
        'comparison': 'Comparación',
        'cmp_title_one': 'La dirección, sola', 'cmp_title_many': 'Las {w}, lado a lado',
        'direction': 'Dirección', 'contrast_aa': 'Contraste AA',
        'mix_guide': 'Guía de mezcla', 'mix_title': 'Tomar X de A y Y de B', 'mixes': 'Mezclas',
        'recommendation': 'Recomendación', 'if_priority': 'Si cambia la prioridad:', 'how_implemented': 'Cómo se implementa',
        'g_pdf': 'Cuadernillo en PDF', 'g_contrast': 'Contraste', 'g_enlarged': 'Pantalla ampliada', 'g_prev': 'Anterior', 'g_next': 'Siguiente',
        'g_real_size': 'Tamaño real', 'g_close': 'Cerrar', 'g_all_dirs': 'Todas las direcciones', 'g_all_screens': 'Todas las pantallas',
        'g_recommended': 'recomendada', 'g_components': 'Componentes', 'g_catalog_note': 'Catálogo · 1440',
        'review_page': 'p. {n}',
    },
}


def t(lang, key, **kw):
    s = TEXTOS.get(lang, TEXTOS['en']).get(key, TEXTOS['en'][key])
    return s.format(**kw) if kw else s


def num(lang, n, fem=False):
    """Number word for 0..8 (feminine form when fem), digits above."""
    return t(lang, 'numbers_f' if fem else 'numbers')[n] if 0 <= n <= 8 else str(n)
