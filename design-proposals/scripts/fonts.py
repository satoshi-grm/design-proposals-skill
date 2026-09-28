#!/usr/bin/env python3
"""Downloads Google Fonts families (woff2) into a folder and writes fonts.css with local paths.

That way screenshots depend neither on the network nor on load timing.

Usage:
  fonts.py [--css NAME] <output-folder> "Instrument Sans:400;500;600" "IBM Plex Mono:400;500" ...
  (weights separated by ";"; for italics: "Bodoni Moda:ital,wght@0,400;1,400"; --css defaults to fonts.css)
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


def family_query(spec):
    name, _, weights = spec.partition(':')
    q = 'family=' + urllib.parse.quote_plus(name.strip())
    if weights:
        q += ':' + (weights if '@' in weights else 'wght@' + weights)
    return q


def main(argv):
    css_name = 'fonts.css'
    if argv[:1] == ['--css'] and len(argv) > 1:
        css_name, argv = argv[1], argv[2:]
    if len(argv) < 2:
        print(__doc__)
        return 2
    out = argv[0]
    os.makedirs(out, exist_ok=True)
    url = 'https://fonts.googleapis.com/css2?' + '&'.join(family_query(s) for s in argv[1:]) + '&display=block'
    css = _get(url).decode()
    # only the latin and latin-ext subsets: enough for Western languages and light
    blocks = re.findall(r'/\* ([\w-]+) \*/\s*(@font-face \{.*?\})', css, re.S)
    result = []
    for subset, block in blocks:
        if subset not in ('latin', 'latin-ext'):
            continue
        for u in re.findall(r'url\((https://[^)]+)\)', block):
            name = re.sub(r'[^\w.-]', '_', urllib.parse.urlparse(u).path.split('/', 2)[-1])
            dest = os.path.join(out, name)
            if not os.path.exists(dest):
                with open(dest, 'wb') as f:
                    f.write(_get(u))
            block = block.replace(u, name)
        result.append(block)
    with open(os.path.join(out, css_name), 'w') as f:
        f.write('\n'.join(result) + '\n')
    print(f'{len(result)} @font-face in {out}/{css_name}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
