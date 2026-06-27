# -*- coding: utf-8 -*-
import json, glob, os, re, html
ROOT = r"C:\Users\yu2_7\Downloads\故宮0625"

# ---------- load ----------
recs = []
for f in sorted(glob.glob(os.path.join(ROOT, "ocr_json", "batch_*.json"))):
    recs += json.load(open(f, encoding="utf-8"))

def num_of(fn):
    m = re.search(r"(\d{3,5})", fn)
    return int(m.group(1)) if m else 99999

for r in recs:
    r["file"] = os.path.splitext(str(r.get("file", "")))[0]
    r["num"] = num_of(r["file"])
    for k in ("type","gallery_guess","artifact_name_zh","artifact_name_en",
              "dynasty","material","museum_id","ocr_text","caption","notes"):
        r[k] = (r.get(k) or "").strip()
recs.sort(key=lambda r: r["num"])

# ---------- canonical exhibition ----------
def canon(g):
    g = g or ""
    def has(*ks): return any(k in g for k in ks)
    if has("大美不言","梵克雅寶","Van Cleef","VCA"): return "大美不言｜梵克雅寶珠寶特展（2025）"
    if has("龍藏"): return "龍藏經｜藏傳佛教泥金寫經"
    if has("神獸","西洋想像","民俗","民間信仰","媽祖","北管","唐卡","佛教","造像","織品"):
        return "神獸現形與民俗信仰"
    if has("寶石","玲瓏","珠寶","珠瑮"): return "玲瓏璀璨｜寶石與珠寶特展"
    if has("硯"): return "硯特展｜與硯為友"
    if has("兵器","青銅","銅器","銅","秦漢","車馬","弩","戈","劍","矛","鉞","印章","嘉量"):
        return "青銅兵器與秦漢銅器｜祀與戎"
    if has("瓷","陶瓷","釉","彩","窯","轉心瓶","甜白","孔雀綠","鬥彩","青花","粉彩","琺瑯"):
        return "院藏歷代陶瓷｜博泥幻化"
    if has("玉"): return "玉器（常設與特展）"
    if has("書畫","郎世寧"): return "書畫"
    return "其他展區"

EX_ORDER = [
    "龍藏經｜藏傳佛教泥金寫經",
    "大美不言｜梵克雅寶珠寶特展（2025）",
    "神獸現形與民俗信仰",
    "玉器（常設與特展）",
    "青銅兵器與秦漢銅器｜祀與戎",
    "院藏歷代陶瓷｜博泥幻化",
    "硯特展｜與硯為友",
    "玲瓏璀璨｜寶石與珠寶特展",
    "書畫",
    "其他展區",
]

DMBY_EX = "大美不言｜梵克雅寶珠寶特展（2025）"
try:
    dmby_set = set(json.load(open(os.path.join(ROOT, "data", "dmby_files.json"), encoding="utf-8")))
except Exception:
    dmby_set = set()
for r in recs:
    r["ex"] = canon(r["gallery_guess"])
    if r["file"] in dmby_set:
        r["ex"] = DMBY_EX
    r["section"] = re.sub(r"\s+", " ", r["gallery_guess"]).strip() or "未分區"

# video frames: route by numeric proximity to nearest PHOTO (more reliable than agent's gallery text)
import bisect
photo_ex = sorted((r["num"], r["ex"]) for r in recs if r.get("src") != "video")
_pnums = [p[0] for p in photo_ex]
for v in recs:
    if v.get("src") == "video" and photo_ex:
        i = bisect.bisect_left(_pnums, v["num"])
        cands = []
        if i < len(photo_ex): cands.append(photo_ex[i])
        if i > 0: cands.append(photo_ex[i-1])
        v["ex"] = min(cands, key=lambda p: abs(p[0]-v["num"]))[1]
        v["section"] = "影片截圖 · " + v["section"]

def clean(t):
    return re.sub(r"\s+", " ", t or "").strip()

# ---------- pairing ----------
vids  = [r for r in recs if r.get("src") == "video"]
precs = [r for r in recs if r.get("src") != "video"]
anchors = [r for r in precs if r["type"] in ("artifact","mixed")]
labels  = [r for r in precs if r["type"] == "label"]
walls   = [r for r in precs if r["type"] == "wall"]
princ   = [r for r in precs if r["type"] == "principle"]
fails   = [r for r in precs if r["type"] == "fail"]
others  = [r for r in precs if r["type"] == "other"]

for a in anchors:
    a["_label"] = None
    a["_extra_imgs"] = []

# attach each label to nearest artifact anchor (no-text) within window & same exhibition
used_label = set()
for lab in labels:
    best, bestd = None, 99
    for a in anchors:
        if a["type"] != "artifact": continue
        if a["_label"] is not None: continue
        if a["ex"] != lab["ex"]: continue
        d = abs(a["num"] - lab["num"])
        if d < bestd and d <= 3:
            best, bestd = a, d
    if best is not None:
        best["_label"] = lab
        best["_extra_imgs"].append(lab["file"])
        used_label.add(lab["file"])

