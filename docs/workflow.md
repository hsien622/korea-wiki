# Loop / Graph 設計

```mermaid
flowchart TD
  A[取得資料：只收有網址的真實來源] --> B{來源檢查：有網址嗎？官方或民間？}
  B -- 不通過 --> A
  B -- 通過 --> C[ingest 進 raw/ 並寫 log]
  C --> D[寫 Wiki 主張：id、官方或民間、來源編號]
  D --> E{check：來源存在？官方標示成立？raw 有被引用？}
  E -- 有錯 --> D
  E -- 通過 --> F[查詢 Wiki：在 slides.json 選出要用的主張]
  F --> G[build：主張原樣帶入簡報]
  G --> H{check：簡報與 Wiki 一致？說明文字無數字？}
  H -- 有錯 --> F
  H -- 通過 --> I[發佈 GitHub Pages]
```

## 哪些步驟會重複
有三個迴圈：B 退回 A（來源不合格就換來源）、E 退回 D（主張有錯就改 Wiki）、H 退回 F（簡報有錯就改大綱）。每個迴圈都是跑到通過為止。

## 哪裡檢查或重新生成
- B：來源檢查，目前由人判斷來源是否真實、屬於官方或民間。
- E：`python3 tools/wiki.py check` 檢查 Wiki 與 raw 的對應。
- H：`build` 之後再跑一次 `check`，確認簡報沒有超出 Wiki。
- 重新生成：Wiki 有修改，簡報一定要重新 build，不手改 index.html。

## 為什麼這樣設計
錯誤越晚發現，修正成本越高。簡報看起來完整，但事實可能早就錯了。所以把檢查放在資料進來之前（B）、Wiki 寫完之後（E）、簡報產生之後（H）三個位置，每一關只負責一種錯誤。
