#!/usr/bin/env python3
"""把 repo 根目錄的 *_data.js 自動接進前端，取代三處手工同步。

以前新增一週要手動改三個地方，漏一個就出錯（而且 VOCAB_DATA 漏列的症狀
「Data missing for this week!」只有切到那一週才看得到）：

    1. index.html 的 <script src="...">      ← 順序還必須排在 vocab_manifest.js 之前
    2. vocab_manifest.js 的 VOCAB_MANIFEST
    3. vocab_manifest.js 的 VOCAB_DATA

這支腳本直接掃檔案系統重新產生這三塊，掃到什麼就接什麼。
（EXAM_RANGES 不碰——考試範圍要含哪幾週是人的判斷，不是檔案掃得出來的。）

用法：
    python3 tools/sync_manifest.py            # 實際寫入
    python3 tools/sync_manifest.py --check    # 只比對，有落差就 exit 1（給 CI／commit 前用）
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 檔名前綴 → (學期代號, 顯示名稱)。新學期要在這裡加一行。
SEMESTERS = [
    ("week",            "2025-fall",   "2025 Fall"),
    ("spring2026_week", "2026-spring", "2026 Spring"),
    ("fall2026_week",   "2026-fall",   "2026 Fall"),
    ("spring2027_week", "2027-spring", "2027 Spring"),
]

MARKERS = {
    "scripts":  ("<!-- DATA_SCRIPTS:START -->", "<!-- DATA_SCRIPTS:END -->"),
    "manifest": ("// VOCAB_MANIFEST:START", "// VOCAB_MANIFEST:END"),
    "data":     ("// VOCAB_DATA:START", "// VOCAB_DATA:END"),
}


def classify(name: str):
    """檔名 → (學期代號, 顯示名稱, 週次, 排序用的學期序)。最長前綴優先。"""
    best = None
    for order, (prefix, sem, label) in enumerate(SEMESTERS):
        if name.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
            m = re.search(r"week(\d+)_data\.js$", name)
            if m:
                best = (prefix, sem, label, int(m.group(1)), order)
    if not best:
        return None
    _, sem, label, week, order = best
    return sem, label, week, order


def data_var(path: Path) -> str | None:
    """從檔案裡讀出真正的變數名，不用檔名猜（避免補零／不補零的落差）。"""
    m = re.search(r"^\s*const\s+(\w+)\s*=\s*\[", path.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


# 命名上也是 *_data.js，但不是單字資料
NOT_VOCAB = {"shop_data.js"}


def collect():
    entries = []
    for p in sorted(ROOT.glob("*_data.js")):
        if p.name in NOT_VOCAB:
            continue
        info = classify(p.name)
        if not info:
            print(f"  ⚠️  略過無法歸類的檔案：{p.name}")
            continue
        sem, label, week, order = info
        var = data_var(p)
        if not var:
            print(f"  ⚠️  {p.name} 找不到 `const xxxData = [`，略過")
            continue
        entries.append({"file": p.name, "semester": sem, "label": label,
                        "week": week, "var": var, "order": order})
    entries.sort(key=lambda e: (e["order"], e["week"]))
    return entries


def render_scripts(entries) -> str:
    lines = []
    last = None
    for e in entries:
        if e["label"] != last:
            lines.append(f"    <!-- {e['label']} -->")
            last = e["label"]
        lines.append(f'    <script src="{e["file"]}"></script>')
    return "\n".join(lines)


def render_manifest(entries) -> str:
    lines = ["const VOCAB_MANIFEST = ["]
    last = None
    for e in entries:
        if e["label"] != last:
            lines.append(f"    // ─── {e['label']} ───")
            last = e["label"]
        lines.append(
            f"    {{ semester: '{e['semester']}', semesterLabel: '{e['label']}', "
            f"week: {e['week']}, dataVar: '{e['var']}', scriptSrc: '{e['file']}' }},")
    lines.append("];")
    return "\n".join(lines)


def render_data(entries) -> str:
    lines = ["// 顯式 registry：頂層 const 不會自動掛上 window，要列名稱抓進來",
             "const VOCAB_DATA = {"]
    last = None
    for e in entries:
        if e["label"] != last:
            lines.append(f"    // {e['label']}")
            last = e["label"]
        lines.append(f"    {e['var']},")
    lines.append("};")
    return "\n".join(lines)


def splice(text: str, kind: str, body: str, path: Path) -> str:
    start, end = MARKERS[kind]
    if start not in text or end not in text:
        sys.exit(f"❌ {path.name} 找不到標記 {start} / {end}，請先手動加上")
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{start}\n{body}\n{end}{tail}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只比對不寫入，有落差 exit 1")
    args = ap.parse_args()

    entries = collect()
    if not entries:
        sys.exit("❌ 找不到任何 *_data.js")

    index_path = ROOT / "index.html"
    manifest_path = ROOT / "vocab_manifest.js"

    new_index = splice(index_path.read_text(encoding="utf-8"),
                       "scripts", render_scripts(entries), index_path)
    mtext = manifest_path.read_text(encoding="utf-8")
    mtext = splice(mtext, "manifest", render_manifest(entries), manifest_path)
    new_manifest = splice(mtext, "data", render_data(entries), manifest_path)

    changes = []
    if new_index != index_path.read_text(encoding="utf-8"):
        changes.append(index_path)
    if new_manifest != manifest_path.read_text(encoding="utf-8"):
        changes.append(manifest_path)

    by_sem: dict[str, list[int]] = {}
    for e in entries:
        by_sem.setdefault(e["label"], []).append(e["week"])
    for label, weeks in by_sem.items():
        print(f"  {label}: {len(weeks)} 週 (W{min(weeks)}–W{max(weeks)})")
    print(f"  合計 {len(entries)} 週")

    if args.check:
        if changes:
            print("\n❌ 前端接線與檔案系統不一致："
                  + "、".join(p.name for p in changes))
            print("   跑 `python3 tools/sync_manifest.py` 重新產生")
            return 1
        print("\n✅ 前端接線與檔案系統一致")
        return 0

    if not changes:
        print("\n✅ 已經是最新，沒有變更")
        return 0

    index_path.write_text(new_index, encoding="utf-8")
    manifest_path.write_text(new_manifest, encoding="utf-8")
    print("\n✅ 已更新：" + "、".join(p.name for p in changes))
    print("   記得跑 node tools/test_dailyplan.js 與 python3 tools/check_coverage.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
