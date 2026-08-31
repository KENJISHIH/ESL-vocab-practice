# tools/ — 單字擴充、發音與每日進度 SOP

這份文件是把新學期／新一週的單字接進站的完整作業程序。**照著跑不會漏發音、不會漏中文釋義、不會忘記改每日進度。**

> ⚠️ 兩個最容易踩的雷，先講在前面：
> 1. **產完 JS 資料檔不等於做完**——還要產音檔（[§5](#5-音檔系統)）、補中文釋義（[§6](#6-中文釋義-zh)）、改 `DAILY_PLAN`（[§4](#4-每日進度計畫-daily_plan)）。用 `tools/check_coverage.py` 確認，不要用回想的。
> 2. **一週跨多頁的單字本要用 `--group N`**，否則第二頁抓不到週次，而且兩頁會被當兩週互相覆蓋。2026 Fall 是一週兩頁 → `--group 2`。
>
> （舊版這裡警告過「重跑 `json_to_js.py` 會洗掉 `zh`」——2026-09-01 已修，現在重跑會把既有的 `zh` 讀回來。）

## 動工前後都跑這兩支，不要靠記性

單字匯進來很容易，忘記補中文釋義與音檔更容易（2026 Spring 就有 9 週停在只有英文的狀態）。所以「有沒有做完」不是用回想的，是用跑的：

```bash
python3 tools/check_coverage.py 2026-fall   # 字數／中文／音檔，全綠才算完成（缺就 exit 1）
node     tools/test_dailyplan.js            # 每日進度的週次運算，20 項斷言
```

`check_coverage.py` 會逐週列出還缺幾筆 `zh`、幾個音檔，並且抓出**字數不是 10 的週次**——每天 2 個字 × 5 天剛好 10 個，少了那一週的 Day5 會沒東西可背。

---

## 0. 前置需求

### 系統

- macOS（`afconvert` 是系統內建，用來把 WAV 轉 m4a，不需另外安裝）
- Python 3.10+（本機 `python3` = 3.11.8）
- 工作目錄根在 `~/Documents/KJ-agent/`（Gemini CLI 的 `@path` 相對於這個 workspace root，換位置會抓不到圖）

### Python 套件（本機規範：uv 優先，不要用 pip3）

```bash
# 專案依賴（建議在 repo 內建 venv）
uv venv
uv pip install pypdfium2 Pillow certifi google-genai
```

| 套件 | 誰在用 | 為什麼需要 |
|---|---|---|
| `pypdfium2` | `pdf_to_vocab.py` | PDF 逐頁渲染成 PNG 給 Gemini 看 |
| `Pillow` | `pdf_to_vocab.py`、`place_item.py`、`make_icon.py` | 影像處理 |
| `certifi` | `batch_tts.py` | **macOS 系統 Python 沒掛 CA bundle**，直打 HTTPS 會 SSL 憑證錯誤，腳本明確用 certifi 的 bundle |
| `google-genai` | `gen_item.py` | 換裝素材生圖（只有做 Avatar Shop 素材才會用到） |

跨專案 CLI 工具另外裝（只有 `place_item.py` 遇到「假透明」原圖才會呼叫）：

```bash
uv tool install 'rembg[cpu]'
```

### Gemini 存取

- **Gemini CLI**（`pdf_to_vocab.py` 用）：`gemini --version` 應為 0.35.0
- **API key 模式**（不是 `oauth-personal`——個人 OAuth 路徑已於 2026-06-18 被 Google 停用）
- key 唯一存放處 `~/.gemini/.env` 的 `GEMINI_API_KEY=`；`batch_tts.py` / `gen_item.py` 直接讀這個檔自己打 REST API，不透過 CLI

### 音檔快取來源

`export_tts.py` 從「一查究竟（peek-dict）」App 的 TTS 快取目錄反查 WAV：

```
~/Library/Caches/com.kenjishih.peekdict/tts/<sha256>.wav
```

`batch_tts.py` 產生的音檔也是**寫進這個同一個快取**（同一套 key 公式），所以 App 之後查同一個字會直接命中。

---

## 1. 新增一個學期（完整 SOP）

以「2026 Fall」為例。九個步驟，**每一步都要做完**。

### 1-1. 來源 → JSON（Gemini OCR）

來源可以是掃描 PDF，**也可以是手機翻拍的照片**（2026 Fall 的單字本就是拍的）：

```bash
# 掃描 PDF
python3 tools/pdf_to_vocab.py "<PDF 完整路徑>" --semester 2026-fall

# 手機照片：一週跨兩頁，所以 --group 2（見下方說明）
python3 tools/pdf_to_vocab.py "<資料夾>"/IMG_30[7-9]*.HEIC --semester 2026-fall --group 2
```

| 參數 | 用途 |
|---|---|
| `--semester` | 學期代號，格式固定 `<year>-<spring\|fall>` |
| `--group N` | **幾頁算一週**（預設 1）。一週跨兩頁就填 2 |
| `--start-page` | PDF 專用：從第幾頁開始（1-based，預設 1；失敗單頁重跑用） |
| `--pages N` | PDF 專用：只處理 N 頁（試水溫或重跑用） |
| `--out-dir` | 預設 `tools/ocr_output/`，不用改 |

#### 🔴 一週跨多頁一定要用 `--group`

2026 Fall 的單字表**一週兩頁**：第一頁有「2026 Fall Semester Week N」標題和前 6 個字，
第二頁接第 7 個字與 Science 段的 8–10。**第二頁沒有 Week 標題**，單獨送去辨識會失敗
（抓不到週次），而且兩頁會被當成兩週互相覆蓋。

`--group 2` 會把連續兩頁併成一次 Gemini 呼叫，讓它看得到標題也拼得出完整的 10 個字，
順帶把 API 呼叫數減半。**照片必須依序排好**（IMG_3070、IMG_3071 = W1，依此類推），
shell 展開 glob 本來就是檔名順序，通常不用特別處理。

換學期前先翻一下單字本：一週幾頁？頁碼有沒有跳號？決定 `--group` 要填幾。

#### 照片來源的處理

- HEIC 用 macOS 內建 `sips` 轉，不用另外裝 pillow-heif
- 會套用 EXIF 方向資訊（照片轉正）、長邊縮到 2000px（省 token，實測辨識率不受影響）
- **保留彩色**：小孩會用螢光筆畫重點，prompt 已交代忽略手寫與螢光標記

#### 自動處理的部分

- **週次由 Gemini 從頁首 "Week N" 讀出**，不需要人工對應「第幾頁 = 第幾週」
- 非單字頁（跨週概覽、spelling 總表、Review & Final Exam、封面、空白頁）會回 `SKIP` 自動跳過
- `category` 欄位（`Reading` / `Science`）**由 Gemini 逐字判斷**，依表格裡的分段標題認定——不是「前 8 字 Reading、後 2 字 Science」這種寫死規則。2026 Spring 是 8+2、2026 Fall 是 7+3
- 同一週次重複出現會覆寫並印警告
- 每筆不是 10 個字時會印 `⚠️` 但不中斷

每組約 10–20 秒。輸出：`tools/ocr_output/<semester>_weekNN.json` 加一份彙整的 `<semester>_all.json`，最後印出收進的週次清單。

### 1-2. 抽查 OCR 結果

```bash
cd tools/ocr_output
for f in 2026-fall_week*.json; do
  echo "=== $f ==="
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); \
    [print(f\"  {x['n']:2d}. {x['word']:<14s} {x.get('category','')}\") for x in d['words']]" "$f"
done
```

某週失敗或內容明顯有錯 → 用 `--start-page N --pages 1` 重跑那一頁，或直接手改 JSON。

### 1-3. JSON → JS 資料檔

```bash
python3 tools/json_to_js.py \
    --input tools/ocr_output \
    --semester 2026-fall \
    --out-dir .
```

產出：

- repo 根的 `fall2026_weekNN_data.js`（變數名 `fall2026WeekNData`，**注意變數名的週次沒有補零**，檔名有）
- `tools/manifest_snippet.txt`（manifest 片段，gitignored，每次跑會覆蓋）

新學期前綴要先在 `tools/json_to_js.py` 的 `SEMESTER_VAR_PREFIX` 與 `SEMESTER_LABEL` 兩張對照表登記（目前已含 2025/2026 的 spring 與 fall）。

> 🚨 **這一步是破壞性的**：`json_to_js.py` 只會寫出 `word` / `pos` / `def` / `ex` / `category` 五個欄位。已經存在的檔案會被整個覆蓋，**手工加的 `zh` 中文釋義會被洗掉**。所以正確順序是：先跑完這步，**再**補 `zh`（[§6](#6-中文釋義-zh手工欄位重跑會被洗掉)）。

### 1-4. 接進前端

#### (a)(b)(c) 跑一支腳本就好

`index.html` 的 `<script>` 清單、`VOCAB_MANIFEST`、`VOCAB_DATA` 這三處以前要手工同步，
現在交給腳本掃檔案系統重新產生：

```bash
python3 tools/sync_manifest.py           # 實際寫入
python3 tools/sync_manifest.py --check   # 只比對，有落差 exit 1
```

它會列出各學期收了幾週，確認數字對得上再往下走。

背後處理掉的幾件事（知道就好，不用自己顧）：

- `<script>` 一定排在 `vocab_manifest.js` 之前——`VOCAB_DATA` 在 parse 當下就要參照到那些 `const`，順序反了會 `ReferenceError`
- `VOCAB_DATA` 的變數名是**從檔案內容讀出來的**，不是用檔名猜的（檔名補零 `week01`、變數名不補零 `Week1Data`，靠猜會錯）
- 漏列 `VOCAB_DATA` 的症狀是切到那一週才跳 `Data missing for this week!`，很難發現——所以才要自動產

> 腳本靠 `index.html` 與 `vocab_manifest.js` 裡的區塊標記（`DATA_SCRIPTS:START/END`、
> `VOCAB_MANIFEST:START/END`、`VOCAB_DATA:START/END`）定位。**不要刪掉那些標記**，
> 也不要在標記之間手改，下次跑會被覆蓋。

以下 (d)(e) 兩處仍需手動，因為那是人的判斷，掃檔案掃不出來。

#### (d) `vocab_manifest.js` 的 `EXAM_RANGES`

考試範圍快選。每筆 `{ semester, id, label, weeks }`，`buildWeekSelector()` 會自動長出選項：

```js
const EXAM_RANGES = [
    { semester: '2026-fall', id: 'midterm', label: '📝 期中考範圍 (W1-W9)', weeks: [1,2,3,4,5,6,7,8,9] },
    { semester: '2026-fall', id: 'final',   label: '🎯 期末考範圍 (W12-W21)', weeks: [12,13,14,15,16,17,19,20,21] },
];
```

- `id` 在同一個 semester 內不可重複（下拉的 value 是 `range:<semester>:<id>`）
- `weeks` 裡列到但 manifest 沒有的週會被安靜略過，**所以 label 上寫的週數要自己對過**
- 沒有考試範圍時可以先不加，等老師公布再補

#### (e) `vocab_manifest.js` 的 `DAILY_PLAN`（**新學期一定要改，不改首頁的「今天」會整個錯**）

見下面 [§4](#4-每日進度計畫-daily_plan) 完整說明。最少要動這兩行：

```js
const DAILY_PLAN = {
    semester: '2026-fall',      // ← 改成新學期代號
    startDate: '2026-08-31',    // ← 改成該學期 W1 的「星期一」
    ...
    skipDates: [],              // ← 把國定假日／連假／段考週的平日填進來
};
```

### 1-5. 產發音音檔

```bash
python3 tools/batch_tts.py fall2026_week01_data.js fall2026_week02_data.js
```

或直接補全站所有缺的字（推薦，冪等）：

```bash
python3 tools/batch_tts.py --all
```

細節與配額行為見 [§5](#5-音檔系統)。**這一步不做，新一週的字按 🔈 只會退回瀏覽器機械音。**

### 1-6. 補中文釋義 `zh`

手工在 `*_data.js` 每筆物件加 `zh: '…'`。見 [§6](#6-中文釋義-zh手工欄位重跑會被洗掉)。

### 1-7. 本地測試

```bash
python3 -m http.server 8765
# 瀏覽器打開 http://localhost:8765/index.html
```

驗證清單：

- [ ] 下拉選單有新學期的 optgroup，每週切換都看得到對應單字
- [ ] 該學期 `🔥 ALL` 的數量 = 週數 × 10
- [ ] 考試範圍選項出得來，數量對得上
- [ ] 每個字按 🔈 是 Achernar 真人音（不是機械音）
- [ ] 有 `zh` 的週，上方「顯示中文釋義」按鈕會出現且展開正常
- [ ] 首頁「今天」卡片顯示的 `W? Day?` 對得上老師的實際進度
- [ ] 切回舊學期完全不受影響

### 1-8. 更新 CHANGELOG 並推上去

有使用者看得到的變化就補一筆到根目錄 `CHANGELOG.md`（最新在最上面，日期用實際 push 日）。

```bash
git add .
git commit -m "擴充 2026 Fall 學期 N 週單字（含發音與中文釋義）"
git push origin main
```

推上 GitHub Pages 後線上就是最新版（`sw.js` 對程式與資料走 network-first，不必手動清快取）。

---

## 2. 新增單一週（學期中每週例行）

老師發了新一週的單字表時：

1. **OCR 那一頁**
   ```bash
   python3 tools/pdf_to_vocab.py "<PDF>" --semester 2026-fall --start-page <該週的頁碼> --pages 1
   ```
2. **轉 JS**（會把 `ocr_output/` 裡所有該學期的週都重轉一次）
   ```bash
   python3 tools/json_to_js.py --input tools/ocr_output --semester 2026-fall --out-dir .
   ```
   ⚠️ 這會覆蓋**所有**已存在的該學期 `*_data.js`。若舊週已經補過 `zh`，先把 `ocr_output/` 裡不需要重轉的週次 JSON 移走，或轉完後把被洗掉的 `zh` 補回來。單週作業更安全的做法是：只留該週的 JSON 在 `ocr_output/`。
3. **加一行到 `index.html` 的 `<script>` 清單**
4. **加一行到 `VOCAB_MANIFEST`、一個名字到 `VOCAB_DATA`**
5. **（若這週屬於某個考試範圍）把週次加進 `EXAM_RANGES` 對應那筆的 `weeks`**
6. **產音檔**：`python3 tools/batch_tts.py fall2026_weekNN_data.js`
7. **補 `zh` 中文釋義**
8. **（若這週前後有放假）把不上課的平日加進 `DAILY_PLAN.skipDates`**
9. 本地開起來看一眼 → commit / push

---

## 3. 現有資料的週次分佈（不要假設連號）

| 學期 | 實際有的週次 | 備註 |
|---|---|---|
| 2025 Fall | W12–W19（8 週） | 舊格式，`backfill_category.py` 已補過 `category` |
| 2026 Spring | W1–W9、W12–W17、W19–W21（**共 18 週**） | **缺 W10、W11、W18**——不是 W1–W21 連號 |

缺號的原因是那幾頁在 PDF 裡是概覽／Review 頁，OCR 階段就被 `SKIP` 掉了。寫任何「從 W1 跑到 W21」的迴圈或 label 之前先對一次 `VOCAB_MANIFEST`。

---

## 4. 每日進度計畫 `DAILY_PLAN`

首頁「今天」模式靠這個區塊算出「今天要背哪兩個字」。定義在 `vocab_manifest.js`。

```js
const DAILY_PLAN = {
    semester: '2026-fall',
    startDate: '2026-08-31',   // 必須是該學期 W1 的星期一
    wordsPerDay: 2,
    daysPerWeek: 5,            // Day1=週一 … Day5=週五
    skipDates: ['2026-09-25', '2026-10-09', '2027-01-01'],   // 放假的平日，純標示用
};
```

### 它怎麼算（用日曆週，不是累計上課日）

1. `weekAndDay()` 先把今天回推到**所屬那一週的星期一**，再算它跟 `startDate` 差幾週
2. `weekNo = 相差週數 + 1`；`dayInWeek` 直接就是星期幾（週一=1 … 週五=5，週末停在 Day5）
3. 到 `VOCAB_MANIFEST` 找 `semester` + `weekNo` 那一筆，取出該週單字陣列
4. 今天的新字 = 陣列的第 `(dayInWeek-1)*2` 到 `+2` 個（Day1 = 第 1–2 個字、Day2 = 第 3–4 個 … Day5 = 第 9–10 個）
5. 另外回傳 `soFar`（本週到今天累積，週末複習用）與 `weekWords`（整週，給 Quiz 當誘答選項池）

回傳的 `status` 三種：`not-started`（今天早於 `startDate`）／`no-data`（算出來的那一週還沒匯入）／`ok`。

> **為什麼不用「累計上課日 ÷ 5」？**
> 這是 2026-08-31 修掉的一個設計錯誤。老師的 W1／W2／W3 是照**日曆週**編號的，放假不會讓週次順延——中秋節（2026-09-25 週五）放假，下週一還是 W5 Day1，不會變成 W4 Day5。用累計上課日的話，只要遇到一天國定假日，之後整學期的週次全部偏移一天，而且**畫面上完全看不出來**，只會發現她背的字跟老師教的對不上。
>
> 改用日曆週之後，放假、複習週、颱風假都不會影響週次對齊。`tools/test_dailyplan.js` 有 20 項斷言守著這件事。

### 每學期要做的兩件事

1. **改 `semester`** 成新學期代號——沒改的話會一直去撈上學期的週次
2. **改 `startDate`** 成新學期 W1 的**星期一**。填成別的星期幾，`Day1` 的錨點就整個偏掉；程式不會檢查也不會報錯

改完跑 `node tools/test_dailyplan.js` 驗一次（測試裡的日期要跟著新學期改）。

### `skipDates` 現在只是標示用

放假的平日填進來，那天會被標成 `isRestDay`，跟週末一樣不加新字、改成複習整週，卡片顯示「🎌 放假複習」。

**它不會影響 `W?/Day?` 的對齊**（週次是照日曆週算的），所以填不填都不會弄錯進度，可以安心留空、也可以事後補。

查國定假日可以用 Twinkle Hub 的 `tw_lookup_holidays`，但**學校行事曆才是準的**（校慶、運動會、彈性放假、颱風假這些國定假日表上沒有）。

### 沒有新單字的週次（複習週／考試週）

學期表裡常有「沒有新單字」的週次——2026 Fall 的 **W10／W11 是 Review + 期中考、W20／W21 是 Review + 期末考**。

這些週**什麼都不用做**：週次照日曆自己走到 W10、W11，manifest 裡沒有這兩週，`getTodayPlan()` 回傳 `status: 'no-data'`，首頁顯示「📦 W10 的單字還沒匯入」，兩週後自動接上 W12。

想讓那兩週顯示得更貼切（例如「這兩週是複習週，來練 🔁 複習錯過的字」），是改 `renderDailyCard()` 的文案或在 manifest 補一筆標記，**不要動 `skipDates`**——那是給「沒去上學的日子」用的，語意不同。

---

## 5. 音檔系統

發音用的是「一查究竟」App 同款的 Gemini TTS（模型 `gemini-2.5-flash-preview-tts`、語音 `Achernar`），預先產成 `audio/<word>.m4a`（AAC 32kbps，約 WAV 的 1/8 大小）。

`index.html` 的 `speak(text)` 會去抓 `audio/<text.trim().toLowerCase()>.m4a`，**抓不到才 fallback 到瀏覽器 `speechSynthesis`**（機械音）。所以檔名一律小寫，含空白的短語檔名就帶著空白（例：`audio/try again.m4a`）。

### 三支腳本的分工

| 腳本 | 做什麼 |
|---|---|
| `batch_tts.py` | **產音源**。直打 Gemini REST API，把 WAV 寫進 peek-dict 快取，跑完自動呼叫 `export_tts.py` |
| `export_tts.py` | **轉檔匯出**。掃站內所有 `*_data.js` 的單字，到 peek-dict 快取用 SHA256 反查 WAV，`afconvert` 轉成 m4a 放進 `audio/`，並列出快取裡還沒有的字 |
| `gen_phrase_tts.py` | **UI 短語專用**。繞過「單字表」過濾，直接產非單字的語音（Quiz 的 Correct / Try again 就是這樣做的） |

### `batch_tts.py` 用法

```bash
# 指定資料檔（可多個）
python3 tools/batch_tts.py fall2026_week01_data.js fall2026_week02_data.js

# 補全站所有還缺音檔的字
python3 tools/batch_tts.py --all
```

- **冪等**：已經有快取、或 `audio/` 已經有 m4a 的字會自動跳過，重跑只補缺的
- 請求間隔固定 8 秒（`PACE_SEC`）——preview TTS 模型的 RPM 很低，實測 3 秒會被 429 轟炸
- preview 模型偶爾回空回應（沒有 content），會自動重試 5 次、每次隔 3 秒
- HTTP 500（Google 端暫時性錯誤）同樣重試

### 🔴 撞到每日配額（RPD 100）的行為

TTS 模型每天約 100 次請求上限。腳本現在的處理是：

1. 收到 429 時先看回應內容分辨是「每分鐘節流」還是「每日上限」
2. **每分鐘節流** → 退避重試（30 / 60 / 90 / 120 秒）。若這樣還被擋（等超過 300 秒），保守判定為配額用完
3. **每日上限** → 丟 `QuotaExhausted`，**乾淨中止整批**（不再空燒），印出「本次已產生 N 字、還剩 M 字沒補」，並提示配額於太平洋時間午夜重置（約台北隔天 15:00 之後）
4. 中止後**仍然照常跑 `export_tts.py` 轉檔**，已產生的音檔不會浪費
5. 最後以 **exit code 2** 結束，讓外層腳本判斷

### `補單字音檔.command`（雙擊執行）

repo 根目錄的 `補單字音檔.command` 是包好的一鍵版，做四件事：

1. `python3 tools/batch_tts.py --all`，記下 exit code
2. **只鎖 `audio/`** 做 `git add` / `commit` / `push origin main`（不會誤推其他工作中的改動）；**即使因配額中止（exit 2），已產生的音檔一樣會被推上去**
3. exit code 是 2 時額外印一行：今天配額用完了，音檔都已保留並推上去，**明天再雙擊一次就會接著補**
4. 再跑一次 `export_tts.py` 統計，印出「還缺約 N 字」

所以字很多的學期，正常做法就是**連續幾天每天雙擊一次**，直到「還缺 0 字」。

### 補 UI 短語音檔

```bash
python3 tools/gen_phrase_tts.py "Correct:correct" "Try again:try again"
```

參數格式 `"要唸的文字:輸出檔名（不含副檔名）"`。檔名必須等於 `speak()` 算出來的路徑，也就是**文字轉小寫、前後去空白**。

### 手動補單一個字（不想動 API 時）

在「一查究竟」App 裡查一次那個單字，快取就會生成，然後跑：

```bash
python3 tools/export_tts.py          # 匯出快取裡有的，並列出還缺的
python3 tools/export_tts.py --force  # 連已存在的 m4a 也重轉
```

---

## 6. 中文釋義 `zh`

`zh` 是給孩子看的中文意思，**OCR 不會產**，要另外補。兩個地方都可以放：

| 放在哪 | 適用 | 特性 |
|---|---|---|
| `tools/ocr_output/<semester>_weekNN.json` 的 `zh` 欄位 | 剛 OCR 完、還沒轉檔 | 轉檔時直接帶進 JS，是「來源真相」 |
| `*_data.js` 的 `zh` 欄位 | 事後補、或只改一兩個字 | 重跑 `json_to_js.py` 會自動讀回來保住 |

欄位放在 `word` 後面：

```js
    {
        word: 'went',
        zh: '去（go 的過去式）',      // ← 放在 word 後面
        pos: '(v.)',
        def: 'past simple of go',
        ex: '1. We went to school early this morning.<br>2. My mom went home late yesterday.',
        category: 'Reading',
    },
```

寫中文釋義時**依英文定義消歧義**：同一個英文字有多個中文意思時，只寫這裡教的那個。
例如 `dairy` 的定義是 "food made with milk…"，就寫「乳製品（牛奶做的食物）」，不要寫「酪農場」。

前端行為：

- `renderList()` 檢查「本週**有任一字**含 `zh`」才顯示上方的「顯示中文釋義」按鈕；整週都沒有 `zh` 的話按鈕根本不出現
- 預設收合，切換週次會自動歸零
- `zh` 與 `ex` 一樣不做 HTML 轉義（是自己寫的資料、含刻意的 `<br>`），所以**不要在 `zh` 裡貼來路不明的內容**
- **Spell 出題的提示區**會把 `zh` 接在英文定義下面一起顯示（Quiz 不顯示 `zh`），所以缺 `zh` 的週次拼字時只有英文提示

### 重跑轉檔已經不會洗掉 `zh` 了（2026-09-01 修正）

以前只要對同一個學期再跑一次 `json_to_js.py`，該學期所有 `*_data.js` 會被整檔重寫、
手工加的 `zh` 全部消失，而且不警告不備份。**現在 `existing_zh()` 會先把舊檔的
`word → zh` 讀回來**，JSON 有 `zh` 就優先用、沒有就沿用舊檔，轉檔完會印「沿用舊檔 N 筆」。

`tools/test_zh_preserve.py` 是這件事的回歸測試（拿真實有 `zh` 的週次模擬重跑）：

```bash
python3 tools/test_zh_preserve.py
```

改過 `json_to_js.py` 就跑一次。真的誤洗了也還救得回：`git checkout -- <檔名>`。

### 目前的 `zh` 覆蓋率

用 `python3 tools/check_coverage.py` 查最準。截至 2026-09-01：

- **2026 Fall**：W1 已補（10/10）
- **2026 Spring**：W12–W17、W19–W21 已補（90 字）；**W1–W9 尚未補**
- **2025 Fall**：尚未補

---

## 7. 附錄：Avatar Shop 素材與 App icon

跟單字流程無關，只有要做換裝素材或改 icon 時才會用到。

```bash
# 1. 用 Gemini 生一張物件原圖 → images/_raw/<name>.png（_raw/ 是 gitignored）
python3 tools/gen_item.py round_glasses "a pair of cute round eyeglasses with thin gold frames"

# 2. 對齊到 char_base 位置，輸出 512x512 透明 PNG → images/
python3 tools/place_item.py glasses images/_raw/round_glasses.png
#    preset: shirt / bottom / shoes / hat / glasses / necklace / halo / wings / pet / bg / outfit
#    偵測到「假透明」（AI 把背景畫進像素）會自動呼叫 rembg 去背

# 3. 重新產 PWA icon（icons/ 三張 + favicon.ico）
python3 tools/make_icon.py                                                 # 素顏站姿版
python3 tools/make_icon.py images/outfit_princess.png images/bg_castle.png # 場景版（目前線上用的）
```

換過 icon 或音檔要注意 `sw.js`：`.m4a` / `.png` / `.ico` 等走 **cache-first**，已經把站加到主畫面的裝置會一直用舊快取。同名檔案換內容時，需要改 `sw.js` 的 `CACHE` 版本號（`esl-vocab-v1` → `v2`）才會強制重抓。

---

## 常見坑

| 症狀 | 原因 | 解法 |
|---|---|---|
| Gemini OCR 某頁失敗 | API 短暫抖動 | 重跑該頁：`--start-page N --pages 1` |
| 某頁顯示「⏭ 跳過：…」 | 該頁不是單字表（概覽、Review 等） | 正常行為，不用處理 |
| 某週 OCR 有錯字或漏字 | 圖片解析度或 Gemini 偶爾失誤 | 重跑該頁，或手改 JSON 後重跑 `json_to_js.py` |
| `Data missing for this week!` | `VOCAB_DATA` 漏列 dataVar | 把名字加進 `vocab_manifest.js` 的 `VOCAB_DATA` |
| 下拉選單缺新週 | manifest 沒更新 | 把 `manifest_snippet.txt` 貼進 `VOCAB_MANIFEST` |
| 載入了但選了沒反應 | `<script src>` 沒加 | 在 `index.html` 補對應的 script 標籤 |
| `ReferenceError: xxxData is not defined` | `vocab_manifest.js` 排在資料檔前面 | 資料檔的 `<script>` 一律排在 `vocab_manifest.js` **之前** |
| 考試範圍選項沒出現／字數少了 | `EXAM_RANGES` 沒加，或 `weeks` 裡的週次 manifest 沒有 | 補 `EXAM_RANGES`；`weeks` 對照 manifest 檢查一次 |
| **新一週的字按 🔈 是機械音** | **`audio/<word>.m4a` 不存在，fallback 到瀏覽器 TTS** | **跑 `python3 tools/batch_tts.py <該週_data.js>`，或雙擊 `補單字音檔.command`** |
| **`batch_tts.py` 跑到一半印「⛔ 今日配額已用完」就停** | **撞到 TTS 每日上限（RPD 100）；程式刻意乾淨中止不空燒，exit code 2** | **正常行為。已產生的音檔已轉檔並（走 .command 的話）推上去了；配額太平洋午夜重置，隔天台北 15:00 後再跑一次接著補** |
| 429 但等一等又好了 | 每分鐘節流（RPM），不是每日上限 | 腳本自己退避重試 30/60/90/120 秒，不用管 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | macOS 系統 Python 沒 CA bundle | 裝 `certifi`（`batch_tts.py` 會用它） |
| **改完某週後「顯示中文釋義」按鈕不見了** | **重跑 `json_to_js.py` 把手工的 `zh` 全洗掉了** | **`git diff` 確認 → `git checkout -- <檔名>` 救回；之後遵守「先轉檔、後補 zh」的順序** |
| **首頁「今天」顯示的 W?/Day? 比老師快** | **`DAILY_PLAN.skipDates` 沒填放假日，假日照樣被算成上課日** | **把漏掉的國定假日／連假／段考週平日補進 `skipDates`，進度會自動退回正確位置** |
| 首頁一直顯示「📅 學期還沒開始」 | `DAILY_PLAN.startDate` 還停在未來，或忘了改成新學期 | 改 `startDate` 為該學期 W1 的星期一 |
| 首頁顯示「📦 W? 的單字還沒匯入」 | 算出來的週次在 `VOCAB_MANIFEST` 裡沒有（多半是複習週或忘了接） | 補那一週的資料，或把那一週的五個平日放進 `skipDates` 跳過 |
| 首頁「今天」抓的是上學期的字 | `DAILY_PLAN.semester` 沒改 | 改成新學期代號 |
| 換了同名音檔／icon，手機上還是舊的 | `sw.js` 對 `.m4a` / `.png` 走 cache-first | 改 `sw.js` 的 `CACHE` 版本號（`esl-vocab-v1` → `v2`） |

---

## 檔案速查

```
esl-vocab-practice/
├── index.html                  ← 主頁（SPA）；改 <script src> 載入清單
├── vocab_manifest.js           ← VOCAB_MANIFEST / VOCAB_DATA / EXAM_RANGES / DAILY_PLAN
├── shop_data.js                ← Avatar Shop 商品定義
├── sw.js                       ← Service worker：程式資料 network-first、音檔圖片 cache-first
├── manifest.json               ← PWA manifest（名稱、主題色、icon 登記）
├── favicon.ico                 ← make_icon.py 產出
├── CHANGELOG.md                ← 使用者看得到的更新紀錄（上線後補一筆）
├── README.md                   ← 專案總覽（對外）
├── 補單字音檔.command           ← 雙擊：批次補音檔 → 只 commit/push audio/
│
├── week12_data.js…week19_data.js              ← 2025 Fall（W12–W19，不要動）
├── spring2026_week01…21_data.js               ← 2026 Spring（缺 W10/W11/W18）
├── fall2026_week*.js                          ← 下學期會在這
│
├── audio/                      ← 發音 m4a（檔名 = 小寫單字；含 correct.m4a / try again.m4a）
├── icons/                      ← PWA icon（icon-192 / icon-512 / apple-touch-icon）
├── images/                     ← Avatar Shop 素材（角色、服裝、背景）
│   └── _raw/                   ← 生圖原始檔（gitignored）
│
└── tools/
    ├── pdf_to_vocab.py         ← ① PDF／照片 → JSON（Gemini OCR，--group N 處理跨頁週次）
    ├── json_to_js.py           ← ② JSON → *_data.js（重跑會保住既有的 zh）
    ├── sync_manifest.py        ← ③ 自動接線：script 標籤 + VOCAB_MANIFEST + VOCAB_DATA
    ├── batch_tts.py            ← ③ 產發音（直打 Gemini TTS API；撞每日配額乾淨中止、exit 2）
    ├── export_tts.py           ← ④ peek-dict 快取 WAV → afconvert → audio/*.m4a
    ├── gen_phrase_tts.py       ← UI 短語發音（Correct / Try again 這類非單字）
    ├── gen_item.py             ← Avatar 素材生圖（google-genai）
    ├── place_item.py           ← Avatar 素材對齊到 char_base（需要時自動 rembg 去背）
    ├── make_icon.py            ← 合成 PWA / iOS icon 與 favicon
    ├── check_coverage.py       ← ⑥ 完整性檢查：字數／中文／音檔（缺就 exit 1）
    ├── test_dailyplan.js       ← DAILY_PLAN 週次運算的斷言測試（node 跑）
    ├── test_zh_preserve.py     ← 驗證重跑 json_to_js.py 不會洗掉 zh
    ├── backfill_category.py    ← 一次性：為 2025 Fall 舊資料補 category（已跑過，不用再跑）
    ├── ocr_output/             ← OCR 暫存（gitignored）
    └── manifest_snippet.txt    ← manifest 片段，每次轉檔會覆蓋（gitignored）
```
