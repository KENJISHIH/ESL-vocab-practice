#!/usr/bin/env python3
"""
json_to_js.py — 把 OCR 產出的 JSON 轉成 index.html 用的 JS 資料檔。

每週一個檔，輸出格式跟現有 weekNN_data.js 一致（陣列），
並另外產出 vocab_manifest_NEW.js 片段供合併進 manifest。

用法：
    python3 json_to_js.py --input ocr_output --semester 2026-spring --out-dir ../

會產出：
    spring2026_week01_data.js  (const spring2026Week1Data = [...])
    spring2026_week02_data.js
    ...
    manifest_snippet.txt        (要手動 append 到 vocab_manifest.js)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SEMESTER_VAR_PREFIX = {
    "2026-spring": "spring2026",
    "2026-fall":   "fall2026",
    "2025-spring": "spring2025",
    "2025-fall":   "fall2025",
}

SEMESTER_LABEL = {
    "2026-spring": "2026 Spring",
    "2026-fall":   "2026 Fall",
    "2025-spring": "2025 Spring",
    "2025-fall":   "2025 Fall",
}


def js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ").strip()


def existing_zh(path: Path) -> dict[str, str]:
    """從既有的 *_data.js 撈出 word → zh 對照。

    `zh` 是手工欄位，OCR 不會產。以前重跑本腳本會把整檔覆蓋、中文釋義全部消失；
    現在改成先把舊檔的 zh 讀回來，重跑就不會再洗掉了。
    """
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for entry in re.findall(r"\{[^{}]*\}", text, re.S):
        w = re.search(r"\bword\s*:\s*'((?:[^'\\]|\\.)*)'", entry)
        z = re.search(r"\bzh\s*:\s*'((?:[^'\\]|\\.)*)'", entry)
        if w and z:
            out[w.group(1).replace("\\'", "'")] = z.group(1)
    return out


def render_week_js(week_obj: dict, var_name: str, keep_zh: dict[str, str]) -> str:
    lines = [f"// {week_obj['semester']} Week {week_obj['week']}"]
    lines.append(f"const {var_name} = [")
    for w in week_obj["words"]:
        word = js_escape(w["word"])
        pos = js_escape(w["pos"])
        def_ = js_escape(w["def"])
        ex = js_escape(w["ex"])
        cat = js_escape(w.get("category", ""))
        # zh 優先吃 JSON 裡的，沒有就沿用舊檔（欄位順序比照手工慣例，放在 word 後面）
        zh = w.get("zh") or keep_zh.get(w["word"].strip(), "")
        lines.append("    {")
        lines.append(f"        word: '{word}',")
        if zh:
            lines.append(f"        zh: '{js_escape(zh)}',")
        lines.append(f"        pos: '{pos}',")
        lines.append(f"        def: '{def_}',")
        lines.append(f"        ex: '{ex}',")
        if cat:
            lines.append(f"        category: '{cat}',")
        lines.append("    },")
    lines.append("];")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True, help="ocr_output 目錄")
    ap.add_argument("--semester", required=True)
    ap.add_argument("--out-dir", type=Path, required=True, help="輸出資料夾（repo 根）")
    args = ap.parse_args()

    prefix = SEMESTER_VAR_PREFIX[args.semester]
    label = SEMESTER_LABEL[args.semester]

    in_dir = args.input
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(in_dir.glob(f"{args.semester}_week*.json"))
    if not files:
        print(f"[warn] 找不到 {args.semester}_week*.json")
        return 1

    manifest_lines: list[str] = []
    for fp in files:
        week_obj = json.loads(fp.read_text(encoding="utf-8"))
        week_n = week_obj["week"]
        var_name = f"{prefix}Week{week_n}Data"
        out_path = out_dir / f"{prefix}_week{week_n:02d}_data.js"
        keep_zh = existing_zh(out_path)          # 保住手工加的中文釋義
        out_path.write_text(render_week_js(week_obj, var_name, keep_zh), encoding="utf-8")
        kept = sum(1 for w in week_obj["words"]
                   if not w.get("zh") and keep_zh.get(w["word"].strip()))
        note = f"（沿用舊檔 {kept} 筆中文釋義）" if kept else ""
        print(f"  ✅ {out_path.name}  ({len(week_obj['words'])} 字){note}")
        manifest_lines.append(
            f"    {{ semester: '{args.semester}', semesterLabel: '{label}', "
            f"week: {week_n}, dataVar: '{var_name}', "
            f"scriptSrc: '{out_path.name}' }},"
        )

    snippet = (out_dir / "tools" / "manifest_snippet.txt")
    snippet.parent.mkdir(parents=True, exist_ok=True)
    snippet.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(f"\n[完成] manifest 片段：{snippet}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
