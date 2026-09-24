#!/usr/bin/env python3
"""驗證重跑 json_to_js.py 不會洗掉手工抄的 keys（老師紅圈關鍵字）。

做法同 test_zh_preserve.py：拿有 keys 的 fall2026_week01_data.js，反推一份 OCR 風格
JSON（沒有 keys），丟進 json_to_js.py 重轉，檢查每個字的 keys 原封不動。
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.home() / "Documents/KJ-agent/esl-vocab-practice"
SRC = ROOT / "fall2026_week01_data.js"


def parse(path):
    out = []
    for e in re.findall(r"\{[^{}]*\}", path.read_text(encoding="utf-8"), re.S):
        item = {}
        for k in ("word", "zh", "pos", "def", "ex", "category"):
            m = re.search(rf"\b{k}\s*:\s*'((?:[^'\\]|\\.)*)'", e, re.S)
            if m:
                item[k] = m.group(1).replace("\\'", "'")
        m = re.search(r"\bkeys\s*:\s*(\[[^\]]*\])", e)
        if m:
            item["keys"] = m.group(1)
        out.append(item)
    return out


before = parse(SRC)
n_before = sum(1 for w in before if w.get("keys"))
print(f"原始檔：{len(before)} 字，其中 {n_before} 筆有 keys")
assert n_before > 0, "測試前提不成立：這個檔案本來就沒有 keys"

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    (td / "ocr").mkdir()
    shutil.copy(SRC, td / SRC.name)
    words = [{k: v for k, v in w.items() if k != "keys"} for w in before]
    (td / "ocr" / "2026-fall_week1.json").write_text(
        json.dumps({"semester": "2026-fall", "week": 1, "words": words},
                   ensure_ascii=False), encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools/json_to_js.py"),
         "--input", str(td / "ocr"), "--semester", "2026-fall", "--out-dir", str(td)],
        capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    assert r.returncode == 0, "json_to_js.py 執行失敗"
    after = parse(td / SRC.name)

ok = len(before) == len(after)
for b, a in zip(before, after):
    if b != a:
        print(f"❌ {b.get('word')}: {b} → {a}")
        ok = False

print("\n✅ 重跑後 keys 完整保留，其他欄位一致" if ok else "\n❌ 有落差")
sys.exit(0 if ok else 1)
