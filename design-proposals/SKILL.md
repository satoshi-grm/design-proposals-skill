---
name: design-proposals
description: "Use when the user must pick a visual direction before building or redesigning a product. Builds a decision booklet with 3 to 8 visual directions applied to the product's real screens, captured at real size, with a 16:9 PDF, a filterable gallery, a design.md and a tokens.css (shadcn/ui + Tailwind v4) per direction, measured checks (WCAG AA contrast, text of 12 px or more, no clipping) and one firm recommendation."
version: 0.3.0
author: satoshi-grm
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [design, proposals, decision, pdf, ui, saas, tokens]
---

# Propuestas visuales: ver, comparar y elegir

Arma un **cuadernillo de decisión** con 3 a 8 direcciones visuales aplicadas a pantallas reales del producto, capturadas a tamaño real y al doble de resolución. Sale un PDF 16:9 (una pantalla por página), una galería `index.html` con filtro por dirección, y por cada dirección un `design.md` y un `tokens.css` listos para pasar al repo. Cierra con comparación, guía de mezcla y **una recomendación firme**.

## When to Use
User must choose between visual directions before building (new product, redesign, a spec that reaches the visual section without a chosen look).

## Cuándo se usa
- «Propuestas», «opciones», «direcciones visuales», «cómo podría verse», o una spec de proyecto llega a la parte visual sin idea elegida.
- Algo existente se ve «por defecto» (shadcn o Tailwind sin tocar).
- No se usa para un parche, un componente suelto o cuando el usuario ya eligió.
- Cantidad: 3 a 5 por defecto; 6 a 8 cuando pide «más propuestas».

## Qué trae la skill
| Archivo | Para qué |
|---|---|
| `templates/componentes/` | Biblioteca «SaaS pro» en HTML y CSS con tokens de nombres shadcn: app shell, ⌘K, tabla con lote, vacíos, skeletons, toasts, modal y sheet, formularios, tabs, onboarding, ajustes, planes, gráficos SVG, avatares, badges, breadcrumbs, paginación y oscuro. `catalogo.html` los muestra todos por tema. Ver su `README.md`. |
| `templates/ejemplo/` | Proyecto mínimo (dos direcciones, panel 1440×900 y celular 390×844) para copiar como punto de partida. |
| `scripts/render.sh <carpeta>` | Un comando: fuentes, pantallas 2x, catálogo por tema, límites medidos, contraste, `design.md`, `tokens.css`, PDF, galería y hojas de revisión. Sale con 1 si algo no cumple. |
| `scripts/build.py` | Lo que corre `render.sh`; `--solo pantallas --dir x` para iterar una dirección. |
| `scripts/fuentes.py` | Baja Google Fonts a local (capturas sin depender de la red). |
| `scripts/contraste.py` | WCAG 2.x de pares sueltos o de un JSON. |
| `references/revision.md` | Criterios de la revisión con visión, página por página. |
| `references/handoff.md` | Cómo pasa la dirección elegida al repo del producto. |

## Requisitos
- Python 3.10 o más, solo biblioteca estándar.
- Chrome o Chromium del sistema, o `chrome-headless-shell` de Playwright (`python3 -m playwright install chromium-headless-shell`). `CHROME` y `SHOT_CHROME` apuntan a un binario propio.
- Opcional: Pillow (`pip install pillow` en un venv). Con Pillow el PDF lleva las capturas en JPEG y pesa mucho menos, y se arman las hojas de revisión; sin Pillow usa PNG.
- Opcional: `poppler-utils` (`pdfinfo`, `pdftoppm`) para contar páginas y armar las hojas de revisión.
- Opcional: `lucide-static` para los íconos `{i:nombre}`: `npm i lucide-static` en la carpeta del cuadernillo (o en la de arriba), o `LUCIDE_DIR=.../lucide-static/icons`. Sin él, el build avisa y sigue sin íconos.
- Red solo la primera vez, para bajar las fuentes.

