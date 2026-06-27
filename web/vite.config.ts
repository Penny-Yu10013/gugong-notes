import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base './' → 可部署在 GitHub Pages 子路徑 (https://user.github.io/<repo>/) 也能正確載入。
// 圖片與資料放在 public/(img、thumb、data/cards.json)，build 時自動進 dist。
export default defineConfig({
  base: './',
  plugins: [react()],
})
