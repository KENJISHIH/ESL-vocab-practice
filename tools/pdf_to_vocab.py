#!/usr/bin/env python3
"""
pdf_to_vocab.py — 把 ESL Vocabulary List PDF 轉成結構化 JSON。

每頁 = 一週，三欄表格固定為 Vocabulary / Picture / Definition and Example，
前 8 字屬 Reading、後 2 字屬 Science。

用法：
    # PDF：全部頁
    python3 pdf_to_vocab.py <pdf_path> --semester 2026-spring

    # PDF：試跑前 N 頁 / 從第 X 頁開始（用於失敗單頁重跑）
    python3 pdf_to_vocab.py <pdf_path> --semester 2026-spring --pages 3
    python3 pdf_to_vocab.py <pdf_path> --semester 2026-spring --start-page 10 --pages 1

    # 照片：直接吃 HEIC / JPG / PNG（2026 Fall 的單字本是手機翻拍，不是掃描 PDF）
    python3 pdf_to_vocab.py IMG_3070.HEIC IMG_3071.HEIC --semester 2026-fall
    python3 pdf_to_vocab.py "單字本/"*.HEIC --semester 2026-fall

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
from typing import Any, Callable

import pypdfium2 as pdfium
from PIL import Image, ImageOps

WORKSPACE = Path.home() / "Documents" / "KJ-agent"
TMP_DIR = Path.home() / ".gemini" / "tmp" / "kj-agent" / "esl_ocr"
RENDER_DPI = 200
PAGE_TIMEOUT = 120

# 手機翻拍原圖有 4000px 以上，縮到長邊這個尺寸就夠 Gemini 看清楚，也省 token
MAX_EDGE = 2000
IMAGE_EXTS = {".heic", ".heif", ".jpg", ".jpeg", ".png", ".webp"}

PROMPT = """以下是 ESL 兒童英文單字表的頁面（可能是掃描檔，也可能是手機翻拍）。
**如果給了不只一張圖，它們是同一週的連續頁面**，請合併成一週再輸出：
第一頁通常有頁首與前幾個字，後續頁接著剩下的字與 Science 段落。

請先判斷：這些頁面合起來是否構成「單一週次的詳細單字表」？
合格的特徵：
- 頁首寫著類似 "2026 Fall Semester Week N Vocabulary & Definition" 或
  "ESL Vocabulary List ... Week N" 的標題（ESL1 / ESL2 都算）
- 內容是表格，分 Reading 與 Science 兩段，合計 10 個字（編號 1–10）
- 每筆有 Vocabulary（單字+詞性）、Picture、Definition and Example 三欄

不合格（要回傳 SKIP）：
- 跨週概覽 / spelling 總表 / Review & Final Exam 頁
- 封面、目錄、空白頁、其他非單字表頁面

