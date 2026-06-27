# -*- coding: utf-8 -*-
import json, os, re, html
ROOT = r"C:\Users\yu2_7\Downloads\故宮0625"
P = json.load(open(os.path.join(ROOT,"data","cards.json"), encoding="utf-8"))
cards = P["cards"]; EX = P["ex_order"]; walls = P["walls"]
others = P["others"]; fails = P["fails"]

# ---------------- MD files ----------------
md_dir = os.path.join(ROOT, "展品")
os.makedirs(md_dir, exist_ok=True)
def yaml_esc(s): return (s or "").replace('"','\\"')
def card_md(c):
    fm = ["---","type: 展品",
        f'exhibition: "{yaml_esc(c["ex"])}"', f'section: "{yaml_esc(c["section"])}"',
        f'artifact_name: "{yaml_esc(c["name_zh"])}"', f'name_en: "{yaml_esc(c["name_en"])}"',
        f'dynasty: "{yaml_esc(c["dynasty"])}"', f'material: "{yaml_esc(c["material"])}"',
        f'museum_id: "{yaml_esc(c["museum_id"])}"', f'status: {c["status"]}',
        f'source_imgs: {json.dumps(c["images"], ensure_ascii=False)}', "---","",
        f'# {c["title"]}', ""]
    for im in c["images"]: fm.append(f'![{im}](img/{im}.jpg)')
    fm.append("")
    if c["dynasty"] or c["material"] or c["museum_id"]:
        fm.append("## 基本資訊")
        if c["dynasty"]:  fm.append(f'- **年代**：{c["dynasty"]}')
        if c["material"]: fm.append(f'- **材質**：{c["material"]}')
        if c["museum_id"]:fm.append(f'- **館藏編號**：{c["museum_id"]}')
        fm.append("")
    if c["desc"]: fm.append("## 展品描述"); fm.append(c["desc"]); fm.append("")
    if c["notes"]: fm.append("## 備註"); fm.append(c["notes"]); fm.append("")
    return "\n".join(fm)
by_ex = {}
for c in cards: by_ex.setdefault(c["ex"], []).append(c)
for i, ex in enumerate(EX):
    cs = by_ex.get(ex, [])
    if not cs: continue
    safe = re.sub(r'[\\/:*?"<>|｜]', "_", ex)
    parts = [f"# {ex}", "", f"共 {len(cs)} 張卡片。", ""]
    secw = [w for w in walls if w["ex"]==ex]
    if secw:
        parts.append("## 展區說明（牆面 OCR）")
        for w in secw:
            parts.append(f'### {w["section"]}')
            parts.append(f'![{w["img"]}](img/{w["img"]}.jpg)')
            if w["text"]: parts.append(w["text"])
            parts.append("")
    parts.append("## 展品")
    for c in cs: parts.append(""); parts.append(card_md(c))
    open(os.path.join(md_dir, f"{i:02d}_{safe}.md"),"w",encoding="utf-8").write("\n".join(parts))
ov = ["---","type: 展區總覽","origin: 故宮 2026-06-25","---","","# 故宮速記 · 展區總覽",""]
for ex in EX:
    cs = by_ex.get(ex, [])
    if not cs: continue
    comp = sum(1 for c in cs if c["status"]=="complete" and c["type"]!="principle")
    pend = sum(1 for c in cs if c["status"]=="pending_label")
    lab  = sum(1 for c in cs if c["type"]=="label_only")
    pr   = sum(1 for c in cs if c["type"]=="principle")
    ov.append(f"## {ex}")
    ov.append(f"- 展品卡片：{comp+pend} 張（名稱已確認 {comp}、🟡名稱待確認 {pend}）")
    if lab: ov.append(f"- 🟡 僅告示牌：{lab} 張")
    if pr:  ov.append(f"- 📐 視覺原理/圖解：{pr} 張")
    ov.append("")
open(os.path.join(ROOT,"展區總覽.md"),"w",encoding="utf-8").write("\n".join(ov))
um = ["# 未配對 / 待人工處理","","以下項目自動配對信心較低，請手動檢查（對照 img/ 原圖）。","",
      "## 🟡 名稱待確認的展品照（找不到鄰近告示牌）",""]
