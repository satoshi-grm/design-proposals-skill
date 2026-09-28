# Legacy booklets (Spanish names)

Booklets made with earlier versions use Spanish keys and folder names. They still render.

## Detection
If the booklet folder contains `fuente/`, the build switches to legacy mode and uses the old names for **inputs and outputs**, so an old booklet regenerates with the same files. Otherwise it uses the new names.

Legacy mode only affects file names. Output language is set by `lang` in the proposal file, which defaults to `"en"`. Add `"lang": "es"` to keep Spanish output.

## Folders and files
| Old | New |
|---|---|
| `fuente/` | `source/` |
| `fuente/propuesta.json` | `source/proposal.json` |
| `fuente/pantallas/` | `source/screens/` |
| `fuente/direcciones/<id>.css` | `source/directions/<id>.css` |
| `fuente/componentes/` | `source/components/` |
| `fuente/assets/fuentes/fuentes.css` | `source/assets/fonts/fonts.css` |
| `assets/iconos/` | `assets/icons/` |
| `assets/fotos/` | `assets/photos/` |
| `pantallas/<dir>-<screen>.png` | `screens/<dir>-<screen>.png` |
| `propuestas.pdf` | `proposals.pdf` |
| `propuestas.html` | `proposals.html` |
| `contraste.txt` | `contrast.txt` |
| `limites.txt` | `limits.txt` |
| `.build/revision-N.png` | `.build/review-N.png` |
| `{{NOMBRE}}` | `{{NAME}}` |
| `{{LATIDOS}}` | `{{BEATS}}` |

## Keys in the proposal file
Old keys are mapped to new ones at load time, at any depth. Token names inside `tokens` are not renamed.

| Old | New |
|---|---|
| `titulo` | `title` |
| `proyecto` | `project` |
| `fecha` | `date` |
| `contexto` | `context` |
| `fijo` | `fixed` |
| `varia` | `varies` |
| `como_leer` | `how_to_read` |
| `datos_ficticios` | `fictional_data` |
| `componentes_pantallas` | `screen_components` |
| `portada_pantalla` | `cover_screen` |
| `catalogo_alto` | `catalog_height` |
| `pantallas` | `screens` |
| `archivo` | `file` |
| `ancho` | `width` |
| `alto` | `height` |
| `nombre` | `name` |
| `nota` | `note` |
| `modo` | `mode` |
| `pagina` | `page` (value `movil` becomes `mobile`) |
| `direcciones` | `directions` |
| `frase` | `tagline` |
| `firma` | `signature` |
| `fuentes` | `fonts` |
| `referencias` | `references` |
| `ejes` | `axes` |
| `temperatura` | `temperature` |
| `densidad` | `density` |
| `tipografia` | `typography` |
| `forma` | `shape` |
| `imagen` | `imagery` |
| `movimiento` | `motion` |
| `a_favor` | `pros` |
| `en_contra` | `cons` |
| `notas` | `notes` |
| `pares_extra` | `extra_pairs` |
| `apertura_img` | `opening_image` |
| `apertura_pos` | `opening_position` |
| `comparativa` | `comparison` |
| `columnas` | `columns` |
| `valores` | `values` |
| `mezcla_regla` | `mix_rule` |
| `mezclas` | `mixes` |
| `texto` | `text` |
| `imgs` | `images` |
| `recomendacion` | `recommendation` |
| `base_nombre` | `base_name` |
| `resumen` | `summary` |
| `porque` | `why` |
| `alternativa` | `alternative` |
| `pasos` | `steps` |
| `pregunta` | `question` |

Unchanged: `version`, `css`, `google_fonts`, `id`, `idea`, `tokens`, `base`.
