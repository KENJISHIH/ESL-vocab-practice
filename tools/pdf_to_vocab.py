#!/usr/bin/env python3
"""
pdf_to_vocab.py — 把 ESL Vocabulary List PDF 轉成結構化 JSON。

每頁 = 一週，三欄表格固定為 Vocabulary / Picture / Definition and Example，
前 8 字屬 Reading、後 2 字屬 Science。

用法：
    # 全部頁
    python3 pdf_to_vocab.py <pdf_path> --semester 2026-spring

    # 試跑前 N 頁
    python3 pdf_to_vocab.py <pdf_path> --semester 2026-spring --pages 3

    # 從第 X 頁開始（用於失敗單頁重跑）
    python3 pdf_to_vocab.py <pdf_path> --semester 2026-spring --start-page 10 --pages 1

週次由 Gemini 從頁首 "Week N" 自動抓出，不需手動指定。
非單字頁（概覽 / Review / 封面）會自動跳過。
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

PROMPT = """這是一張 ESL 兒童英文單字表的可能頁面。

請先判斷：這頁是否是「單一週次的詳細單字表」？
合格的頁面特徵：
- 頁首寫著類似 "ESL1 Vocabulary List ... Week N" 的標題
- 內容是表格形式，分 Reading 與 Science 兩段，列出 10 個字
- 每筆有 Vocabulary（單字+詞性）、Picture、Definition and Example 三欄

不合格的頁面（要回傳 SKIP）：
- 跨週概覽 / spelling 總表 / Review & Final Exam 頁
- 封面、目錄、空白頁、其他非單字表頁面

——————————————————————————————

如果是「不合格頁面」，只輸出一行：
SKIP: <一句話原因>

如果是「合格的單週單字表」，輸出純 JSON 物件（不要加 ```json 標記、不要解釋）：
{
  "week": 從頁首抓到的週次數字,
  "words": [
    {
      "n": 序號(1-10),
      "word": "單字（保留原拼字大小寫）",
      "pos": "詞性符號，如 (n.)、(v.)、(adj.)、(adv.)、(prep)、(conj.)、(pronoun)",
      "category": "Reading 或 Science",
      "def": "定義（一行，去掉螢光標記）",
      "ex": "1. 第一句例句<br>2. 第二句例句"
    }
  ]
}

注意：
- week 一定要從頁首實際看到的 "Week N" 抓出來，不要用推測的
- ex 兩句之間用 <br>，不要換行
- 例句裡保留底線單字原樣，不要加標記
- 若某字有 (plural → xxx) 等補充，併入 def 末尾"""


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


class SkipPage(Exception):
    """非單字頁，應跳過。"""


def parse_response(text: str) -> dict[str, Any]:
    """
    解析 Gemini 回應：
      - 若以 SKIP: 開頭 → 拋 SkipPage
      - 否則嘗試解析成 {"week": N, "words": [...]} 物件
    """
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    if text.lstrip().upper().startswith("SKIP"):
        # 取冒號後的原因
        reason = text.split(":", 1)[1].strip() if ":" in text else "non-vocab page"
        raise SkipPage(reason)

    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError(f"找不到 JSON 物件，原始輸出前 300 字：\n{text[:300]}")
    obj = json.loads(m.group(0))
    if "words" not in obj or not isinstance(obj["words"], list):
        raise ValueError(f"回應缺少 words 陣列：{obj}")
    return obj


def process_pdf(
    pdf_path: Path,
    semester: str,
    start_page: int,
    page_limit: int | None,
    out_dir: Path,
) -> list[dict[str, Any]]:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = pdfium.PdfDocument(str(pdf_path))
    total = len(doc)
    start_idx = start_page - 1  # 1-based → 0-based
    end_idx = total if page_limit is None else min(start_idx + page_limit, total)
    n_pages = end_idx - start_idx
    print(f"[OCR] {pdf_path.name}：共 {total} 頁，本次處理第 {start_page}–{end_idx} 頁（{n_pages} 頁）")
    print(f"      週次由 Gemini 從頁首 \"Week N\" 抓出；非單字頁會自動跳過")

    session = uuid.uuid4().hex[:8]
    all_weeks: list[dict[str, Any]] = []
    skipped: list[tuple[int, str]] = []

    for i in range(start_idx, end_idx):
        page_num = i + 1  # 1-based
        img_path = TMP_DIR / f"{session}_p{page_num:02d}.png"
        try:
            render_page(pdf_path, i, img_path)
            print(f"[OCR] 第 {page_num} 頁：呼叫 Gemini …")
            raw = call_gemini(img_path)
            obj = parse_response(raw)
            week = int(obj["week"])
            entries = obj["words"]
            if len(entries) != 10:
                print(f"  ⚠️ 第 {page_num} 頁（Week {week}）解析出 {len(entries)} 筆（預期 10）")
            week_obj = {
                "semester": semester,
                "week": week,
                "source_page": page_num,
                "words": entries,
            }
            all_weeks.append(week_obj)

            per_week = out_dir / f"{semester}_week{week:02d}.json"
            if per_week.exists():
                print(f"  ⚠️ {per_week.name} 已存在，覆寫（你可能跑了重複的 PDF？）")
            per_week.write_text(
                json.dumps(week_obj, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  ✅ 第 {page_num} 頁 → Week {week}（{len(entries)} 筆）→ {per_week.name}")
        except SkipPage as e:
            skipped.append((page_num, str(e)))
            print(f"  ⏭  第 {page_num} 頁跳過：{e}")
        except Exception as e:
            print(f"  ❌ 第 {page_num} 頁失敗：{e}")
        finally:
            if img_path.exists():
                img_path.unlink()

    combined = out_dir / f"{semester}_all.json"
    combined.write_text(
        json.dumps(all_weeks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n[完成] 收 {len(all_weeks)} 週、跳過 {len(skipped)} 頁，彙整：{combined.name}")
    if skipped:
        print("  跳過的頁：")
        for p, r in skipped:
            print(f"    - p{p:02d}: {r}")
    weeks_seen = sorted({w["week"] for w in all_weeks})
    print(f"  收進的週次：{weeks_seen}")
    return all_weeks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--semester", required=True, help="例：2026-spring")
    ap.add_argument("--start-page", type=int, default=1, help="從 PDF 第幾頁開始（1-based，預設 1）")
    ap.add_argument("--pages", type=int, default=None, help="只處理 N 頁，省略則從 start-page 跑到底")
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
        start_page=args.start_page,
        page_limit=args.pages,
        out_dir=args.out_dir,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
