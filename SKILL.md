---
name: academic-poster
description: Build a print-ready, browser-editable academic conference poster (React single-file HTML) from a paper — figures freshly drawn by Gemini, typography matched to real AI-conference posters, automated overflow/orphan QA, PDF + shareable standalone export. Use when the user asks to make a conference/workshop poster.
---

# Academic Poster — paper → editable HTML → print PDF

Based on [ethanweber/posterskill](https://github.com/ethanweber/posterskill), extended with a
production pipeline refined on a real ICML workshop poster: Gemini-drawn figures,
typography rules measured from real conference posters, an automated QA loop
(overflow + orphan-line detection), and a self-contained shareable export.

## Phase 0 — Gather facts before touching code

1. **Exact board spec**: orientation + physical size in **mm** (workshop poster sizes often
   differ from the main conference — verify, don't assume). Set `@page` and `body` to those mm.
2. **Read the paper**; extract: 1-line claim, the 2–4 core sections, the evaluation protocol,
   and anything promotional the user wants (lab intro, recruiting block, funding line).
3. Ask the user for: logos, author ID photos, QR targets (profile pages, promo video, paper).
4. If the user has example posters they like, measure them (word count, font pt at true scale)
   before designing. Real-world reference: a good A1 poster ≈ 400 words, body 18–20 pt single
   size; a NeurIPS poster at 1.2 m width uses 48–54 pt body. See `reference/poster_typography.md`.

## Phase 1 — Template setup (`template.html`)

Copy `template.html`, then customize the marked `CUSTOMIZE` blocks only:
- `:root` colors → ONE accent family (the strongest poster in our reference study used a
  single institutional blue; two-institution posters read better unified than half-and-half).
- `--font-scale`: tune so body lands at 18–20 pt equivalent for A1-class posters.
  Title 48–54 pt, section headers 30–32 pt, captions ~1 pt-class below body. 4 levels max.
- `CARD_REGISTRY`: one entry per card. `DEFAULT_LAYOUT`: columns + card order.
- `POSTER_ID`: bump whenever card ids change — it versions the localStorage key
  (stale saved configs from an older poster otherwise silently delete cards / break logos;
  `loadInitialConfig` also validates card ids and re-sources logo paths as a second guard).

**Editing gotcha**: when programmatically replacing the `CARD_REGISTRY` → `DEFAULT_LAYOUT`
span, it is easy to drop the last card + closing `};`. After every bulk replace, assert each
card key still exists in the file. Prefer targeted string replacement over whole-block rewrite.

### Header/logo rules (learned the hard way)
- On a colored header band, render logos white via `filter:brightness(0) invert(1)`
  (needs source PNGs with alpha).
- **Trim each logo PNG to its content bbox** so the wordmarks' left edges align when stacked.
- Match *lettering* height, not image height: if one logo's wordmark occupies 68% of its
  image height and the other 100%, render the first ~1.5× taller for equal-looking text.

## Phase 2 — Figures: Gemini-drawn, never pasted screenshots

Redraw every figure in a consistent style with `scripts/gen_img.py`. It works in two modes:
- **API mode**: `GEMINI_API_KEY` env var set → calls `gemini-3-pro-image`
  (fallback `gemini-2.5-flash-image`), aspect + 2K configurable.
- **Manual mode**: no key → it prints the fully-assembled prompt for the user to paste into
  Gemini/AI Studio themselves, then post-process the saved file with `--postprocess`.

The script automatically appends the battle-tested constraints:
- **SOLID PURE WHITE background** — never ask Gemini for transparency: it *paints* a fake
  checkerboard mosaic while alpha stays 255. Generate on white and trim.
- **Watermark handling**: the prompt reserves the bottom ~8% as an empty white band, so the
  visible watermark lands there; post-processing crops that band, then `trim_white`s the rest.
- **Big labels** (~5% of image height) — small text dies at poster print scale.

Tips:
- To composite REAL photos (your actual instruments) into a diagram, pass them as extra
  `--src` images and instruct "replace the photo in node X with IMAGE 2, cut out on white".
- Fixing a typo in a generated figure: re-run with the flawed image as `--src` and ask for a
  pixel-identical redraw with only the word corrected.
- Place figures with `class="fig nat"` (natural width-bound sizing) — fixed-height boxes
  letterbox or overflow. To shrink one figure, inline `style={{width:'92%'}}` (the wrap centers it).

## Phase 3 — Write the text (content budget)

- Body bullets in full sentences but tight; **≤ ~450 words** total for A1-class.
- Bold the load-bearing phrases (scannable from 2 m), one bold run per bullet max.
- Keep ALL paper-critical details the audience will ask about (evaluation protocol, funding,
  roadmap table) — condensing happens in the QA loop, not by omission up front.
- `text-align: justify` + `text-wrap: pretty` are already in the template.

## Phase 4 — QA loop (run after EVERY edit)

```bash
python scripts/inspect_render.py index.html --width-mm 610 --height-mm 910 \
    --png preview.png --pdf poster.pdf
```
Iterate until the report is clean:
- **overflow > 0** on a card → content clipped: condense the longest bullet(s) (drop
  parentheticals first) or shrink a figure a few %. Changes of one line ≈ 2 px/mm × line-height.
- **overflow < −60 px** → conspicuous dead space at the card bottom: restore previously
  condensed text or add one genuinely-new bullet from the paper. (Don't stretch line-height.)
- **orphans** → a 1–2-word hanging last line: shorten that sentence so the line disappears
  entirely (removing ~the width of the orphan from anywhere in the paragraph pulls it up).
  Multi-word tails (4+ words) flagged at 20–26% width are fine — ignore.
- Then **look at the PNG yourself** — measurements miss things like a figure's internal
  whitespace, duplicated labels, or a caption fighting a figure. Truncate card-name keys
  ≥ 12 chars in reports (8-char keys once collided and hid a 50 mm gap for three rounds).

## Phase 5 — Deliverables

1. `poster.pdf` — exact mm size, print-ready (verify with PyMuPDF: page size in mm).
2. `preview.png` — for chat/quick review.
3. Shareable editable file:
   ```bash
   python scripts/build_standalone.py index.html poster_standalone.html            # ~2 MB
   python scripts/build_standalone.py index.html poster_standalone_HQ.html --lossless  # print-quality
   ```
   One file, works offline, opens in any browser. Recipient edits layout (drag dividers,
   swap cards via the ⧫ handle, A± font) and sends back **Copy Config** JSON, which you bake
   into `DEFAULT_LAYOUT`.
   **Test standalones against a POISONED localStorage** (seed an old config under the previous
   key and under the current key with wrong card ids) — a fresh browser always passes and
   will hide this entire bug class.

## Recurring pitfalls index

| Symptom | Cause / fix |
|---|---|
| "Transparent" figure shows grey checkerboard | Gemini painted it; regenerate on solid white + trim |
| Cards vanish / logos break for one user only | stale localStorage config; bump `POSTER_ID`, keep validation |
| Toolbar or ⧫ icons in the PDF | render without adding `body.preview`; always add it before capture |
| Whole column overflows horizontally | header children too wide (e.g. side-by-side logos) — stack them |
| One-word line after a bullet ("loop") | orphan; condense sentence, keep `text-wrap:pretty` on |
| Replaced text "didn't take" silently | bold/entity markup differs from what you assumed — grep the actual bytes first |
| Full-page screenshot wider than poster | editor toolbar extends the page; crop to poster bounds |
