# Biblioteca «SaaS pro»

CSS plano, sin framework. Los componentes leen **solo variables**, así que cualquier tema los re-viste.
`catalogo.html` muestra todo junto en una hoja de 1440 px (≈ 2590 px de alto).

## Archivos

| Archivo | Qué trae |
|---|---|
| `base.css` | Contrato de tokens (nombres shadcn/ui), reset, tipografía y controles chicos: `.btn` `.kbd` `.badge` `.avatar` `.crumbs` `.tabs` `.seg` `.field` `.input` `.select` `.switch` `.check` |
| `shell.css` | Marco de la app: sidebar, riel, selector de organización, topbar |
| `tabla.css` | Tabla de datos con barra, filtros, selección, acciones masivas y paginación |
| `overlays.css` | Barra ⌘K, modal, confirmación destructiva, panel lateral, toasts, scrim |
| `formularios.css` | Layout de formulario, prefijo/sufijo, contador, validación, tarjetas de opción, carga de archivos, `.bar` |
| `estados.css` | Vacío con ilustración, esqueletos, spinner, error con reintento |
| `paginas.css` | Primeros pasos, configuración, planes y facturación |
| `graficos.css` | Barras, sparkline, franja de disponibilidad 24 h, leyenda, tooltip |
| `temas-ejemplo.css` | Tema `ejemplo` claro y oscuro (neutro cálido + verde `#1f6b4f`) |
| `catalogo.html` | Hoja de muestra con datos de un producto inventado (Taller Sur) |

Orden de carga: `base.css` → componentes → temas. El catálogo trae la línea `<!-- TEMAS -->` justo después de los `<link>`: ahí el build inyecta las hojas de los otros temas.

## Cómo entra un tema

```html
<html data-theme="banco" data-mode="dark">
```

Un tema es un bloque `[data-theme="id"] { … }` más `[data-theme="id"][data-mode="dark"] { … }` que **pisa variables y nada más**: `--background --foreground --card --popover --muted --muted-foreground --primary --primary-foreground --accent --accent-ink --border --input --ring --destructive --success --warning --info --sidebar* --chart-1..5 --font-sans/-display/-mono --radius --shadow-float`. Opcional: `--scrim` (si falta, sale de `--foreground` en claro y de `--background` en oscuro).
Reglas: texto ≥ 4,5:1 sobre `--card` y `--background`; `--input` ≥ 3:1 sobre `--card`; en oscuro las superficies se aclaran al subir (`--background` < `--card` < `--popover`).

## API de clases (una línea por componente)

**shell.css**
- `.shell > .sidebar + .main` · `.shell[data-collapsed]` pasa la sidebar de 240 px a riel de 60 px (solo íconos, `.tip` para el nombre).
- `.org-switch` (`.avatar.avatar--sq.org-mark` + `.org-switch__name/__plan` + chevron) · `[aria-expanded="true"]` abierto.
- `.popover` > `.popover__label` + `.menu-item` (`.menu-item__text/__sub`, `[data-highlighted]`) + `.menu-sep`.
- `.nav` > `.nav__section` + `a.nav__item` (`.nav__label`, `.nav__count`, `.nav__count--alert`) · `[aria-current="page"]` activo · `[data-badge]` punto en el riel.
- `.sidebar__foot > .user-row` (`.avatar[data-presence]` + `.user-row__name/__mail`).
- `.topbar` > `.crumbs` + `.search-trigger` («Buscar… ⌘K») + `.topbar__actions` (`.icon-dot` = novedad).
- `.page` > `.page-head` (`.page-head__title/__desc` + botones).

**tabla.css**
- `.dt` > `.dt-toolbar` | `.dt-bulk` | `table.table` | `.dt-foot`.
- `.search` (input con ícono) · `.chip` (`.chip__key` + `.chip__val`, `[data-active]`, `.chip--add` punteado, `.chip__clear`).
- `.dt-bulk` (`.dt-bulk__count`, `.sep`, `.btn--ghost`, `.is-danger`).
- `th[aria-sort] > .sort` · `.num` a la derecha (celdas en mono tabular) · `.col-check` · `.col-more > .row-more`.
- `tr[aria-selected="true"]` · `tr:hover` / `.is-hover` · `.cell-main` (`__title` + `__sub`) · `.cell-ico`.
- `.dt-foot` > `.dt-foot__range` + `.pager > .pager__btn[aria-current="page"]`.

**overlays.css**
- `.scrim` fondo plano translúcido (sin blur) · `.float` superficie flotante genérica.
- `.cmdk` > `.cmdk__input` + `.cmdk__list > .cmdk__group > .cmdk__label + .cmdk__item[aria-selected]` (`mark`, `.cmdk__meta`) + `.cmdk__foot`.
- `.dialog` > `.dialog__head` (`__titles`, `__title`, `__desc`, `__close`) + `.dialog__body` + `.dialog__foot` · `.dialog--danger` con `.dialog__icon`.
- `.sheet` > `.sheet__head` + `.sheet__body` + `.sheet__foot` · `.kv` lista clave/valor (`dt`/`dd`).
- `.toast-stack > .toast.toast--ok|--err|--info` (`.toast__title/__desc`, `.toast__actions`, `.toast__close`).

