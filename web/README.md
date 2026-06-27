# 故宮速記 · React/Reactbits 版

Vite 7 + React + TypeScript + 純 CSS + motion(Framer Motion) + ogl(Circular Gallery)。
資料來源 = 專案根目錄的 `data/cards.json`、`img/`(大圖)、`thumb/`(縮圖)。
由 `vite.config.ts` 的 `localAssets` plugin 直接服務(不複製、不佔空間)；重跑 `_build.py` 會即時同步。

## 啟動（日常用這個）

```bash
cd web
npm install      # 第一次才需要
npm run dev      # → http://localhost:5174
```

## ⚠️ 關於 `npm run build`（產生 dist）

目前在這台機器 **build 會原生崩潰**（exit 0xC0000409）。實測證明**與本專案程式碼無關**：
即使把畫面元件全部拿掉，`vite build` 仍崩——這是 **rollup 原生套件在 Node 24 + Windows 的已知問題**，
`dev` 用的是 esbuild 不受影響、功能完整。

要產生可分享 dist 時，任一即可：
- **改用 Node 22 LTS**（最穩；用 nvm-windows 切換後 `npm run build` 即正常），或
- 直接用根目錄那份 **`index.html` 靜態版**當分享檔（雙擊就開，本來就是單檔可攜）。

`dev` 模式日常使用完全不受此影響。

## Reactbits 風格動效（目前·克制）

- **BlurText**：標題逐字去模糊淡入（一次）。`src/effects.tsx`
- **AnimatedContent**：切換展區時內容淡入上浮。`src/effects.tsx`
- **SpotlightCard**：游標跟隨的暖色光暈（hover）。`src/effects.tsx` + `.card .spot`
- **CircularGallery**（滑覽）：水平拖曳相片牆。`bend=0`(不彎)、`wobble=0`(不晃)、點圖開卡。`src/CircularGallery.tsx`
- **Modal**：scale + fade 進出（motion `AnimatePresence`）。

要加更多 Reactbits 效果：逛 https://reactbits.dev ，把想要的元件名稱給我整合。動畫強度目前設定為「克制·美術館感」。

## 結構
- `src/App.tsx` — 主畫面（側欄／工具列／網格／滑覽／詳情）
- `src/CircularGallery.tsx` — Reactbits 滑覽元件（已加 `wobble` 與 `onItemClick`）
- `src/effects.tsx` — BlurText / AnimatedContent / Spotlight
- `src/types.ts` — cards.json 型別（對應 `../data/SCHEMA.md`）
- 圖片不放在 `public/`，由 `vite.config.ts` 的 `localAssets` plugin 從根目錄 `img/`、`thumb/`、`data/` 直接服務