unmatched_labels = [l for l in labels if l["file"] not in used_label]

# ---------- build cards ----------
cards = []
def name_from(r, lab=None):
    src = lab or r
    nz = src["artifact_name_zh"]; ne = src["artifact_name_en"]
    return nz, ne

for a in anchors:
    lab = a.get("_label")
    nz, ne = name_from(a, lab)
    dynasty = (lab or a)["dynasty"] or a["dynasty"]
    material = (lab or a)["material"] or a["material"]
    mid = (lab or a)["museum_id"] or a["museum_id"]
    desc = clean((lab["ocr_text"] if lab else "") or a["ocr_text"])
    # for mixed remove pure-name noise: keep ocr as desc anyway
    title = nz or a["caption"] or ne or a["file"]
    if nz:
        status = "complete"; marker = ""
    else:
        status = "pending_label"; marker = "partial"  # 名稱未確認
    imgs = [a["file"]] + a["_extra_imgs"]
    cards.append({
        "id": a["file"], "title": title, "name_zh": nz, "name_en": ne,
        "dynasty": dynasty, "material": material, "museum_id": mid,
        "desc": desc, "caption": a["caption"], "notes": clean(a["notes"]),
        "images": imgs, "ex": a["ex"], "section": a["section"],
        "type": a["type"], "status": status, "marker": marker,
        "num": a["num"],
    })

# label-only cards (no artifact photo matched)
for lab in unmatched_labels:
    cards.append({
        "id": lab["file"], "title": lab["artifact_name_zh"] or lab["caption"] or lab["file"],
        "name_zh": lab["artifact_name_zh"], "name_en": lab["artifact_name_en"],
        "dynasty": lab["dynasty"], "material": lab["material"], "museum_id": lab["museum_id"],
        "desc": clean(lab["ocr_text"]), "caption": lab["caption"],
        "notes": clean(lab["notes"]) + "（僅有告示牌，展品照可能未拍或在影片中）",
        "images": [lab["file"]], "ex": lab["ex"], "section": lab["section"],
        "type": "label_only", "status": "partial", "marker": "partial", "num": lab["num"],
    })

# principle cards
for p in princ:
    cards.append({
        "id": p["file"], "title": p["artifact_name_zh"] or p["caption"] or "視覺原理/圖解",
        "name_zh": p["artifact_name_zh"], "name_en": p["artifact_name_en"],
        "dynasty": "", "material": "", "museum_id": "",
        "desc": clean(p["ocr_text"]), "caption": p["caption"], "notes": clean(p["notes"]),
        "images": [p["file"]], "ex": p["ex"], "section": p["section"],
        "type": "principle", "status": "complete", "marker": "", "num": p["num"],
    })

# video-derived cards (standalone, no pairing)
TYPEMAP = {"label":"label_only","artifact":"artifact","mixed":"mixed",
           "wall":"wall","principle":"principle"}
for v in vids:
    if v["type"] == "other":
        others.append(v); continue
    nz = v["artifact_name_zh"]
    named = bool(nz) or v["type"] in ("wall","principle")
    cards.append({
        "id": v["file"], "title": nz or v["caption"] or v["artifact_name_en"] or v["file"],
        "name_zh": nz, "name_en": v["artifact_name_en"],
        "dynasty": v["dynasty"], "material": v["material"], "museum_id": v["museum_id"],
        "desc": clean(v["ocr_text"]), "caption": v["caption"], "notes": clean(v["notes"]),
        "images": [v["file"]], "ex": v["ex"], "section": v["section"],
        "type": TYPEMAP.get(v["type"], "artifact"),
        "status": "complete" if named else "pending_label",
        "marker": "" if named else "partial", "num": v["num"], "video": True,
    })

for c in cards:
    c.setdefault("video", False)
cards.sort(key=lambda c: c["num"])

# ---------- dedup: merge same-item multi-angle cards ----------
# signals: identical name OR identical museum_id, WITHIN same exhibition AND numerically close.
GAP = 6
def norm_name(s): return re.sub(r"\s+", "", (s or "")).strip()
def norm_id(s):
    m = re.match(r"((?:故|購|贈|中|順|寄)[玉瓷銅雜鑲文庫])0*(\d+)", (s or "").strip())
    return m.group(1) + m.group(2) if m else None

parent = {}
def find(x):
    parent.setdefault(x, x)
    r = x
    while parent[r] != r: r = parent[r]
    while parent[x] != r: parent[x], x = r, parent[x]
    return r
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[rb] = ra

for c in cards: find(c["id"])
from collections import defaultdict as _dd
buckets = _dd(list)
for c in cards:
    nn = norm_name(c["name_zh"])
    if nn: buckets[("n", c["ex"], nn)].append(c)
    ni = norm_id(c["museum_id"])
    if ni: buckets[("i", c["ex"], ni)].append(c)
for key, grp in buckets.items():
    grp.sort(key=lambda c: c["num"])
    for a, b in zip(grp, grp[1:]):
        if b["num"] - a["num"] <= GAP:   # proximity guard: only merge nearby same-name/id
            union(a["id"], b["id"])

