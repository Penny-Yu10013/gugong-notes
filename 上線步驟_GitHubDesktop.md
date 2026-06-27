# 用 GitHub Desktop 把滑覽版放上網（GitHub Pages）

專案已經是 git repo、部署設定（GitHub Actions）也備好了。你只要照下面點：

## 一、第一次上線

1. **GitHub Desktop** → 上方 `File` → `Add local repository…`
   選資料夾：`C:\Users\yu2_7\Downloads\故宮0625`（已是 repo，會直接認得）。
2. 左側會列出要提交的檔案（約 2000 個，主要是優化過的圖）。
   左下角填 Summary 例如「初版」→ 按 **Commit to main**。
3. 右上 **Publish repository**：
   - **務必取消勾選「Keep this code private」**（免費 GitHub Pages 需要公開 repo）。
   - 名稱例如 `gugong-notes`，按 Publish。第一次會上傳約 100MB 圖，等幾分鐘。
4. 用瀏覽器打開這個 repo 的 GitHub 網頁 → `Settings` → 左欄 `Pages`：
   - 「Build and deployment」的 **Source** 選 **GitHub Actions**（通常已自動是，不是的話手動選）。
5. 切到 repo 的 **Actions** 分頁，會看到「Deploy 故宮速記 to GitHub Pages」在跑，
   等變成綠勾（約 1–3 分鐘）。
6. 完成後網址是：
   **https://<你的GitHub帳號>.github.io/<repo名>/**
   （Actions 跑完那筆 deploy 點進去也會顯示 page_url）

把這個網址丟給朋友、或手機瀏覽器打開 → 就是滑覽版，手機會自動收側欄、響應式排版。

## 二、之後內容有更新時

1. 如果**資料有改**（OCR、精選、編號…）：先在這資料夾跑
   ```powershell
   python _build.py
   python _html.py
   python _webassets.py    # 重新產生 web/public 的優化圖與 cards.json
   ```
   （只改程式、沒動資料，可跳過這步。）
2. GitHub Desktop：填 Summary → **Commit to main** → **Push origin**。
3. Actions 會自動重新 build + 部署，等綠勾後重新整理網頁即可。

## 注意
- **公開**：repo 與圖片是公開的，任何拿到網址的人都看得到（給朋友看沒問題，但不是私密）。
  想要不公開又要線上，需要 GitHub Pro（私人 repo 才能開 Pages），或改用別的私密託管。
- 本機 `npm run build` 仍會崩沒關係——上線是 GitHub 在 Linux 上 build，繞過了那個問題。
- 自己看用 `cd web; npm run dev`（http://localhost:5173）。
