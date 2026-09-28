# Revisión con visión

Se mira **cada PNG** de `pantallas/` a tamaño completo y **cada página** del PDF en las hojas `fuente/.build/revision-*.png`. Lo que falla se corrige y se vuelve a renderizar; en la verificación se anota qué se miró y qué se corrigió.

## Por pantalla
| Criterio | Pasa si |
|---|---|
| Jerarquía | Hay un solo punto focal y se encuentra en 2 segundos (la vista previa en el editor, la frase de estado en el monitor, el botón principal en el celular, el producto en la TV). |
| Aire | Grupos separados por espacio antes que por cajas; nada pegado a los bordes; ritmo entre zonas densas y abiertas. |
| Un solo acento | Un color de acción; los estados llevan punto o ícono y texto. |
| Nada del promedio de IA | Ninguno de los hábitos del diseño promedio de IA (cifras grandes en fila, tarjeta con franja de color, degradé violeta, vidrio, texto con degradé, tarjetas en tarjetas, marcos de dispositivo, emojis). |
| Firma | El momento firma de la dirección se ve sin buscarlo, y solo donde se definió. |
| Límites duros | Texto ≥ 12 px (TV ≥ 28 px a 1080p, margen seguro 5 %), controles de una fila con la misma altura, nada cortado, encimado ni partido en dos líneas por error. |
| Datos | Los mismos datos en todas las direcciones; nombres largos truncados con criterio. |

## Por página del PDF
| Criterio | Pasa si |
|---|---|
| Escala | La pantalla ocupa la página (1440 px de 1600) y el texto de la interfaz se lee al 100 % de zoom. |
| Texto propio | Ningún texto del cuadernillo por debajo de 13 px; leyendas de 3 líneas o menos. |
| Corte | Nada desborda la página 16:9; imágenes sin deformar. |
| Ritmo | Apertura, pantallas, celular + componentes y TV alternan densidad; la recomendación se lee sola. |

## Antes y después
Si hay un cuadernillo anterior, se arma `antes-despues.png` con la página equivalente del viejo y del nuevo, lado a lado y a la misma altura.