clusters = _dd(list)
for c in cards: clusters[find(c["id"])].append(c)
merged = []
for root, grp in clusters.items():
    grp.sort(key=lambda c: c["num"])
    if len(grp) == 1:
        grp[0]["merged_from"] = [grp[0]["id"]]; merged.append(grp[0]); continue
    base = dict(grp[0])
    imgs = []
    for c in grp:
        for im in c["images"]:
            if im not in imgs: imgs.append(im)
    def pick(f):
        for c in grp:
            if (c.get(f) or "").strip(): return c[f]
        return ""
    base["images"] = imgs
    base["name_zh"], base["name_en"] = pick("name_zh"), pick("name_en")
    base["dynasty"], base["material"], base["museum_id"] = pick("dynasty"), pick("material"), pick("museum_id")
    base["caption"] = pick("caption")
    base["title"] = base["name_zh"] or base["caption"] or base["title"]
    base["desc"] = max((c["desc"] for c in grp), key=len)
    base["notes"] = " / ".join(dict.fromkeys(c["notes"] for c in grp if c.get("notes")))
    base["status"] = "complete" if base["name_zh"] else grp[0]["status"]
    base["marker"] = "" if base["name_zh"] else grp[0]["marker"]
    base["video"] = all(c.get("video") for c in grp)
    base["num"] = grp[0]["num"]
    base["merged_from"] = [c["id"] for c in grp]
    merged.append(base)
n_before = len(cards); cards = merged
cards.sort(key=lambda c: c["num"])
for i, c in enumerate(cards, 1):
    c["uid"] = f"c{i:04d}"
    c["image_count"] = len(c["images"])
print(f"dedup: {n_before} -> {len(cards)} cards (merged {n_before-len(cards)})")

# ---------- manual overrides (id 修正 + 精選清單) ----------
try:
    ov = json.load(open(os.path.join(ROOT, "data", "overrides.json"), encoding="utf-8"))
except Exception:
    ov = {}
id_fixes = ov.get("id_fixes", {})
hl_set = set(ov.get("highlights", []))
n_fix = n_hl = 0
for c in cards:
    c["highlight"] = False
    srcs = set(c.get("merged_from", [])) | {c["id"]}
    for img, mid in id_fixes.items():
        if img in srcs:
            c["museum_id"] = mid; n_fix += 1
    if srcs & hl_set:
        c["highlight"] = True; n_hl += 1
print(f"overrides: id-fixes {n_fix}, highlights {n_hl}")

# ---------- section overviews from walls ----------
sections = {}  # ex -> list of {section, text, img}
for w in walls:
    sections.setdefault(w["ex"], []).append({
        "section": w["section"], "text": clean(w["ocr_text"]),
        "img": w["file"], "num": w["num"],
        "title": w["artifact_name_zh"] or w["caption"],
    })

# ---------- stats ----------
from collections import Counter, defaultdict
ex_counts = Counter(c["ex"] for c in cards)

# ---------- write data.json (schema v2) ----------
os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
exhibitions = [{"key": ex, "title": ex, "short": ex.split("｜")[0],
                "count": sum(1 for c in cards if c["ex"] == ex)}
               for ex in EX_ORDER if any(c["ex"] == ex for c in cards)]
payload = {
    "schema_version": 2,
    "generated": "2026-06-28",
    "meta": {
        "source": "故宮速記 OCR pipeline",
        "image_dir": "img",
        "total_cards": len(cards),
        "video_cards": sum(1 for c in cards if c.get("video")),
        "exhibitions": len(exhibitions),
        "status_enum": ["complete", "pending_label", "partial"],
        "type_enum": ["artifact", "mixed", "label_only", "principle", "wall"],
    },
    "exhibitions": exhibitions,
    "cards": cards,
    "sections": sections,
    "walls": [{"ex":w["ex"],"section":w["section"],"text":clean(w["ocr_text"]),"img":w["file"],"num":w["num"]} for w in walls],
    "ex_order": EX_ORDER,
    "fails": [f["file"] for f in fails],
    "others": [{"file":o["file"],"caption":o["caption"]} for o in others],
}
json.dump(payload, open(os.path.join(ROOT,"data","cards.json"),"w",encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("cards:", len(cards), " video-cards:", sum(1 for c in cards if c.get("video")))
print("  artifact/mixed cards:", sum(1 for c in cards if c["type"] in ("artifact","mixed")))
print("  complete:", sum(1 for c in cards if c["status"]=="complete"))
print("  pending_label:", sum(1 for c in cards if c["status"]=="pending_label"))
print("  label_only:", sum(1 for c in cards if c["type"]=="label_only"))
print("  principle:", sum(1 for c in cards if c["type"]=="principle"))
print("walls:", len(walls), "fails:", len(fails), "others:", len(others))
print("unmatched labels:", len(unmatched_labels))
for ex in EX_ORDER:
    print(f"  {ex_counts.get(ex,0):3d}  {ex}")
