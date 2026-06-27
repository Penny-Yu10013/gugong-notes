# -*- coding: utf-8 -*-
# 從 data/cards.json + img/ + thumb/ 產生「網站部署用」的優化資產到 web/public/
# 只挑卡片實際用到的圖；img 壓到 1000px，thumb 用 400px。資料更新後重跑此檔。
import os, json, shutil
from PIL import Image
ROOT = r"C:\Users\yu2_7\Downloads\故宮0625"
P = json.load(open(os.path.join(ROOT, "data", "cards.json"), encoding="utf-8"))

refs = set()
for c in P["cards"]:
    refs.update(c["images"])
for w in P["walls"]:
    refs.add(w["img"])

pub = os.path.join(ROOT, "web", "public")
oimg, othumb, odata = (os.path.join(pub, d) for d in ("img", "thumb", "data"))
for d in (oimg, othumb, odata):
    os.makedirs(d, exist_ok=True)

src, tsrc = os.path.join(ROOT, "img"), os.path.join(ROOT, "thumb")
mi = mt = 0
for f in refs:
    sp = os.path.join(src, f + ".jpg")
    if os.path.exists(sp):
        im = Image.open(sp); w, h = im.size; s = 1000 / max(w, h)
        if s < 1:
            im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
        im.save(os.path.join(oimg, f + ".jpg"), "JPEG", quality=72); mi += 1
    tp = os.path.join(tsrc, f + ".jpg")
    if os.path.exists(tp):
        shutil.copy(tp, os.path.join(othumb, f + ".jpg")); mt += 1
shutil.copy(os.path.join(ROOT, "data", "cards.json"), os.path.join(odata, "cards.json"))
print(f"web/public/img: {mi}, web/public/thumb: {mt}, cards.json copied")
