import sys, os
from PIL import Image, ImageOps
import pillow_heif
pillow_heif.register_heif_opener()

SRC = r"C:\Users\yu2_7\Downloads\故宮0625\原始素材"
OUT = r"C:\Users\yu2_7\Downloads\故宮0625\jpg"
os.makedirs(OUT, exist_ok=True)

MAXDIM = 1600
Q = 80

names = sys.argv[1:]  # optional subset
if not names:
    names = [f for f in os.listdir(SRC) if f.lower().endswith((".heic", ".jpg", ".png"))]

done = 0
for f in names:
    src = os.path.join(SRC, f)
    base = os.path.splitext(f)[0]
    dst = os.path.join(OUT, base + ".jpg")
    if os.path.exists(dst):
        done += 1
        continue
    try:
        im = Image.open(src)
        im = ImageOps.exif_transpose(im)
        im = im.convert("RGB")
        w, h = im.size
        s = MAXDIM / max(w, h)
        if s < 1:
            im = im.resize((int(w*s), int(h*s)), Image.LANCZOS)
        im.save(dst, "JPEG", quality=Q)
        done += 1
    except Exception as e:
        print("ERR", f, e)
print("converted/exists:", done, "of", len(names))
