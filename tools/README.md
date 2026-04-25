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
python3 tools/pdf_to_vocab.py "<PDF 完整路徑>" \
    --semester 2026-fall \
    --start-week 1
```

參數說明：

| 參數 | 用途 |
|---|---|
| `--semester` | 學期代號，命名規則 `<year>-<spring/fall>` |
| `--start-week` | PDF 第 1 頁對應第幾週（一般填 `1`） |
| `--pages N` | 只跑前 N 頁試水溫（驗 OCR 品質用） |
| `--out-dir` | 預設 `tools/ocr_output/`，不用改 |

每頁 ≈ 10 秒。輸出在 `tools/ocr_output/<semester>_weekNN.json`。

### 1a. PDF 結構不規則時

實測 2026 Spring 的 PDF 第 10 頁是「W12-21 spelling 概覽表」、不是單週詳細頁，Gemini 會硬掰一份假資料出來。**OCR 完一定要抽查**：

```bash
cd tools/ocr_output
for w in 01 02 ... 19; do
  echo "=== Week $w ==="
  python3 -c "import json; d=json.load(open('<semester>_week${w}.json')); \
    [print(f\"  {x['n']:2d}. {x['word']}\") for x in d['words']]"
done
```

對照 PDF 每頁 header 上的 `Week N` 確認週次有沒有錯位。如果發現有：

- **整頁亂掰** → 砍那個 JSON 檔（如 2026 Spring W10）
- **頁碼錯位** → 用 Python 一次重命名 + 改內部 `week` 欄位

範例（修正錯位）：

```python
import json
from pathlib import Path
remap = {11: 12, 12: 13, ..., 17: 19, 18: 20, 19: 21}  # 跳過 W18 Review
loaded = {}
for cur, real in remap.items():
    fp = Path(f'2026-spring_week{cur:02d}.json')
    obj = json.loads(fp.read_text())
    obj['week'] = real
    loaded[real] = obj
    fp.unlink()
for real, obj in loaded.items():
    Path(f'2026-spring_week{real:02d}.json').write_text(
        json.dumps(obj, ensure_ascii=False, indent=2)
    )
```

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
| Gemini OCR 失敗單頁 | API 短暫抖動 | 重跑該頁：`--pages 1 --start-week N` |
| OCR 出來一頁是別頁的內容 | PDF 有非單字頁，Gemini 幻想 | 砍該 JSON、用上面的 remap 修頁碼 |
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
    ├── pdf_to_vocab.py     ← OCR 入口
    ├── json_to_js.py       ← JSON → JS 轉檔
    ├── ocr_output/         ← 暫存（gitignored）
    └── manifest_snippet.txt ← 每次跑會覆蓋
```