**formularios.css**
- `.form` · `.form-row` (2 columnas) · `.form-actions`.
- `.field` + `.field__top` (`.label` + `.counter[data-near|data-over]`) · `.req` (obligatorio) · `.opt` (opcional) · `.field__msg` con ícono.
- `.input-group` > `.addon` (prefijo/sufijo, `.addon--ghost`) + `input` · `.select > .select__val` · `.textarea`.
- `.radio-cards > .radio-card[aria-checked]` (`__title`, `__desc`, `__mark`, `__shape`).
- `.dropzone[data-dragover]` · `.file-row` (`__name`, `__meta`, `.bar`) · `.bar > span` con `--p: 0..1` (`[data-level="warn|full"]`).

**estados.css**
- `.empty` > `svg.empty__art` (trazos `.ill-line .ill-faint .ill-dash .ill-soft .ill-card .ill-accent .ill-fill .ill-text`) + `.empty__title/__desc/__actions`.
- `.skel` + `--line|--title|--avatar|--block|--pill` (`--w`, `--h`) · `.skel-lines` · `.skel-table > .skel-table__row` · `.skel-card`.
- `svg.spinner` (`.track` + `.head`) · `.loading-inline` · `.btn[data-loading]`.
- `.error-state` > `__icon` + `__title` + `__desc` + `__actions` (`__code`).

**paginas.css**
- `.onboarding` > `__head` (`__title`, `__count` «2 de 4») + `.bar` + `ol.steps > li.step[data-state="done|current|pending"]` (`__mark`, `__title`, `__desc`, acción).
- `.settings` > `.subnav > .subnav__item[aria-current]` + `.settings__body > .set-section` (`__label/__title/__desc` + `__controls`, `.set-line`) · `.set-section--full` · `.danger-zone > .danger-zone__row` · `.btn--danger-outline`.
- `.plans > .plan[aria-current="true"]` (`__head`, `__name`, `__price > __amount + __per`, `__desc`, `__feats`, `__cta`).
- `.meter[data-level="full"]` (`__top`, `__label`, `__val`, `.bar`, `__note`) · `table.table.invoices`.

**graficos.css**
- `svg.chart` con `.chart__grid` `.chart__base` `.chart__axis(--end|--mid)` `.chart__bar(--2..--5)` `.chart__line(--2)` `.chart__area` `.chart__dot` `.chart__hover` `.chart__cursor`.
- `.chart-tip` (`__title`, `__row > b`) · `.legend > .legend__item > .legend__sw(--2..--5|--ok|--warn|--err|--none)`.
- `.spark` (`__label`, `__num > __value + __delta(--down)`, `svg`) · `.uptime > .uptime__row` (`__name`, `__strip > i[data-s="warn|down|none"]`, `__pct`) + `.uptime__axis`.

## Estados por componente

| Componente | Estados |
|---|---|
| Nav / subnav | normal, hover, activo (`aria-current`), con conteo, con alerta, riel colapsado + tooltip |
| Selector de organización | cerrado, abierto (popover), organización actual con check, ítem resaltado |
| Tabla | fila normal, hover, seleccionada, encabezado mixto; orden asc/desc; filtros con valor y para agregar; barra masiva; paginación con anterior/siguiente deshabilitados |
| Barra ⌘K | vacía, con búsqueda y coincidencias marcadas, ítem resaltado, grupos, atajos |
| Modal | estándar, destructivo (`--danger`, `role="alertdialog"`) |
| Panel lateral | cabecera con estado, cuerpo con scroll, pie con acción destructiva |
| Toast | éxito, error, con acción («Deshacer»), apilados; entrada animada |
| Campo | normal, hover, foco (`:focus` o `.is-focus`), deshabilitado, error (`data-invalid`), válido (`data-valid`), contador cerca/pasado del límite |
| Tarjeta de opción | elegida, sin elegir, deshabilitada |
| Carga de archivos | espera, arrastrando (`data-dragover`), subiendo con progreso |
| Vacío / error / carga | vacío con ilustración y CTA; error con reintento y código; esqueleto con brillo; spinner; botón cargando |
| Primeros pasos | hecho, actual, pendiente; progreso |
| Plan / medidor | plan actual, plan disponible; medidor normal y al límite |
| Gráficos | barra en hover con tooltip; franja: en línea, intermitente, caída, apagada |

## Movimiento y accesibilidad

Transiciones de 120–280 ms con `--ease-out`, solo `transform` y `opacity` (el ancho de `.bar` se anima con `scaleX`). Con `prefers-reduced-motion` se apagan las entradas y el brillo del esqueleto; el spinner gira lento. Texto ≥ 12 px, áreas de toque ≥ 24 px (`.check` y `.switch` amplían la suya), foco visible con `--ring`. Íconos: Lucide inline con `class="i"` y `stroke="currentColor"`.
