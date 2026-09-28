# Ejemplo mínimo

Copiá esta carpeta a `docs/propuestas/<fecha>-<tema>/` del proyecto y corré `bash <skill>/scripts/render.sh <carpeta>`. Trae dos direcciones («Banco de trabajo» y «Pizarra de turnos») y dos pantallas (panel 1440×900 y celular 390×844) de un producto inventado, Taller Sur, para ver el circuito completo (tokens → captura 2x → design.md → tokens.css → PDF → galería). Sumá direcciones en `fuente/propuesta.json` (cada una con `tokens.light` y `tokens.dark`), pantallas en `fuente/pantallas/` y la composición de cada dirección en `fuente/direcciones/<id>.css`.

En las plantillas: `{{ATTRS}}` y `{{HEAD}}` los completa el build; `{i:nombre}` es un ícono Lucide; `{{A}}` es la ruta a `fuente/assets/`.
