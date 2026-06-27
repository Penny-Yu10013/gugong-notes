# cards.json schema v2

故宮速記的單一資料源。`index.html` 與未來的 React 版都應只讀這個檔。
圖片路徑 = `<meta.image_dir>/<image>.jpg`（目前 `img/`，已補光）。

## 頂層

| key | 說明 |
|---|---|
| `schema_version` | 目前 `2` |
| `generated` | 產生日期字串 |
| `meta` | 統計與 enum（見下） |
| `exhibitions` | `[{key,title,short,count}]`，已依展覽順序排好 |
| `cards` | 主資料，展品卡陣列 |
| `walls` | `[{ex,section,text,img,num}]` 展區說明牆（牆面 OCR 全文） |
| `sections` | `{ex: [展區說明...]}` 同上的分組版 |
| `ex_order` | 展區顯示順序 |
| `fails` | OCR 失敗檔名（目前 0） |
| `others` | 排除項（全景／人／空櫃／問卷／純剪輯素材） |

## card 物件

| 欄位 | 型別 | 說明 |
|---|---|---|
| `uid` | str | 穩定唯一鍵 `c0001`…（排序後指派，React 用這個當 key） |
| `id` | str | 代表圖檔名（不含副檔名） |
| `merged_from` | str[] | 去重前的原始卡 id（多角度合併來源） |
| `images` | str[] | 此卡所有圖檔名（多角度／展品＋名牌／影片幀） |
| `image_count` | int | `images` 長度 |
| `title` | str | 顯示標題（= name_zh 或 caption） |
| `name_zh` / `name_en` | str | 品名中／英（OCR 自牌面，可空） |
| `dynasty` | str | 年代／朝代 |
| `material` | str | 材質 |
| `museum_id` | str | 館藏／典藏編號（故宮統一編號或出借單位名） |
| `desc` | str | 說明 / OCR 全文 |
| `caption` | str | 一句話描述（無牌時的推測名來源） |
| `notes` | str | 備註（工藝亮點、存疑、聯想點） |
| `ex` | str | 所屬展區（= exhibitions[].key） |
| `section` | str | 子分區（細主題） |
| `type` | enum | `artifact`/`mixed`/`label_only`/`principle`/`wall` |
| `status` | enum | `complete`/`pending_label`/`partial` |
| `marker` | str | `""` 或 `partial`（🟡 用） |
| `video` | bool | 來源是否為影片截圖 |
| `num` | int | 拍攝序號（排序用） |

## 給 React 階段的提示

- 用 `uid` 當 list key；用 `ex` / `exhibitions` 做側欄；`dynasty`/`material` 做 facet 篩選。
- 多圖卡（`image_count>1`）可做輪播／放大鏡。
- `video:true` 標「影片」；`status!=='complete'` 標 🟡。
- 之後要加的「特別酷／精選」：建議新增 `highlight: bool` 與 `fav_note: str` 欄位（目前未用），由人工清單注入。
- 深入查詢外連目前在前端即時組（Google + 故宮典藏庫），未存進資料。