for c in cards:
    if c["status"]=="pending_label":
        um.append(f'- `{c["id"]}`（{c["ex"]}／{c["section"]}）— 推測：{c["caption"] or "?"}')
um.append(""); um.append("## 🟡 僅有告示牌、缺展品照（可能在影片中）"); um.append("")
for c in cards:
    if c["type"]=="label_only":
        um.append(f'- `{c["id"]}` {c["name_zh"]}（{c["ex"]}）')
open(os.path.join(ROOT,"_unmatched.md"),"w",encoding="utf-8").write("\n".join(um))
ex_md = ["# 排除項（全景／人／空櫃／問卷等）",""]
for o in others: ex_md.append(f'- `{o["file"]}` {o["caption"]}')
if fails: ex_md.append(""); ex_md.append("## ❌ OCR 失敗"); ex_md += [f'- `{f}`' for f in fails]
open(os.path.join(ROOT,"_excluded.md"),"w",encoding="utf-8").write("\n".join(ex_md))

# ---------------- HTML ----------------
data_js = json.dumps(P, ensure_ascii=False).replace("</", "<\\/")
total_artifacts = sum(1 for c in cards if c["type"] in ("artifact","mixed","label_only"))
total_principle = sum(1 for c in cards if c["type"]=="principle")

HTML = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>故宮速記 · 2026-06-25</title>
<style>
:root{
  --wall:#e9e3d6;        /* 展廳米牆 */
  --wall2:#efe9dd;
  --rail:#e4ddcd;        /* 側欄(更靜) */
  --card:#fffdf8;        /* 卡片白 */
  --ink:#2c2823;         /* 主文字 暖黑 */
  --ink2:#7a7060;        /* 次文字 */
  --ink3:#a59a85;        /* 更淡 */
  --line:#d9d0bd;
  --accent:#9c3326;      /* 故宮硃紅 */
  --accent-soft:#b5503f;
  --jade:#4f7a5b;        /* 材質 */
  --gold:#9a7b3f;        /* 朝代 */
  --shadow:0 1px 2px rgba(60,45,25,.06), 0 1px 3px rgba(60,45,25,.05);
  --shadow-lg:0 10px 30px rgba(60,45,25,.18), 0 4px 10px rgba(60,45,25,.10);
}
*{box-sizing:border-box}
html,body{background:var(--wall)}
body{margin:0;color:var(--ink);
  font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;
  font-size:15px;line-height:1.65;-webkit-font-smoothing:antialiased}
