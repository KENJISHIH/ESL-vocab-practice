#!/usr/bin/env python3
"""單字資料完整性檢查：字數、中文釋義、預錄音檔。

用法：
    python3 tools/check_coverage.py                # 檢查全部學期
    python3 tools/check_coverage.py 2026-fall      # 只檢查某個學期

離開碼 0 = 全部通過；1 = 有缺漏（可掛進 CI 或 commit 前自己跑一次）。

為什麼需要這支：
    OCR 只會產 word/pos/def/ex/category，`zh` 與音檔都是額外步驟，很容易匯完
    單字就以為做完了。與其靠記性，不如每次改完資料跑一次這支確認全綠。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT / "audio"

WORDS_PER_WEEK = 10          # 每天 2 個字 × 5 天，少於這個數每日模式會有空檔
FIELDS = ("word", "pos", "def", "ex", "category")

# 檔名前綴 → 學期代號
SEMESTER_OF_PREFIX = {
    "week": "2025-fall",
    "spring2026_week": "2026-spring",
    "fall2026_week": "2026-fall",
    "spring2027_week": "2027-spring",
}


def semester_of(filename: str) -> str:
    for prefix in sorted(SEMESTER_OF_PREFIX, key=len, reverse=True):
        if filename.startswith(prefix):
            return SEMESTER_OF_PREFIX[prefix]
    return "unknown"


def week_of(filename: str) -> int:
    m = re.search(r"week(\d+)_data\.js$", filename)
    return int(m.group(1)) if m else 0


def parse_words(path: Path) -> list[dict]:
    """從 *_data.js 逐筆抓出欄位（不求完整 JS 解析，夠用即可）。"""
    text = path.read_text(encoding="utf-8")
    body = text[text.index("["): text.rindex("]") + 1]
    out = []
    for entry in re.findall(r"\{[^{}]*\}", body, re.S):
        item = {}
        for key in FIELDS + ("zh",):
            m = re.search(rf"\b{key}\s*:\s*(['\"])(.*?)\1\s*(?:,|\}})", entry, re.S)
            if m:
                item[key] = m.group(2)
        out.append(item)
    return out


def main() -> None:
    want_semester = sys.argv[1] if len(sys.argv) > 1 else None
    audio = {p.stem.lower() for p in AUDIO_DIR.glob("*.m4a")} if AUDIO_DIR.is_dir() else set()

    files = sorted(ROOT.glob("*_data.js"), key=lambda p: (semester_of(p.name), week_of(p.name)))
    if want_semester:
        files = [f for f in files if semester_of(f.name) == want_semester]
        if not files:
            sys.exit(f"找不到學期 {want_semester} 的資料檔")

    problems = []
    current = None
    totals = {"n": 0, "zh": 0, "audio": 0}

    for f in files:
        sem = semester_of(f.name)
        if sem != current:
            print(f"\n=== {sem} ===")
            print(f"{'週次':<6} {'字數':>4} {'中文':>6} {'音檔':>6}  問題")
            print("-" * 62)
            current = sem

        words = parse_words(f)
        n = len(words)
        n_zh = sum(1 for w in words if w.get("zh"))
        missing_audio = [w.get("word", "?") for w in words
                         if w.get("word", "").strip().lower() not in audio]
        n_audio = n - len(missing_audio)

        notes = []
        if n != WORDS_PER_WEEK:
            notes.append(f"⚠️ 字數 {n}≠{WORDS_PER_WEEK}（每日模式會有空檔）")
            problems.append(f"{f.name}: 字數 {n}")
        for w in words:
            missing = [k for k in FIELDS if not w.get(k)]
            if missing:
                notes.append(f"⚠️ {w.get('word', '?')} 缺 {'/'.join(missing)}")
                problems.append(f"{f.name}: {w.get('word', '?')} 缺 {'/'.join(missing)}")
        if n_zh < n:
            problems.append(f"{f.name}: 缺 {n - n_zh} 筆中文釋義")
        if missing_audio:
            problems.append(f"{f.name}: 缺 {len(missing_audio)} 個音檔")

        mark = lambda got, tot: f"{got}/{tot}" + ("✅" if got == tot and tot else "")
        print(f"W{week_of(f.name):<5} {n:>4} {mark(n_zh, n):>6} {mark(n_audio, n):>6}  {' '.join(notes)}")

        totals["n"] += n
        totals["zh"] += n_zh
        totals["audio"] += n_audio

    t = totals
    pct = lambda got: f"{got * 100 // t['n']}%" if t["n"] else "-"
    print("\n" + "=" * 62)
    print(f"總計 {t['n']} 字 ｜ 中文 {t['zh']} ({pct(t['zh'])}) ｜ 音檔 {t['audio']} ({pct(t['audio'])})")

    if not problems:
        print("\n✅ 全部完整")
        return

    print(f"\n❌ 有 {len(problems)} 項待補：")
    for p in problems[:20]:
        print(f"   - {p}")
    if len(problems) > 20:
        print(f"   …另外 {len(problems) - 20} 項")
    print("\n補法：")
    print("   缺中文 → 加 zh 欄位（OCR JSON 或 *_data.js 都行，放在 word 後面）；")
    print("            json_to_js.py 重跑時會把既有的 zh 讀回來，不會洗掉")
    print("   缺音檔 → python3 tools/batch_tts.py <該週_data.js>，或雙擊 補單字音檔.command")
    print("   字數不足 → 回頭核對 OCR 結果，每週要剛好 10 個字")
    sys.exit(1)


if __name__ == "__main__":
    main()
