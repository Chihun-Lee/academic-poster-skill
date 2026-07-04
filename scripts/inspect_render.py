#!/usr/bin/env python3
"""Render the poster AND run the QA routine (run after EVERY edit).

  python inspect_render.py index.html --width-mm 610 --height-mm 910 \
      [--png preview.png] [--pdf poster.pdf]

Checks (JSON report on stdout):
  1. overflow  — per .card: (max child bottom) − (card bottom), in px at 2 px/mm.
       > 0        : content overflows / gets clipped → condense text or shrink figures
       < −60 px   : ~>30 mm dead whitespace at the card bottom → restore text or add a bullet
  2. orphans   — text blocks whose LAST line is shorter than 26% of the container
       (a 1–2-word hanging line). Fix by condensing the sentence so the whole line
       disappears; multi-word tails flagged here can be ignored.
       CSS guard: `text-wrap: pretty` prevents most single-word orphans (template has it).

Rendering notes:
  - `body.preview` is added before capture → hides toolbar / dividers / swap handles.
  - Screenshot is full_page at dsf=2 then CROPPED to poster bounds (the editor toolbar
    makes the full page wider than the poster).
  - PDF uses the @page size; screen-emulated with print_background.
"""
import argparse, json
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('html')
ap.add_argument('--width-mm', type=int, default=610)
ap.add_argument('--height-mm', type=int, default=910)
ap.add_argument('--png'); ap.add_argument('--pdf')
args = ap.parse_args()

VW, VH = args.width_mm * 2, args.height_mm * 2   # 2 px per mm

JS = '''() => {
  const out = {overflow: {}, orphans: []};
  for (const card of document.querySelectorAll('.card')) {
    const h2 = card.querySelector('h2');
    const key = h2 ? h2.textContent.slice(0, 16) : 'untitled';
    const cb = card.getBoundingClientRect().bottom;
    let inner = 0;
    for (const el of card.querySelectorAll('*')) {
      const b = el.getBoundingClientRect().bottom; if (b > inner) inner = b;
    }
    out.overflow[key] = Math.round(inner - cb);
  }
  for (const el of document.querySelectorAll('.card li, .card p, .fig .cap, td')) {
    const cs = getComputedStyle(el);
    const lh = parseFloat(cs.lineHeight);
    if (!lh) continue;
    const nLines = Math.round(el.getBoundingClientRect().height / lh);
    if (nLines < 2) continue;
    const range = document.createRange(); range.selectNodeContents(el);
    const rects = [...range.getClientRects()].filter(r => r.width > 1);
    const last = rects[rects.length - 1];
    const cw = el.getBoundingClientRect().width;
    if (last && last.width < cw * 0.26)
      out.orphans.push({lastLinePct: Math.round(100 * last.width / cw),
                        tail: el.textContent.trim().slice(-30)});
  }
  return out;
}'''

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': VW, 'height': VH}, device_scale_factor=2)
    pg.goto('file://' + __import__('os').path.abspath(args.html))
    pg.wait_for_timeout(2500)
    pg.evaluate("document.body.classList.add('preview')")
    report = pg.evaluate(JS)
    print(json.dumps(report, indent=1, ensure_ascii=False))
    if args.png:
        pg.screenshot(path=args.png + '.full.png', full_page=True)
        from PIL import Image
        im = Image.open(args.png + '.full.png')
        im.crop((0, 0, VW * 2, VH * 2)).save(args.png)
        __import__('os').remove(args.png + '.full.png')
    if args.pdf:
        pg.emulate_media(media='screen')
        pg.pdf(path=args.pdf, width=f'{args.width_mm}mm', height=f'{args.height_mm}mm',
               print_background=True, page_ranges='1')
    b.close()
