# Handoff: de la dirección elegida al repo del producto

Lo que genera el cuadernillo por dirección y adónde va:

| Archivo | Destino | Cómo |
|---|---|---|
| `<dir>/tokens.css` | `src/app/globals.css` (o la hoja global) del repo | Reemplaza los bloques `:root` y `.dark` de shadcn/ui. Trae `@theme inline` para Tailwind v4 (`bg-primary`, `font-display`, `rounded-lg`…). Las variables tienen los nombres de shadcn: no hay mapeo que hacer, solo pegar. Sin shadcn, sirven igual como variables CSS. |
| `<dir>/design.md` | `docs/design.md` del repo | Frontmatter con tokens (colores, tipografía, radios, componentes) y cuerpo con identidad, sistema, componentes con estados, layout y reglas. Lo lee cualquier agente que construya la interfaz. |
| Bloque «Para la SPEC» del `design.md` | Spec o README técnico del proyecto, sección de diseño | Se pega tal cual: idea, firma, tokens, tipografía, forma, densidad, movimiento y contraste medido. |
| Tabla de componentes del `design.md` | Spec o brief de quien implementa | Lista de componentes con sus estados obligatorios; la biblioteca de `templates/componentes/` es la referencia visual. |
| `pantallas/<dir>-*.png` | Brief de quien implementa | Referencia visual de las pantallas clave: se reproducen con los componentes del proyecto y el CSS de la firma. |

Pasos:
1. El usuario elige (o mezcla). Si mezcla, se edita `fuente/propuesta.json` con la mezcla como dirección nueva y se vuelve a correr `render.sh`: así el `tokens.css` sale de una sola fuente.
2. Una nota de decisión corta («Dirección visual») con el enlace al PDF, en el lugar donde el proyecto guarde sus decisiones.
3. Pegar el bloque «Para la SPEC» en la spec, con los límites duros medidos (contraste AA, texto ≥ 12 px, sin recortes, sin scroll horizontal) como criterios verificables.
4. En el brief de quien implementa: «tokens desde `docs/propuestas/<carpeta>/<dir>/tokens.css`; firma según `design.md` §3.2; pantallas de referencia en `pantallas/`».
