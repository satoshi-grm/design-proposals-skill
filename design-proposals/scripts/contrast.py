#!/usr/bin/env python3
"""WCAG 2.x contrast between color pairs.

Usage:
  contrast.py '#1e252c/#fafaf7' '#4e5a66/#ffffff:text' '#6e7a86/#ffffff:border'
  contrast.py --json pairs.json   # {"pairs": [["#fg", "#bg", "text|large|border"], ...]}

Default kind: text (4.5:1). large and border: 3:1.
Exits with code 1 if any pair fails.
"""
import json
import sys

MINIMUM = {'text': 4.5, 'large': 3.0, 'border': 3.0}
KINDS = {'texto': 'text', 'grande': 'large', 'borde': 'border'}  # legacy names


def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexcolor):
    h = hexcolor.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    if len(h) != 6:
        raise ValueError(f'invalid color: {hexcolor}')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def parse_arg(s):
    kind = 'text'
    if ':' in s:
        s, kind = s.rsplit(':', 1)
    fg, bg = s.split('/')
    return fg, bg, KINDS.get(kind, kind)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == '--json':
        data = json.load(open(argv[1]))
        pairs = [(p[0], p[1], KINDS.get(p[2], p[2]) if len(p) > 2 else 'text') for p in data.get('pairs', data.get('pares', []))]
    else:
        pairs = [parse_arg(a) for a in argv]
    ok = 0
    min_text = None
    for fg, bg, kind in pairs:
        r = contrast(fg, bg)
        passes = r >= MINIMUM.get(kind, 4.5)
        ok += passes
        if kind == 'text':
            min_text = r if min_text is None else min(min_text, r)
        print(f"{'OK ' if passes else 'NO '} {fg} on {bg} [{kind}] {r:.2f}:1")
    summary = f'{ok}/{len(pairs)} pairs pass AA'
    if min_text is not None:
        summary += f' · min text {min_text:.2f}:1'
    print(summary)
    return 0 if ok == len(pairs) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
