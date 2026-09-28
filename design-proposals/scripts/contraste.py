#!/usr/bin/env python3
"""Contraste WCAG 2.x entre pares de colores.

Uso:
  contraste.py '#1e252c/#fafaf7' '#4e5a66/#ffffff:texto' '#6e7a86/#ffffff:borde'
  contraste.py --json pares.json   # {"pares": [["#fg", "#bg", "texto|grande|borde"], ...]}

Tipo por defecto: texto (4,5:1). grande y borde: 3:1.
Sale con código 1 si algún par no cumple.
"""
import json
import sys

MINIMO = {'texto': 4.5, 'grande': 3.0, 'borde': 3.0}


def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(hexcolor):
    h = hexcolor.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    if len(h) != 6:
        raise ValueError(f'color inválido: {hexcolor}')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def parse_arg(s):
    tipo = 'texto'
    if ':' in s:
        s, tipo = s.rsplit(':', 1)
    fg, bg = s.split('/')
    return fg, bg, tipo


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == '--json':
        pares = [tuple(p) + (('texto',) if len(p) == 2 else ()) for p in json.load(open(argv[1]))['pares']]
    else:
        pares = [parse_arg(a) for a in argv]
    ok = 0
    minimo_texto = None
    for fg, bg, tipo in pares:
        r = contraste(fg, bg)
        cumple = r >= MINIMO.get(tipo, 4.5)
        ok += cumple
        if tipo == 'texto':
            minimo_texto = r if minimo_texto is None else min(minimo_texto, r)
        print(f"{'OK ' if cumple else 'NO '} {fg} sobre {bg} [{tipo}] {r:.2f}:1")
    resumen = f'{ok}/{len(pares)} pares cumplen AA'
    if minimo_texto is not None:
        resumen += f' · texto mínimo {minimo_texto:.2f}:1'.replace('.', ',')
    print(resumen)
    return 0 if ok == len(pares) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