頁面上可能有小孩用螢光筆、紅筆畫的圈記與手寫註記，**那些都不是原文，請忽略**，
只抓印刷體的內容。

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
- n 依表格上的編號 1–10，Reading 與 Science 連號不重新計數
- category 依該字在表格中屬於 "Reading" 還是 "Science" 段落來判斷，不要用數量推測
- ex 是表格裡的 "E.g." 例句，請去掉 "E.g." 改成編號：'1. 第一句<br>2. 第二句'
- 例句裡保留底線單字原樣，不要加標記
- 若某字有 (plural → xxx) 等補充，併入 def 末尾"""


def render_page(pdf_path: Path, page_idx: int, out_path: Path) -> None:
    doc = pdfium.PdfDocument(str(pdf_path))
    page = doc[page_idx]
    scale = RENDER_DPI / 72
    bitmap = page.render(scale=scale, rotation=0)
    pil_img = bitmap.to_pil().convert("L")
    pil_img.save(out_path)


def render_photo(src: Path, out_path: Path) -> None:
    """手機翻拍照（含 iPhone HEIC）→ PNG。

    HEIC 用 macOS 內建的 sips 轉，免裝 pillow-heif。保留彩色（螢光標記靠顏色
    才分得出來），只把長邊縮到 MAX_EDGE。
    """
    tmp_jpg = None
    if src.suffix.lower() in {".heic", ".heif"}:
        tmp_jpg = out_path.with_suffix(".src.jpg")
        subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "90",
             str(src), "--out", str(tmp_jpg)],
            capture_output=True, check=True,
        )
        img = Image.open(tmp_jpg)
    else:
        img = Image.open(src)

    img = ImageOps.exif_transpose(img)          # 照片的方向 metadata
    if max(img.size) > MAX_EDGE:
        img.thumbnail((MAX_EDGE, MAX_EDGE))
    img.convert("RGB").save(out_path)
    img.close()
    if tmp_jpg and tmp_jpg.exists():
        tmp_jpg.unlink()


def call_gemini(img_paths: list[Path]) -> str:
    refs = " ".join(f"@{p}" for p in img_paths)
    prompt = f"{refs} {PROMPT}"
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


def process_sources(
    sources: list[tuple[str, list[Callable[[Path], None]]]],
    semester: str,
    out_dir: Path,
) -> list[dict[str, Any]]:
    """sources 是 (標籤, 產生 PNG 的函式清單)；一組頁面合併成一次 Gemini 呼叫。

    2026 Fall 的單字本一週跨兩頁（第二頁沒有 Week 標題），所以必須整組一起送，
    Gemini 才看得到週次、也才拼得出完整的 10 個字。
    """
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    n_pages = sum(len(g) for _, g in sources)
    print(f"[OCR] 本次處理 {n_pages} 頁，分成 {len(sources)} 組（每組 = 一週 = 一次 Gemini 呼叫）")
    print('      週次由 Gemini 從頁首 "Week N" 抓出；非單字頁會自動跳過')

    session = uuid.uuid4().hex[:8]
    all_weeks: list[dict[str, Any]] = []
    skipped: list[tuple[str, str]] = []

    for idx, (label, makers) in enumerate(sources, 1):
        img_paths = [TMP_DIR / f"{session}_{idx:03d}_{j}.png" for j in range(len(makers))]
        try:
            for make_png, p in zip(makers, img_paths):
                make_png(p)
            print(f"[OCR] ({idx}/{len(sources)}) {label}：呼叫 Gemini …")
            obj = parse_response(call_gemini(img_paths))
            week = int(obj["week"])
            entries = obj["words"]
            if len(entries) != 10:
                print(f"  ⚠️ {label}（Week {week}）解析出 {len(entries)} 筆（預期 10）")
            week_obj = {
                "semester": semester,
                "week": week,
                "source_page": label,
                "words": entries,
            }
            all_weeks.append(week_obj)

            per_week = out_dir / f"{semester}_week{week:02d}.json"
            if per_week.exists():
                print(f"  ⚠️ {per_week.name} 已存在，覆寫（同一週被掃到兩次？）")
            per_week.write_text(
                json.dumps(week_obj, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  ✅ {label} → Week {week}（{len(entries)} 筆）→ {per_week.name}")
        except SkipPage as e:
            skipped.append((label, str(e)))
            print(f"  ⏭  {label} 跳過：{e}")
        except Exception as e:
            print(f"  ❌ {label} 失敗：{e}")
        finally:
            for p in img_paths:
                if p.exists():
                    p.unlink()

    combined = out_dir / f"{semester}_all.json"
    combined.write_text(
        json.dumps(all_weeks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n[完成] 收 {len(all_weeks)} 週、跳過 {len(skipped)} 頁，彙整：{combined.name}")
    if skipped:
        print("  跳過的頁：")
        for p, r in skipped:
            print(f"    - {p}: {r}")
    print(f"  收進的週次：{sorted({w['week'] for w in all_weeks})}")
    return all_weeks


def build_sources(paths: list[Path], start_page: int, page_limit: int | None, group: int):
    """把命令列給的檔案展開成 (標籤, 產生 PNG 的函式清單)，每 group 頁併成一組。"""
    pages: list[tuple[str, Callable[[Path], None]]] = []

    pdfs = [p for p in paths if p.suffix.lower() == ".pdf"]
    images = [p for p in paths if p.suffix.lower() in IMAGE_EXTS]
    for p in paths:
        if p not in pdfs and p not in images:
            print(f"⚠️  略過不支援的檔案格式：{p.name}", file=sys.stderr)

    for pdf_path in pdfs:
        total = len(pdfium.PdfDocument(str(pdf_path)))
        start_idx = start_page - 1
        end_idx = total if page_limit is None else min(start_idx + page_limit, total)
        for i in range(start_idx, end_idx):
            pages.append((
                f"{pdf_path.name} p{i + 1}",
                lambda out, _p=pdf_path, _i=i: render_page(_p, _i, out),
            ))

    for img in images:
        pages.append((img.name, lambda out, _s=img: render_photo(_s, out)))

    grouped: list[tuple[str, list[Callable[[Path], None]]]] = []
    for i in range(0, len(pages), group):
        chunk = pages[i:i + group]
        label = chunk[0][0] if len(chunk) == 1 else f"{chunk[0][0]} + {len(chunk) - 1} 頁"
        grouped.append((label, [fn for _, fn in chunk]))
    return grouped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", type=Path, nargs="+",
                    help="PDF 檔，或一到多張照片（HEIC / JPG / PNG）")
    ap.add_argument("--semester", required=True, help="例：2026-fall")
    ap.add_argument("--start-page", type=int, default=1, help="PDF 專用：從第幾頁開始（1-based）")
    ap.add_argument("--pages", type=int, default=None, help="PDF 專用：只處理 N 頁")
    ap.add_argument("--group", type=int, default=1,
                    help="幾頁算一週（2026 Fall 的單字本一週跨兩頁，用 --group 2）")
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).parent / "ocr_output",
    )
    args = ap.parse_args()

    missing = [p for p in args.sources if not p.exists()]
    if missing:
        for p in missing:
            print(f"找不到檔案：{p}", file=sys.stderr)
        return 1

    sources = build_sources(args.sources, args.start_page, args.pages, args.group)
    if not sources:
        print("沒有可處理的來源檔", file=sys.stderr)
        return 1

    process_sources(sources=sources, semester=args.semester, out_dir=args.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
