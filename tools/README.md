# tools/ — 新學期單字擴充流程

下學期收到新的 PDF 單字表時，照這份 SOP 跑一次就能擴充進站。

## 前置需求

- macOS + Python 3.10+
- `pip3 install pypdfium2 Pillow`
- Gemini CLI 已登入（`oauth-personal`）：`gemini --version`
- 工作目錄在 `~/Documents/KJ-agent/`（OCR 暫存路徑相依此）

## 1. 把新 PDF OCR 成 JSON

```bash
cd ~/Documents/KJ-agent/esl-vocab-practice
python3 tools/pdf_to_vocab.py "<PDF 完整路徑>" --semester 2026-fall
```

參數說明：

| 參數 | 用途 |
|---|---|
| `--semester` | 學期代號，命名規則 `<year>-<spring/fall>` |
| `--start-page` | 從 PDF 第幾頁開始（1-based，預設 1，用於失敗單頁重跑）|
| `--pages N` | 只處理 N 頁（試水溫或重跑用） |
| `--out-dir` | 預設 `tools/ocr_output/`，不用改 |

**自動處理**：
- 週次由 Gemini 從頁首 "Week N" 自動讀出（不需手動對應頁→週）
- 非單字頁（概覽表、Review、封面、空白頁）會自動偵測並跳過
- 若同週次重複出現會覆寫，並印出警告

每頁 ≈ 10 秒。輸出在 `tools/ocr_output/<semester>_weekNN.json`，最後印出收進的週次清單。

### 1a. 跑完抽查

雖然週次偵測 + 跳頁邏輯已經很穩，OCR 文字內容仍建議快速抽查：

```bash
cd tools/ocr_output
for f in <semester>_week*.json; do
  echo "=== $f ==="
  python3 -c "import json; d=json.load(open('$f')); \
    [print(f\"  {x['n']:2d}. {x['word']}\") for x in d['words']]"
done
```

如果某週 OCR 失敗或內容怪怪的，直接用 `--start-page N --pages 1` 重跑那一頁。

## 2. JSON → JS 資料檔

```bash
python3 tools/json_to_js.py \
    --input tools/ocr_output \
    --semester 2026-fall \
    --out-dir .
```

會在 repo 根產出 `<prefix>_weekNN_data.js`（命名規則：`spring2026Week1Data`、`fall2026Week1Data` 等），並另外產 `tools/manifest_snippet.txt` 裡是 manifest 片段。

如果要新增學期前綴，編輯 `tools/json_to_js.py` 的 `SEMESTER_VAR_PREFIX` 與 `SEMESTER_LABEL` 兩個對照表。

## 3. 接進前端

三個地方要改：

### 3a. `index.html` 的 `<script>` 載入清單

每週一行，照週次順序：

```html
<script src="fall2026_week01_data.js"></script>
<script src="fall2026_week02_data.js"></script>
...
```

### 3b. `vocab_manifest.js` 的 `VOCAB_MANIFEST`

把 `tools/manifest_snippet.txt` 的內容貼進去（保持登記順序，新學期接在現有 entries 之後）。

### 3c. `vocab_manifest.js` 的 `VOCAB_DATA`

每個 dataVar 名要列進物件中（頂層 `const` 不會自動掛 `window`，必須顯式列名）：

```js
const VOCAB_DATA = {
    week12Data, ..., spring2026Week21Data,
    // ↓ 新增的列在這
    fall2026Week1Data, fall2026Week2Data, ...
};
```

## 4. 本地測試

```bash
cd ~/Documents/KJ-agent/esl-vocab-practice
python3 -m http.server 8765
# 瀏覽器打開 http://localhost:8765/index.html
```

驗證：

- 下拉選單有新學期的 optgroup
- 每週切換能看到對應單字
- 該學期的 `🔥 ALL` 數量 = 週數 × 10
- 切回舊學期不受影響

## 5. Commit & Push

```bash
git add .
git commit -m "擴充 2026 Fall 學期 N 週單字"
git push
```

## 常見坑

| 症狀 | 原因 | 解法 |
|---|---|---|
| Gemini OCR 失敗單頁 | API 短暫抖動 | 重跑該頁：`--start-page N --pages 1` |
| 某頁顯示「⏭ 跳過：…」 | 該頁不是單字表（概覽、Review 等） | 正常行為，不用處理 |
| 某週的 OCR 有錯字或漏字 | 圖片解析度或 Gemini 偶爾失誤 | 重跑該頁，或手動編輯 JSON 後重跑 json_to_js.py |
| `Data missing for this week!` | `VOCAB_DATA` 漏列 dataVar | 把名字加進 `vocab_manifest.js` 的 `VOCAB_DATA` |
| 下拉選單缺新週 | manifest 沒更新 | 把 snippet 貼進 `VOCAB_MANIFEST` |
| 載入了但選了沒反應 | `<script src>` 沒加 | 在 index.html 補對應的 script 標籤 |

## 檔案速查

```
esl-vocab-practice/
├── index.html              ← 主頁，改 <script src> 載入清單
├── vocab_manifest.js       ← 改 VOCAB_MANIFEST 與 VOCAB_DATA
├── shop_data.js
├── week12_data.js…week19_data.js          ← 2025 Fall（不要動）
├── spring2026_week01_data.js…week21_data.js  ← 2026 Spring
├── fall2026_week*.js       ← 下學期會在這
├── images/
└── tools/
    ├── pdf_to_vocab.py        ← OCR 入口（自動偵測非單字頁、自動抓週次）
    ├── json_to_js.py          ← JSON → JS 轉檔
    ├── backfill_category.py   ← 一次性：為 2025 Fall 舊資料補 category 欄位（已跑過）
    ├── ocr_output/            ← 暫存（gitignored）
    └── manifest_snippet.txt   ← 每次跑會覆蓋
```
