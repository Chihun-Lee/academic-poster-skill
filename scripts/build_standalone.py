#!/usr/bin/env python3
"""Export the poster as ONE self-contained HTML file (share with anyone, works offline).

  python build_standalone.py index.html out.html            # compressed (~2 MB, share/review)
  python build_standalone.py index.html out.html --lossless # original PNGs (print-quality, big)

What it does (and why):
  - Pre-compiles the <script type="text/babel"> JSX with esbuild → Babel (2.6 MB CDN) not needed.
  - Inlines React + ReactDOM UMD.
  - Drops KaTeX tags (the template guards `renderMathInElement` — safe if you use no math;
    if you DO use math, inline KaTeX yourself).
  - Inlines the Nunito font as a @font-face data URI (Google Fonts serves ONE variable woff2
    for all weights — deduped to a single `font-weight: 400 900` face).
  - Inlines every image referenced in the app JS as a data URI. Compressed mode: figures
    max 1500 px JPEG q86, photos 500 px q88; QR codes and logos stay PNG (logos need alpha
    if you use `filter: invert(1)` on a colored header).

Requires: node/npx (esbuild), Pillow. Internet needed once (React + font download).
"""
import argparse, base64, io, json, os, re, subprocess, sys, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--lossless', action='store_true')
args = ap.parse_args()

src_dir = os.path.dirname(os.path.abspath(args.src)) or '.'
s = open(args.src).read()
css = s.split('<style>')[1].split('</style>')[0]
jsx = s.split('<script type="text/babel">')[1].split('</script>')[0]
title = re.search(r'<title>(.*?)</title>', s).group(1)

# 1) compile JSX
open('/tmp/_app.jsx', 'w').write(jsx)
subprocess.run(['npx', 'esbuild', '/tmp/_app.jsx', '--loader:.jsx=jsx',
                '--format=iife', '--outfile=/tmp/_app.js'], check=True)
app = open('/tmp/_app.js').read()

# 2) React UMD
def fetch(url):
    return urllib.request.urlopen(url, timeout=60).read().decode()
react = fetch('https://unpkg.com/react@18/umd/react.production.min.js')
rdom = fetch('https://unpkg.com/react-dom@18/umd/react-dom.production.min.js')

# 3) font (Nunito variable; swap the family here if your template uses another)
req = urllib.request.Request(
    'https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap',
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120 Safari/537.36'})
fcss = urllib.request.urlopen(req, timeout=60).read().decode()
furl = re.search(r'url\((\S+?\.woff2)\)', fcss).group(1)
fb64 = base64.b64encode(urllib.request.urlopen(furl, timeout=60).read()).decode()
fonts = ("@font-face { font-family:'Nunito'; font-style:normal; font-weight:400 900; "
         f"src:url(data:font/woff2;base64,{fb64}) format('woff2'); }}")

# 4) images referenced in the compiled JS
names = sorted(set(re.findall(r'["\']([\w./-]+\.(?:png|jpe?g))["\']', app)), key=len, reverse=True)
from PIL import Image
def uri_for(name):
    path = os.path.join(src_dir, name)
    if args.lossless or name.endswith(('.jpg', '.jpeg')) or os.path.getsize(path) < 120_000:
        ext = 'jpeg' if name.endswith(('.jpg', '.jpeg')) else 'png'
        return f'data:image/{ext};base64,' + base64.b64encode(open(path, 'rb').read()).decode()
    im = Image.open(path).convert('RGB')
    maxw, q = (500, 88) if 'photo' in name else (1500, 86)
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

for name in names:
    if not os.path.exists(os.path.join(src_dir, name)):
        print('WARN missing', name); continue
    u = uri_for(name)
    for q in ['"', "'"]:
        app = app.replace(q + name + q, q + u + q)

left = re.findall(r'["\'][\w./-]+\.(?:png|jpe?g)["\']', app)
if left:
    print('WARN unresolved image refs:', left[:5])

html = (f'<title>{title}</title>\n<style>\n{fonts}\n{css}\n</style>\n'
        f'<div id="root"></div>\n<script>{react}</script>\n<script>{rdom}</script>\n'
        f'<script>{app}</script>\n')
open(args.out, 'w').write(html)
print('wrote', args.out, round(len(html) / 1e6, 1), 'MB')
