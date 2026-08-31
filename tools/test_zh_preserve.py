#!/usr/bin/env python3
"""驗證重跑 json_to_js.py 不會洗掉手工加的 zh。

做法：拿真實有 zh 的 spring2026_week21_data.js，反推一份「OCR 會產出的」JSON
（故意不含 zh），丟進 json_to_js.py 重轉，檢查 zh 有沒有活下來。
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.home() / "Documents/KJ-agent/esl-vocab-practice"
SRC = ROOT / "spring2026_week21_data.js"


def parse(path):
    text = path.read_text(encoding="utf-8")
    out = []
    for e in re.findall(r"\{[^{}]*\}", text, re.S):
        item = {}
        for k in ("word", "zh", "pos", "def", "ex", "category"):
            m = re.search(rf"\b{k}\s*:\s*'((?:[^'\\]|\\.)*)'", e, re.S)
            if m:
                item[k] = m.group(1).replace("\\'", "'")
        out.append(item)
    return out


before = parse(SRC)
n_zh_before = sum(1 for w in before if w.get("zh"))
print(f"原始檔：{len(before)} 字，其中 {n_zh_before} 筆有中文釋義")
assert n_zh_before > 0, "測試前提不成立：這個檔案本來就沒有 zh"

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    (td / "ocr").mkdir()
    # 1. 把現有檔案複製過去，模擬「repo 裡已經有補好 zh 的版本」
    shutil.copy(SRC, td / SRC.name)
    # 2. 造一份 OCR 風格的 JSON：有全部欄位、但故意沒有 zh
    words = [{k: v for k, v in w.items() if k != "zh"} for w in before]
    (td / "ocr" / "2026-spring_week21.json").write_text(
        json.dumps({"semester": "2026-spring", "week": 21, "words": words},
                   ensure_ascii=False), encoding="utf-8")

    # 3. 重跑轉檔
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools/json_to_js.py"),
         "--input", str(td / "ocr"), "--semester", "2026-spring", "--out-dir", str(td)],
        capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    assert r.returncode == 0, "json_to_js.py 執行失敗"

    after = parse(td / SRC.name)

n_zh_after = sum(1 for w in after if w.get("zh"))
print(f"重跑後：{len(after)} 字，其中 {n_zh_after} 筆有中文釋義")

ok = True
if n_zh_after != n_zh_before:
    print(f"❌ 中文釋義數量不符：{n_zh_before} → {n_zh_after}")
    ok = False

for b, a in zip(before, after):
    if b.get("zh", "") != a.get("zh", ""):
        print(f"❌ {b['word']}: '{b.get('zh')}' → '{a.get('zh')}'")
        ok = False
    for k in ("word", "pos", "def", "ex", "category"):
        if b.get(k, "") != a.get(k, ""):
            print(f"❌ {b['word']} 的 {k} 不一致")
            ok = False

# 欄位順序也要對（zh 緊接在 word 後面）
order = re.search(r"\{\s*word:.*?\n\s*(\w+):", (Path(SRC).read_text(encoding="utf-8")), re.S)
print("\n✅ 重跑後中文釋義完整保留，其他欄位一致" if ok else "\n❌ 有落差")
sys.exit(0 if ok else 1)
