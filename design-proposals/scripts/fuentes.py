#!/usr/bin/env python3
"""Baja familias de Google Fonts (woff2) a una carpeta y escribe fuentes.css con rutas locales.

Así las capturas no dependen de la red ni del tiempo de carga.

Uso:
  fuentes.py <carpeta-salida> "Instrument Sans:400;500;600" "IBM Plex Mono:400;500" ...
  (pesos separados por «;»; para itálica: "Bodoni Moda:ital,wght@0,400;1,400")
"""
import os
import re
import sys
import urllib.parse
import urllib.request

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36'


def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def familia_query(spec):
    nombre, _, pesos = spec.partition(':')
    q = 'family=' + urllib.parse.quote_plus(nombre.strip())
    if pesos:
        q += ':' + (pesos if '@' in pesos else 'wght@' + pesos)
    return q


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    out = argv[0]
    os.makedirs(out, exist_ok=True)
    url = 'https://fonts.googleapis.com/css2?' + '&'.join(familia_query(s) for s in argv[1:]) + '&display=block'
    css = _get(url).decode()
    # solo los subconjuntos latin y latin-ext: alcanza para castellano y pesa poco
    bloques = re.findall(r'/\* ([\w-]+) \*/\s*(@font-face \{.*?\})', css, re.S)
    salida = []
    for subset, bloque in bloques:
        if subset not in ('latin', 'latin-ext'):
            continue
        for u in re.findall(r'url\((https://[^)]+)\)', bloque):
            nombre = re.sub(r'[^\w.-]', '_', urllib.parse.urlparse(u).path.split('/', 2)[-1])
            destino = os.path.join(out, nombre)
            if not os.path.exists(destino):
                with open(destino, 'wb') as f:
                    f.write(_get(u))
            bloque = bloque.replace(u, nombre)
        salida.append(bloque)
    with open(os.path.join(out, 'fuentes.css'), 'w') as f:
        f.write('\n'.join(salida) + '\n')
    print(f'{len(salida)} @font-face en {out}/fuentes.css')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
