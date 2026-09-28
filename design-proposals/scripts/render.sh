#!/usr/bin/env bash
# One command: 2x screens, per-theme catalog, limits, contrast, design.md, tokens.css, 16:9 PDF, gallery and review sheets.
# Usage: render.sh <booklet-folder> [steps]   (steps: themes,screens,catalog,limits,contrast,docs,pdf,gallery,review)
# Legacy booklets (fuente/propuesta.json) keep their old file names.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
FOLDER="$(cd "${1:?Usage: render.sh <folder> [steps]}" && pwd)"
STEPS="${2:-themes,screens,catalog,limits,contrast,docs,pdf,gallery,review}"
if [ -d "$FOLDER/fuente" ]; then
  PROPOSAL="$FOLDER/fuente/propuesta.json"; FONTS_DIR="$FOLDER/fuente/assets/fuentes"; FONTS_CSS=fuentes.css
else
  PROPOSAL="$FOLDER/source/proposal.json"; FONTS_DIR="$FOLDER/source/assets/fonts"; FONTS_CSS=fonts.css
fi
[ -f "$PROPOSAL" ] || { echo "Missing $PROPOSAL (copy templates/example/ to start)" >&2; exit 1; }
if [ ! -f "$FONTS_DIR/$FONTS_CSS" ]; then
  # fonts declared in proposal.json -> local files
  mapfile -t FAMILIES < <(python3 -c "import json,sys; print('\n'.join(json.load(open(sys.argv[1])).get('google_fonts', [])))" "$PROPOSAL")
  if [ "${#FAMILIES[@]}" -gt 0 ] && [ -n "${FAMILIES[0]}" ]; then python3 "$HERE/fonts.py" --css "$FONTS_CSS" "$FONTS_DIR" "${FAMILIES[@]}"; fi
fi
python3 "$HERE/build.py" "$FOLDER" --only "$STEPS"
for PDF in proposals.pdf propuestas.pdf; do
  if [ -f "$FOLDER/$PDF" ]; then
    command -v pdfinfo >/dev/null && pdfinfo "$FOLDER/$PDF" | grep -E 'Pages|Page size'
    echo "Done: $FOLDER/index.html and $FOLDER/$PDF"
  fi
done
