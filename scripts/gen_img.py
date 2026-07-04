#!/usr/bin/env python3
"""Generate poster figures with Gemini image models — or print a ready-to-paste prompt.

Two modes:
  1. API mode (GEMINI_API_KEY env var set):
       python gen_img.py --prompt-file p_motiv.txt --out motiv.png --aspect 16:9 [--src ref1.png --src ref2.jpg]
  2. Manual mode (no key): the fully-assembled prompt is printed — paste it into the
     Gemini app / AI Studio yourself, save the result, then post-process it:
       python gen_img.py --postprocess raw.png --out motiv.png

Watermark strategy (applied in BOTH modes):
  - The prompt automatically asks the model to leave the bottom ~8% of the image as an
    EMPTY solid-white margin band. Gemini's visible watermark lands in that band.
  - Post-processing crops the bottom band away, then trims all white borders (trim_white),
    so the delivered figure is watermark-free and tightly cropped.

Hard-won rules baked into the prompt suffix:
  - "SOLID PURE WHITE background" — Gemini fakes transparency by PAINTING a checkerboard
    mosaic (alpha stays 255). Never ask for transparency; ask for white and trim.
  - Large text: labels ~5% of image height, or they become unreadable at poster scale.
"""
import argparse, base64, json, os, sys, time, urllib.request, urllib.error

PROMPT_SUFFIX = (
    "\n\nMANDATORY RENDERING RULES:\n"
    "- SOLID PURE WHITE (#FFFFFF) background. NO checkerboard, NO transparency pattern, NO grey mosaic.\n"
    "- All text labels LARGE and BOLD (letter height roughly 4-5% of image height) so they stay readable when printed small.\n"
    "- Leave the BOTTOM ~8% of the image as a completely EMPTY solid white margin band (no content there); a watermark may be placed in that band.\n"
    "- Correct English spelling on every label."
)

MODELS = ['gemini-3-pro-image', 'gemini-2.5-flash-image', 'gemini-3-pro-image']


def enc(path):
    mime = 'image/jpeg' if path.lower().endswith(('.jpg', '.jpeg')) else 'image/png'
    return {"inline_data": {"mime_type": mime,
                            "data": base64.b64encode(open(path, 'rb').read()).decode()}}


def generate(key, prompt, srcs, aspect, out_raw):
    parts = [enc(p) for p in srcs] + [{"text": prompt}]
    body = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"],
                             "imageConfig": {"aspectRatio": aspect, "imageSize": "2K"}}
    }).encode()
    for m in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
        try:
            d = json.load(urllib.request.urlopen(
                urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}),
                timeout=360))
            for c in d.get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    if "inlineData" in p:
                        open(out_raw, "wb").write(base64.b64decode(p["inlineData"]["data"]))
                        print("generated via", m)
                        return True
            print("no image from", m)
        except urllib.error.HTTPError as e:
            print("HTTP", e.code, m, e.read()[:200].decode('utf8', 'ignore')); time.sleep(3)
        except Exception as e:
            print(m, "FAIL", str(e)[:150]); time.sleep(3)
    return False


def postprocess(raw_path, out_path, bottom_crop=0.08, white_thresh=244, pad=8):
    """Crop the bottom watermark band, then trim white borders tight."""
    from PIL import Image
    import numpy as np
    im = Image.open(raw_path).convert('RGB')
    w, h = im.size
    im = im.crop((0, 0, w, int(h * (1 - bottom_crop))))          # drop watermark band
    a = np.array(im)
    mask = (a.min(axis=2) < white_thresh)                        # non-white content
    ys, xs = np.where(mask)
    if len(xs):
        box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0),
               min(xs.max() + pad, im.width), min(ys.max() + pad, im.height))
        im = im.crop(box)
    im.save(out_path)
    print("saved", out_path, im.size)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--prompt-file'); ap.add_argument('--prompt')
    ap.add_argument('--out', required=True)
    ap.add_argument('--aspect', default='16:9')
    ap.add_argument('--src', action='append', default=[],
                    help='optional reference image(s) — e.g. real equipment photos to composite in')
    ap.add_argument('--postprocess', help='skip generation; crop+trim this already-generated file')
    ap.add_argument('--bottom-crop', type=float, default=0.08)
    args = ap.parse_args()

    if args.postprocess:
        postprocess(args.postprocess, args.out, args.bottom_crop); sys.exit(0)

    prompt = (open(args.prompt_file).read() if args.prompt_file else args.prompt or '') + PROMPT_SUFFIX
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        print("=" * 60)
        print("GEMINI_API_KEY not set — MANUAL MODE.")
        print("Paste the prompt below into Gemini / AI Studio")
        print(f"(aspect {args.aspect}, 2K), save the image, then run:")
        print(f"  python gen_img.py --postprocess RAW.png --out {args.out}")
        print("=" * 60)
        print(prompt)
        sys.exit(0)

    raw = args.out + '.raw.png'
    if not generate(key, prompt, args.src, args.aspect, raw):
        print("ALL MODELS FAILED"); sys.exit(1)
    postprocess(raw, args.out, args.bottom_crop)
    os.remove(raw)