## Procedimiento
1. **Contrato (≤ 5 min).** Qué queda fijo (rutas, datos, límites duros, marca del cliente) y qué varía. Si hay sitio o capturas, analizalos primero: colores, tipografías y componentes reales.
2. **Pantallas del producto, no plantillas.** Elegí 3 o 4 pantallas clave con datos verosímiles del dominio (las mismas en todas las direcciones). Escribilas como HTML en `fuente/pantallas/` a su tamaño real: 1440×900 panel, 390×844 celular, 1920×1080 TV. Usá las clases de `base.css` y un `pantallas.css` propio. Nada de cifras grandes en fila ni sidebar genérico: la pantalla es la que el producto necesita.
3. **Direcciones.** En `fuente/propuesta.json`: `proyecto` (nombre del producto), nombre del mundo del cliente, frase, idea en 2 líneas, momento firma, 6 ejes (temperatura, densidad, tipografía, forma, imagen, movimiento; cada dirección difiere de las otras en al menos 3), tokens claro y oscuro, fuentes, a favor y en contra honestos. La composición y la firma van en `fuente/direcciones/<id>.css` (todo bajo `[data-dir="<id>"]`). Nivel de referencia: Linear, Vercel, Stripe, Raycast.
4. **Nada del diseño promedio de IA.** Prohibido: cifras grandes en fila, tarjeta con franja de color, degradé violeta, vidrio (blur de fondo), texto con degradé, tarjetas dentro de tarjetas, marcos de dispositivo dibujados, emojis como íconos. Un solo acento de color; los estados llevan punto o ícono y texto.
5. **Imágenes.** Fotos libres (Unsplash por ID en `images.unsplash.com`, licencia Unsplash) bajadas a `fuente/assets/fotos/`, o SVG propio. Sin créditos pagos. Íconos: Lucide inline con `{i:nombre}`; el build los copia a `fuente/assets/iconos/` (ver Requisitos; nunca instalación global).
6. **Render y chequeos medidos.** `bash scripts/render.sh <carpeta>`. Deja `limites.txt` (texto ≥ 12 px y ≥ 28 px en TV, incluidos `::before/::after`; sin scroll horizontal; sin texto recortado) y `contraste.txt` (AA por dirección y modo). Para iterar: `python3 scripts/build.py <carpeta> --solo pantallas,limites --dir <id>`.
7. **Revisión con visión** de cada PNG y de las hojas `fuente/.build/revision-*.png` con los criterios de `references/revision.md`. Se corrige y se vuelve a renderizar. Una dirección mediocre se descarta y se hace otra.
8. **Cierre en `propuesta.json`:** comparación, 4 a 6 mezclas («tomar X de A y Y de B») y recomendación con alternativa y pasos.
9. **Entrega.** Rutas del PDF y de `index.html`, 3 líneas por dirección y **una sola pregunta**: «¿Cuál elegís, o mezclamos? (recomendada: …)». Al elegir, seguí `references/handoff.md`.

## Salida (carpeta del proyecto, `docs/propuestas/<fecha>-<tema>/`)
`index.html`, `propuestas.pdf`, `pantallas/<dir>-<pantalla>.png`, `<dir>/design.md`, `<dir>/tokens.css`, `contraste.txt`, `limites.txt`, `README.md` y `fuente/` (todo lo necesario para regenerar; `fuente/.build/` y `propuestas.html` son intermedios y van al `.gitignore`).

## Con muchas direcciones
Con 5 o más direcciones, repartí cada dirección en un subagente que solo toca `fuente/direcciones/<id>.css`: vos armás pantallas, `pantallas.css` y la primera dirección; cada subagente renderiza la suya con `--dir <id>` y la revisa con visión. Mostrá 2 pantallas de la primera dirección apenas estén, antes de terminar el resto.

## Pitfalls
- Chrome con `--headless=new` le resta ~87 px de alto al viewport: el build usa `chrome-headless-shell` (Playwright) si está; si no, compensa la ventana.
- Lucide ya no trae íconos de marcas (Instagram, WhatsApp): usá `at-sign`, `message-circle`.
- Marcos de dispositivo dibujados: prohibidos. Las pantallas van a sangre o sobre un fondo liso.
- En las superficies que muestran la marca del cliente (TV, páginas públicas) manda esa marca: la dirección cambia composición, no la marca.
- El `design.md` y los `tokens.css` se generan desde el JSON: no se editan a mano.
- En el PDF las capturas van como JPEG 2x (calidad 85) si hay Pillow: los PNG sin pérdida lo llevan de 20 a 60 MB.
- Un texto escondido con `text-indent` o `overflow` cuenta como recorte: para mostrar parte de un dato, usá un `data-*` y `::after`.

## Se integra bien con
Opcional, si las tenés: una skill que analice un sitio existente (para el paso 1) y una de spec de proyecto (para recibir el bloque «Para la SPEC» del `design.md`). La skill funciona sola sin ninguna de las dos.
