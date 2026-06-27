# -*- coding: utf-8 -*-
import sys, os
from PIL import Image, ImageOps, ImageEnhance, ImageStat
ROOT = r"C:\Users\yu2_7\Downloads\故宮0625"
SRC = os.path.join(ROOT, "jpg")
OUT = os.path.join(ROOT, "img")

def enhance(im):
    im = im.convert("RGB")
    # mean luminance
    g = im.convert("L")
    mean = ImageStat.Stat(g).mean[0]
    # 1) gentle tonal stretch (clip extremes), preserve color via luminance-aware autocontrast
    im = ImageOps.autocontrast(im, cutoff=(0.5, 0.15))
    # 2) adaptive midtone lift for dark museum shots (gamma < 1 brightens midtones)
    if mean < 70:      gamma = 0.72
    elif mean < 100:   gamma = 0.82
    elif mean < 130:   gamma = 0.92
    else:              gamma = 1.0
    if gamma < 1.0:
        lut = [min(255, int((i/255.0)**gamma * 255 + 0.5)) for i in range(256)] * 3
        im = im.point(lut)
    # 3) gentle finish: a touch of saturation, contrast, sharpness
    im = ImageEnhance.Color(im).enhance(1.12)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = ImageEnhance.Sharpness(im).enhance(1.18)
    return im, mean, gamma

if __name__ == "__main__":
    args = sys.argv[1:]
    sample = False
    if args and args[0] == "--sample":
        sample = True; args = args[1:]
    outdir = os.path.join(ROOT, "img_test") if sample else OUT
    os.makedirs(outdir, exist_ok=True)
    names = [a + ".jpg" for a in args] if args else os.listdir(SRC)
    done = 0
    for f in names:
        if not f.lower().endswith(".jpg"): continue
        try:
            im = Image.open(os.path.join(SRC, f))
            out, mean, gamma = enhance(im)
            out.save(os.path.join(outdir, f), "JPEG", quality=85)
            done += 1
            if sample: print(f"{f}  mean={mean:.0f} gamma={gamma}")
        except Exception as e:
            print("ERR", f, e)
    print("enhanced:", done, "-> ", outdir)
