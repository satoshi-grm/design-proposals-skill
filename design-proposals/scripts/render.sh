#!/usr/bin/env bash
# Un comando: pantallas 2x, catálogo por tema, contraste, design.md, tokens.css, PDF 16:9, galería y hojas de revisión.
# Uso: render.sh <carpeta-del-cuadernillo> [pasos]   (pasos: temas,pantallas,catalogo,limites,contraste,docs,pdf,galeria,revision)
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
CARPETA="$(cd "${1:?Uso: render.sh <carpeta> [pasos]}" && pwd)"
PASOS="${2:-temas,pantallas,catalogo,limites,contraste,docs,pdf,galeria,revision}"
[ -f "$CARPETA/fuente/propuesta.json" ] || { echo "Falta $CARPETA/fuente/propuesta.json (copiá templates/ejemplo/)" >&2; exit 1; }
if [ ! -f "$CARPETA/fuente/assets/fuentes/fuentes.css" ]; then
  # fuentes declaradas en propuesta.json → locales
  mapfile -t FAMILIAS < <(python3 -c "import json,sys; print('\n'.join(json.load(open(sys.argv[1])).get('google_fonts', [])))" "$CARPETA/fuente/propuesta.json")
  [ "${#FAMILIAS[@]}" -gt 0 ] && python3 "$AQUI/fuentes.py" "$CARPETA/fuente/assets/fuentes" "${FAMILIAS[@]}"
fi
python3 "$AQUI/build.py" "$CARPETA" --solo "$PASOS"
command -v pdfinfo >/dev/null && [ -f "$CARPETA/propuestas.pdf" ] && pdfinfo "$CARPETA/propuestas.pdf" | grep -E 'Pages|Page size'
echo "Listo: $CARPETA/index.html y $CARPETA/propuestas.pdf"
