# AGENTS.md：韓國自由行 LLM Wiki 與教學簡報

## 目的
用「來源可追溯的 Wiki」產生教學簡報。簡報裡每一個事實，都必須能追回 Wiki 主張，再追回 raw/ 的原始來源。

## 結構
```
raw/    原始來源，一份一個 TXT，檔名以兩位數編號開頭（01_xxx.txt 對應 S01）
wiki/   index.md、log.md，以及主題頁（entry、transport、tax、customs、safety）
docs/   discussion.md（討論紀錄）、workflow.md（流程圖）、run-log.md（執行紀錄與反思）
tools/  wiki.py（build、check）、slides.json（簡報大綱）
index.html  由 build 產生，不要手改
```

## Ingest 規則（新增來源）
1. 只收有網址的真實來源。無法追溯的資料不可當來源。
2. raw 檔格式：標題、來源網址、教材整理日期、資料類型、【內容】。
3. 官方 = 網址含 boca.gov.tw 或 visitkorea.or.kr；其他都是民間。
4. 在 wiki/log.md 記一筆 ingest。

## Wiki 主張格式（每條一行，不可省略）
`- {頁面-編號} 【官方|民間】內容。 [Sxx]`
- 一條主張只講一件事；數字、日期、金額必須和來源一致。
- 標【官方】的主張，引用的來源至少要有一份官方網址。
- 來源沒寫的內容不可寫進 Wiki，不可憑記憶補充。

## 簡報規則
- 簡報頁只能引用 Wiki 主張 id（在 tools/slides.json 的 claims 列出），文字由 build 原樣帶入。
- 每頁的教學說明（note）可以自己寫，但不可含任何數字。
- 每頁必須標示 data-wiki，每個主張卡片附來源連結與官方或民間標籤。

## Loop（每次修改都跑）
取得資料 → ingest 進 raw/ → 寫 Wiki 主張 → `python3 tools/wiki.py check` → 有錯就退回修 Wiki → 編輯 slides.json → `python3 tools/wiki.py build` → 再 check → 全部通過才發佈。
check 會擋下：主張缺來源或來源不存在、標官方卻沒有官方網址、raw 沒被引用、簡報引用不存在的主張、簡報文字與 Wiki 不一致、說明文字出現數字。

## 禁止
- 手改 index.html；Wiki 以外的事實進簡報；把民間資料標成官方；刪除 log 紀錄。
