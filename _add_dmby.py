# -*- coding: utf-8 -*-
import os, sys, json
from PIL import Image, ImageOps
import pillow_heif
pillow_heif.register_heif_opener()
sys.path.insert(0, r"C:\Users\yu2_7\Downloads\故宮0625")
from _enhance import enhance   # reuse adaptive enhancer

ROOT = r"C:\Users\yu2_7\Downloads\故宮0625"
SRC  = os.path.join(ROOT, "原始素材", "2025大美不言")
JPG  = os.path.join(ROOT, "jpg")
IMG  = os.path.join(ROOT, "img")
os.makedirs(JPG, exist_ok=True); os.makedirs(IMG, exist_ok=True)

names = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".heic"))
bases = []
done = 0
for f in names:
    base = os.path.splitext(f)[0]; bases.append(base)
    jdst = os.path.join(JPG, base + ".jpg")
    idst = os.path.join(IMG, base + ".jpg")
    try:
        im = Image.open(os.path.join(SRC, f))
        im = ImageOps.exif_transpose(im).convert("RGB")
        w, h = im.size; s = 1600 / max(w, h)
        if s < 1: im = im.resize((int(w*s), int(h*s)), Image.LANCZOS)
        im.save(jdst, "JPEG", quality=80)
        en, _, _ = enhance(Image.open(jdst))
        en.save(idst, "JPEG", quality=85)
        done += 1
    except Exception as e:
        print("ERR", f, e)
print("converted+enhanced:", done)

# batch files (namespaced) + membership list
B = 28
os.makedirs(os.path.join(ROOT, "batches"), exist_ok=True)
batches = [bases[i:i+B] for i in range(0, len(bases), B)]
for i, b in enumerate(batches):
    json.dump(b, open(os.path.join(ROOT, "batches", f"dmby_{i:02d}.json"), "w"), ensure_ascii=False)
os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
json.dump(bases, open(os.path.join(ROOT, "data", "dmby_files.json"), "w"), ensure_ascii=False)
print("batches:", len(batches), "files:", len(bases))
