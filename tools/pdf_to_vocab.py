#!/usr/bin/env python3
"""
pdf_to_vocab.py — 把 ESL Vocabulary List PDF 轉成結構化 JSON。

每頁 = 一週，三欄表格固定為 Vocabulary / Picture / Definition and Example，
前 8 字屬 Reading、後 2 字屬 Science。

用法：
    # 單頁試跑（先跑 Week 1 確認品質）
    python3 pdf_to_vocab.py <pdf_path> --semester 2026-spring --start-week 1 --pages 1

    # 全部 19 頁
    python3 pdf_to_vocab.py <pdf_path> --semester 2026-spring --start-week 1
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

import pypdfium2 as pdfium

WORKSPACE = Path.home() / "Documents" / "KJ-agent"
TMP_DIR = Path.home() / ".gemini" / "tmp" / "kj-agent" / "esl_ocr"
RENDER_DPI = 200
PAGE_TIMEOUT = 120

PROMPT = """這是一張 ESL 兒童英文單字表的圖片。
表格分兩段：上半段標題 "Reading"（前 8 個字）、下半段標題 "Science"（後 2 個字）。
每列有三欄：Vocabulary（單字 + 詞性）、Picture、Definition and Example（定義 + 兩個例句）。

請輸出純 JSON 陣列（不要加 ```json 標記、不要解釋），每個元素格式：
{
  "n": 序號(1-10),
  "word": "單字（小寫，原樣）",
  "pos": "詞性符號，如 (n.)、(v.)、(adj.)、(adv.)、(prep)、(conj.)、(pronoun)",
  "category": "Reading 或 Science",
  "def": "定義（一行，去掉螢光標記）",
  "ex": "1. 第一句例句<br>2. 第二句例句"
}

注意事項：
- word 保留原拼字大小寫（通常全小寫，專有名詞除外）
- ex 兩句之間用 <br> 連接，不要換行
- 例句裡保留底線單字的原樣（不要加任何標記）
- 若某字有 (plural → xxx) 等補充，併入 def 末尾，例如 "...(plural → people)"
- 只輸出 JSON 陣列，不要多餘文字"""


def render_page(pdf_path: Path, page_idx: int, out_path: Path) -> None:
    doc = pdfium.PdfDocument(str(pdf_path))
    page = doc[page_idx]
    scale = RENDER_DPI / 72
    bitmap = page.render(scale=scale, rotation=0)
    pil_img = bitmap.to_pil().convert("L")
    pil_img.save(out_path)


def call_gemini(img_path: Path) -> str:
    prompt = f"@{img_path} {PROMPT}"
    result = subprocess.run(
        ["gemini", "-p", prompt, "-o", "text"],
        capture_output=True,
        text=True,
        timeout=PAGE_TIMEOUT,
        cwd=str(WORKSPACE),
    )
    if result.returncode != 0:
        raise RuntimeError(f"gemini exit {result.returncode}: {result.stderr.strip()}")
    out = result.stdout
    out = "\n".join(l for l in out.splitlines() if not l.startswith("Loaded cached"))
    return out.strip()


def parse_json_response(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    m = re.search(r"\[[\s\S]*\]", text)
    if not m:
        raise ValueError(f"找不到 JSON 陣列，原始輸出前 300 字：\n{text[:300]}")
    return json.loads(m.group(0))


def process_pdf(
    pdf_path: Path,
    semester: str,
    start_week: int,
    page_limit: int | None,
    out_dir: Path,
) -> list[dict[str, Any]]:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = pdfium.PdfDocument(str(pdf_path))
    n_pages = len(doc) if page_limit is None else min(page_limit, len(doc))
    print(f"[OCR] {pdf_path.name}：共 {len(doc)} 頁，本次處理 {n_pages} 頁")

    session = uuid.uuid4().hex[:8]
    all_weeks: list[dict[str, Any]] = []

    for i in range(n_pages):
        week = start_week + i
        img_path = TMP_DIR / f"{session}_w{week:02d}.png"
        try:
            render_page(pdf_path, i, img_path)
            print(f"[OCR] Week {week}：呼叫 Gemini …")
            raw = call_gemini(img_path)
            entries = parse_json_response(raw)
            if len(entries) != 10:
                print(f"  ⚠️ Week {week} 解析出 {len(entries)} 筆（預期 10），請檢查")
            week_obj = {
                "semester": semester,
                "week": week,
                "words": entries,
            }
            all_weeks.append(week_obj)

            per_week = out_dir / f"{semester}_week{week:02d}.json"
            per_week.write_text(
                json.dumps(week_obj, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  ✅ Week {week}：{len(entries)} 筆 → {per_week.name}")
        except Exception as e:
            print(f"  ❌ Week {week} 失敗：{e}")
        finally:
            if img_path.exists():
                img_path.unlink()

    combined = out_dir / f"{semester}_all.json"
    combined.write_text(
        json.dumps(all_weeks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n[完成] 共 {len(all_weeks)} 週，彙整：{combined}")
    return all_weeks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--semester", required=True, help="例：2026-spring")
    ap.add_argument("--start-week", type=int, default=1)
    ap.add_argument("--pages", type=int, default=None, help="只處理前 N 頁，省略則跑完")
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).parent / "ocr_output",
    )
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"找不到 PDF：{args.pdf}", file=sys.stderr)
        return 1

    process_pdf(
        pdf_path=args.pdf,
        semester=args.semester,
        start_week=args.start_week,
        page_limit=args.pages,
        out_dir=args.out_dir,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