.serif{font-family:"Noto Serif TC","Songti TC","PMingLiU",Georgia,serif}
a{color:var(--accent)}
header{padding:20px 30px 16px;background:var(--wall);
  border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
header::after{content:"";position:absolute;left:0;bottom:-1px;width:120px;height:2px;background:var(--accent)}
header h1{margin:0;font-size:22px;letter-spacing:3px;font-weight:600;font-family:"Noto Serif TC","Songti TC",Georgia,serif}
header h1 .g{color:var(--accent)}
header h1 .d{color:var(--ink3);font-weight:400;font-size:15px;letter-spacing:1px}
header .sub{color:var(--ink2);font-size:12.5px;margin-top:5px;letter-spacing:.3px}
.wrap{display:flex;align-items:flex-start}
/* ---- 靜默側欄 ---- */
nav{width:230px;flex:0 0 230px;background:var(--rail);
  padding:18px 12px;position:sticky;top:75px;height:calc(100vh - 75px);overflow:auto}
nav .lbl{font-size:11px;letter-spacing:2px;color:var(--ink3);padding:0 10px 8px;text-transform:uppercase}
nav .navitem{padding:8px 12px 8px 13px;border-radius:7px;cursor:pointer;color:var(--ink2);
  display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:14px;
  border-left:2px solid transparent;transition:background .12s,color .12s}
nav .navitem:hover{background:rgba(255,255,255,.55);color:var(--ink)}
nav .navitem.active{background:var(--card);color:var(--ink);font-weight:600;
  border-left:2px solid var(--accent);box-shadow:var(--shadow)}
nav .navitem .c{font-size:11.5px;color:var(--ink3);background:rgba(0,0,0,.04);border-radius:10px;padding:1px 8px;font-weight:400}
nav .navitem.active .c{color:var(--accent)}
/* ---- 主舞台 ---- */
main{flex:1;padding:22px 30px 60px;min-width:0;background:var(--wall)}
.toolbar{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:22px;align-items:center}
.toolbar input,.toolbar select{background:var(--card);border:1px solid var(--line);
  color:var(--ink);border-radius:8px;padding:9px 12px;font-size:14px;outline:none;box-shadow:var(--shadow)}
.toolbar select{cursor:pointer}
.toolbar input:focus,.toolbar select:focus{border-color:var(--accent)}
.toolbar input[type=search]{flex:1;min-width:220px}
.btn{background:transparent;border:1px solid var(--line);color:var(--ink2);
  border-radius:8px;padding:9px 14px;cursor:pointer;font-size:13px}
.btn:hover{color:var(--accent);border-color:var(--accent)}
.exhead{margin:4px 0 20px;display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
.exhead h2{font-size:25px;margin:0;color:var(--ink);font-weight:600;
  font-family:"Noto Serif TC","Songti TC",Georgia,serif;letter-spacing:1px}
.exhead .meta{color:var(--ink2);font-size:13px}
.exhead .meta b{color:var(--accent);font-weight:600}
details.walls{background:var(--card);border:1px solid var(--line);border-radius:11px;
  margin-bottom:22px;padding:4px 16px;box-shadow:var(--shadow)}
details.walls summary{cursor:pointer;color:var(--accent);font-size:13.5px;padding:9px 0;font-weight:600;letter-spacing:.5px}
details.walls .w{border-top:1px solid var(--line);padding:12px 0;display:flex;gap:15px}
details.walls .w img{width:130px;height:96px;object-fit:cover;border-radius:7px;cursor:pointer;flex:0 0 130px}
details.walls .w .t{flex:1;font-size:13px;color:var(--ink2)}
details.walls .w .t b{color:var(--ink);font-size:14px}
/* ---- 作品卡 ---- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(228px,1fr));gap:22px}
.card{background:var(--card);border-radius:12px;overflow:hidden;cursor:pointer;
  box-shadow:var(--shadow);transition:transform .16s ease,box-shadow .16s ease;
  display:flex;flex-direction:column;border:1px solid rgba(217,208,189,.6)}
.card:hover{transform:translateY(-4px);box-shadow:var(--shadow-lg)}
.card .imgwrap{aspect-ratio:4/5;background:#15120e;position:relative;overflow:hidden}
.card .imgwrap img{width:100%;height:100%;object-fit:cover;display:block;
  transition:transform .35s ease}
.card:hover .imgwrap img{transform:scale(1.04)}
.card .badge{position:absolute;top:9px;left:9px;font-size:11px;padding:2px 9px;border-radius:20px;
  background:rgba(20,15,10,.66);backdrop-filter:blur(5px);color:#f3ead7;letter-spacing:.3px}
.b-partial,.b-pend{color:#f0c869} .b-pr{color:#9fd6bd}
.card .fav{position:absolute;top:7px;right:9px;color:#f0c24a;font-size:17px;
  text-shadow:0 1px 4px rgba(0,0,0,.7);z-index:2}
.card.is-fav{box-shadow:0 0 0 2px var(--gold), var(--shadow)}
.card.is-fav:hover{box-shadow:0 0 0 2px var(--gold), var(--shadow-lg)}
nav .navitem.fav-nav{color:var(--gold)}
nav .navitem.fav-nav.active{color:#8a6a25}
.card .body{padding:12px 14px 15px;flex:1;display:flex;flex-direction:column;gap:6px}
.card .title{font-size:14.5px;font-weight:600;line-height:1.45;color:var(--ink);
  font-family:"Noto Serif TC","Songti TC",Georgia,serif}
.card .chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:1px}
.chip{font-size:11px;color:var(--ink2);background:rgba(0,0,0,.035);border:1px solid var(--line);
  border-radius:6px;padding:1px 8px}
.chip.dyn{color:var(--gold);border-color:rgba(154,123,63,.3);background:rgba(154,123,63,.07)}
.chip.mat{color:var(--jade);border-color:rgba(79,122,91,.3);background:rgba(79,122,91,.07)}
.card .mid{font-size:11px;color:var(--ink3);margin-top:auto;letter-spacing:.3px}
.empty{color:var(--ink2);padding:50px;text-align:center}
/* ---- 詳情 ---- */
.modal{position:fixed;inset:0;background:rgba(30,22,14,.82);z-index:50;display:none;
  padding:34px;overflow:auto;backdrop-filter:blur(3px)}
.modal.open{display:block}
.mbox{max-width:1020px;margin:0 auto;background:var(--card);border-radius:14px;
  overflow:hidden;box-shadow:var(--shadow-lg)}
.mbox .imgs{display:flex;gap:2px;flex-wrap:wrap;background:#15120e}
.mbox .imgs img{max-height:72vh;max-width:100%;object-fit:contain;flex:1;min-width:300px;cursor:zoom-in}
.mbox .info{padding:22px 28px 26px}
.mbox .info h3{margin:0 0 3px;font-size:24px;color:var(--ink);font-weight:600;
  font-family:"Noto Serif TC","Songti TC",Georgia,serif;letter-spacing:.5px}
.mbox .info .en{color:var(--ink2);font-size:14px;margin-bottom:12px;font-style:italic}
.mbox .info .row{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.mbox .info .sec{margin-top:16px}
.mbox .info .sec h4{margin:0 0 5px;font-size:12px;color:var(--accent);letter-spacing:2px;font-weight:600}
.mbox .info .desc{color:#4a4338;font-size:14px;white-space:pre-wrap;line-height:1.75}
.mbox .info .notes{color:var(--accent-soft);font-size:13px;line-height:1.7}
.mclose{position:fixed;top:20px;right:28px;font-size:26px;color:#fff;cursor:pointer;z-index:60;
  background:rgba(0,0,0,.4);width:46px;height:46px;border-radius:50%;display:flex;
  align-items:center;justify-content:center;line-height:1}
.sec.links{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.dlink{font-size:13px;text-decoration:none;color:var(--accent);border:1px solid var(--line);
  border-radius:8px;padding:7px 14px;background:rgba(156,51,38,.05);transition:.12s}
.dlink:hover{background:var(--accent);color:#fff;border-color:var(--accent)}
.fns{font-size:12px;color:var(--ink3);margin-top:14px;border-top:1px solid var(--line);padding-top:10px}
@media(max-width:760px){nav{display:none}main{padding:16px}}
</style>
</head>
<body>
<header>
  <h1><span class="g">故宮</span> 速記導覽 <span class="d">· 2026.06.25</span></h1>
  <div class="sub">__SUB__</div>
</header>
<div class="wrap">
  <nav id="nav"></nav>
  <main>
    <div class="toolbar">
      <input type="search" id="q" placeholder="搜尋名稱 / 描述 / 編號…">
      <select id="fType"><option value="">類型：全部</option>
        <option value="artifact">展品照</option>
        <option value="label_only">僅告示牌</option>
        <option value="principle">視覺原理</option></select>
      <select id="fDyn"><option value="">朝代：全部</option></select>
      <select id="fMat"><option value="">材質：全部</option></select>
      <select id="fStat"><option value="">狀態：全部</option>
        <option value="complete">已確認</option>
        <option value="pending_label">名稱待確認</option>
        <option value="partial">部分</option></select>
      <button class="btn" id="reset">重設</button>
    </div>
    <div id="content"></div>
  </main>
</div>
<div class="modal" id="modal"><div class="mclose" onclick="closeModal()">×</div><div class="mbox" id="mbox"></div></div>
<script>
const DATA = __DATA__;
const IMG = f => "img/"+f+".jpg";
const cards = DATA.cards, EX = DATA.ex_order, walls = DATA.walls;
let curEx = EX.find(e=>cards.some(c=>c.ex===e));
const state={q:"",type:"",dyn:"",mat:"",stat:""};
function uniq(a){return [...new Set(a.filter(Boolean))].sort()}
const fDyn=document.getElementById('fDyn'),fMat=document.getElementById('fMat');
uniq(cards.map(c=>c.dynasty)).forEach(d=>fDyn.add(new Option(d,d)));
uniq(cards.map(c=>c.material)).forEach(m=>fMat.add(new Option(m,m)));
function exCount(e){return cards.filter(c=>c.ex===e).length}
const nav=document.getElementById('nav');
function renderNav(){
  nav.innerHTML='<div class="lbl">展區</div>';
  const all=document.createElement('div');
  all.className="navitem"+(curEx==="__ALL__"?" active":"");
  all.innerHTML='<span>全部展區</span><span class="c">'+cards.length+'</span>';
  all.onclick=()=>{curEx="__ALL__";render()};nav.appendChild(all);
  const nfav=cards.filter(c=>c.highlight).length;
  if(nfav){const fav=document.createElement('div');
    fav.className="navitem fav-nav"+(curEx==="__FAV__"?" active":"");
    fav.innerHTML='<span>★ 精選口袋名單</span><span class="c">'+nfav+'</span>';
    fav.onclick=()=>{curEx="__FAV__";render()};nav.appendChild(fav);}
  EX.forEach(e=>{const n=exCount(e);if(!n)return;
    const d=document.createElement('div');
    d.className="navitem"+(e===curEx?" active":"");
    d.innerHTML='<span>'+e.split('｜')[0]+'</span><span class="c">'+n+'</span>';
    d.onclick=()=>{curEx=e;render()};nav.appendChild(d);});
}
function matchFilter(c){
  if(state.type){if(state.type==="artifact"&&!(c.type==="artifact"||c.type==="mixed"))return false;
    if(state.type!=="artifact"&&c.type!==state.type)return false;}
  if(state.dyn&&c.dynasty!==state.dyn)return false;
  if(state.mat&&c.material!==state.mat)return false;
  if(state.stat){if(state.stat==="partial"){if(c.marker!=="partial")return false;}
    else if(c.status!==state.stat)return false;}
  if(state.q){const s=(c.title+" "+c.name_en+" "+c.desc+" "+c.museum_id+" "+c.section).toLowerCase();
    if(!s.includes(state.q.toLowerCase()))return false;}
  return true;
}
function badge(c){
  if(c.video)return '<span class="badge" style="color:#7fc8e0">影片</span>';
  if(c.type==="principle")return '<span class="badge b-pr">圖解</span>';
  if(c.type==="label_only")return '<span class="badge b-partial">僅告示牌</span>';
  if(c.status==="pending_label")return '<span class="badge b-pend">名稱待確認</span>';
  return "";
}
function esc(s){return (s||"").replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]))}
function cardHTML(c,i){
  const chips=[];
  if(c.dynasty)chips.push('<span class="chip dyn">'+esc(c.dynasty)+'</span>');
  if(c.material)chips.push('<span class="chip mat">'+esc(c.material)+'</span>');
  return '<div class="card'+(c.highlight?' is-fav':'')+'" onclick="openModal('+i+')">'+
    '<div class="imgwrap">'+badge(c)+(c.highlight?'<div class="fav">★</div>':'')+'<img loading="lazy" src="'+IMG(c.images[0])+'"></div>'+
    '<div class="body"><div class="title">'+esc(c.title)+'</div>'+
    '<div class="chips">'+chips.join('')+'</div>'+
    (c.museum_id?'<div class="mid">'+esc(c.museum_id)+'</div>':'')+
    '</div></div>';
}
let viewList=[];
function render(){
  renderNav();
  const content=document.getElementById('content');
  let list=cards.filter(matchFilter);
  if(curEx==="__FAV__")list=list.filter(c=>c.highlight);
  else if(curEx!=="__ALL__")list=list.filter(c=>c.ex===curEx);
  if(curEx!=="__FAV__")list=list.slice().sort((a,b)=>(b.highlight?1:0)-(a.highlight?1:0)); // 精選置頂
  viewList=list;
  const exName=curEx==="__FAV__"?"★ 精選口袋名單":(curEx==="__ALL__"?"全部展區":curEx);
  let h='<div class="exhead"><h2>'+esc(exName)+'</h2><div class="meta"><b>'+list.length+'</b> 張</div></div>';
  if(curEx!=="__ALL__"){
    const ws=walls.filter(w=>w.ex===curEx);
    if(ws.length){h+='<details class="walls"><summary>展區說明牆 · '+ws.length+'</summary>';
      ws.forEach(w=>{h+='<div class="w"><img loading="lazy" src="'+IMG(w.img)+'" onclick="lightbox(\''+w.img+'\')">'+
        '<div class="t"><b>'+esc(w.section)+'</b><br>'+esc(w.text).slice(0,600)+'</div></div>';});
      h+='</details>';}
  }
  if(!list.length)h+='<div class="empty">沒有符合條件的項目</div>';
  else h+='<div class="grid">'+list.map((c,i)=>cardHTML(c,i)).join('')+'</div>';
  content.innerHTML=h;window.scrollTo(0,0);
}
function openModal(i){
  const c=viewList[i];const b=document.getElementById('mbox');
  let h='<div class="imgs">'+c.images.map(im=>'<img src="'+IMG(im)+'" onclick="lightbox(\''+im+'\')">').join('')+'</div>';
  h+='<div class="info"><h3>'+(c.highlight?'<span style="color:#c79a2e">★ </span>':'')+esc(c.title)+'</h3>';
  if(c.name_en)h+='<div class="en">'+esc(c.name_en)+'</div>';
  h+='<div class="row">';
  if(c.dynasty)h+='<span class="chip dyn">'+esc(c.dynasty)+'</span>';
  if(c.material)h+='<span class="chip mat">'+esc(c.material)+'</span>';
  if(c.museum_id)h+='<span class="chip">'+esc(c.museum_id)+'</span>';
  h+='<span class="chip">'+esc(c.ex.split('｜')[0])+'</span></div>';
  if(c.desc)h+='<div class="sec"><h4>說明 · OCR</h4><div class="desc">'+esc(c.desc)+'</div></div>';
  if(c.notes)h+='<div class="sec"><h4>備註</h4><div class="notes">'+esc(c.notes)+'</div></div>';
  if(c.name_zh&&!c.video){
    const q=encodeURIComponent(c.name_zh+' '+(c.museum_id||'')+' 故宮');
    const npm='https://digitalarchive.npm.gov.tw/';
    h+='<div class="sec links">'+
       '<a class="dlink" target="_blank" rel="noopener" href="https://www.google.com/search?q='+q+'">🔎 深入查詢</a>'+
       '<a class="dlink" target="_blank" rel="noopener" href="'+npm+'">🏛️ 故宮典藏庫</a></div>';
  }
  h+='<div class="fns">展區：'+esc(c.section)+(c.image_count>1?'　·　'+c.image_count+' 圖':'')+'　·　來源：'+c.images.map(x=>x).join(', ')+'</div></div>';
  b.innerHTML=h;document.getElementById('modal').classList.add('open');
}
function closeModal(){document.getElementById('modal').classList.remove('open')}
function lightbox(im){window.open(IMG(im),'_blank')}
document.getElementById('modal').onclick=e=>{if(e.target.id==='modal')closeModal()};
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});
document.getElementById('q').oninput=e=>{state.q=e.target.value;render()};
document.getElementById('fType').onchange=e=>{state.type=e.target.value;render()};
fDyn.onchange=e=>{state.dyn=e.target.value;render()};
fMat.onchange=e=>{state.mat=e.target.value;render()};
document.getElementById('fStat').onchange=e=>{state.stat=e.target.value;render()};
document.getElementById('reset').onclick=()=>{state.q=state.type=state.dyn=state.mat=state.stat="";
  document.getElementById('q').value="";['fType','fDyn','fMat','fStat'].forEach(id=>document.getElementById(id).value="");render()};
render();
</script>
</body></html>"""

n_ex = sum(1 for ex in EX if any(c["ex"] == ex for c in cards))
n_vid = sum(1 for c in cards if c.get("video"))
sub = (f'共 {len(cards)} 張卡片 · 展品 {total_artifacts} · 視覺原理 {total_principle} · '
       f'{n_ex} 大展區 · 主展 龍藏經 · 暗櫃照片已自動補光 · 含 {n_vid} 則影片截圖補充')
HTML = HTML.replace("__SUB__", html.escape(sub)).replace("__DATA__", data_js)
open(os.path.join(ROOT,"index.html"),"w",encoding="utf-8").write(HTML)
print("index.html written:", len(HTML), "bytes")
