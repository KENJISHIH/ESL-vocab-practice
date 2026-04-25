#!/usr/bin/env python3
"""
backfill_category.py — 為舊 2025 Fall 資料補上 category 欄位。

舊檔結構：
    {
        word: "...",
        pos: "...",
        def: "...",
        ex: "..."
    },
    // Science Category
    {
        word: "...",
        ...
    },

補完後每筆都會有 category: 'Reading' 或 'Science'，跟新檔格式一致。
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

OBJ_PATTERN = re.compile(
    r"(\{\s*word:[\s\S]*?ex:\s*\"[^\"]*\")(\s*\})",
    re.MULTILINE,
)

def insert_cat(text: str, cat: str) -> str:
    # 把 ex: "..."後的 } 替換成 ex: "...",\n        category: "X"\n    }
    def repl(m: re.Match) -> str:
        body, close = m.group(1), m.group(2)
        return f'{body},\n        category: "{cat}"\n    }}'
    return OBJ_PATTERN.sub(repl, text)

def backfill(file_path: Path) -> bool:
    text = file_path.read_text(encoding="utf-8")
    if "category:" in text:
        print(f"  [skip] {file_path.name} 已有 category")
        return False
    if "// Science" not in text:
        print(f"  [warn] {file_path.name} 沒有 // Science 標記，跳過")
        return False

    head, tail = text.split("// Science", 1)
    new_text = insert_cat(head, "Reading") + "// Science" + insert_cat(tail, "Science")
    file_path.write_text(new_text, encoding="utf-8")
    print(f"  ✅ {file_path.name}")
    return True

def main() -> int:
    files = sorted(REPO.glob("week*_data.js"))
    print(f"處理 {len(files)} 個檔案：")
    for f in files:
        backfill(f)
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
