#!/usr/bin/env python3
"""批次產生例句 TTS（Edge TTS，en-US-JennyNeural），輸出到 audio/ex/。

單字音檔走 Gemini Achernar（batch_tts.py），但例句有 680 句，
preview TTS 模型 8 秒一句加每日上限跑不完，所以例句改用 Edge TTS：
免費、本機呼叫、語速可調（-25% 給三年級聽）。

檔名＝句子的 slug，必須與 index.html 的 exAudioPath() 完全一致：
    小寫 → 非 a-z0-9 換成 '-' → 去頭尾 '-' → 取前 80 字 → 再去尾 '-'
全站 680 句實測 slug 無碰撞（同一句共用同一檔）。

用法：
    python3 tools/gen_example_tts.py fall2026_week01_data.js   # 指定週
    python3 tools/gen_example_tts.py --all                     # 全站缺的都補
    python3 tools/gen_example_tts.py --all --force             # 已存在的也重做
"""
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent
EX_DIR = SITE_DIR / "audio" / "ex"
VOICE = "en-US-JennyNeural"
RATE = "-25%"
WORKERS = 4
EDGE_TTS = Path.home() / ".local/bin/edge-tts"

# ex 的值有單引號（內含 \' 逸出）也有雙引號兩種寫法，兩種都要吃
EX_RE = re.compile(r"""ex:\s*(['"])((?:\\.|(?!\1).)*)\1""")


def unescape(js_str: str) -> str:
    return re.sub(r"\\(.)", r"\1", js_str)


def slugify(sentence: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", sentence.lower()).strip("-")[:80].rstrip("-")


def split_examples(ex: str) -> list[str]:
    """依 <br> 切句並剝掉開頭的 1. 2. 編號（跟 index.html 的 splitExamples 同規則）"""
    parts = re.split(r"<br\s*/?>", ex, flags=re.I)
    return [s for s in (re.sub(r"^\s*\d+\s*\.\s*", "", p).strip() for p in parts) if s]


def sentences_in(path: Path) -> list[str]:
    out = []
    for m in EX_RE.finditer(path.read_text(encoding="utf-8")):
        out.extend(split_examples(unescape(m.group(2))))
    return out


def synthesize(sentence: str) -> tuple[str, bool, str]:
    dst = EX_DIR / f"{slugify(sentence)}.m4a"
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        mp3 = Path(tmp.name)
    try:
        subprocess.run(
            [str(EDGE_TTS), "--voice", VOICE, f"--rate={RATE}",
             "--text", sentence, "--write-media", str(mp3)],
            check=True, capture_output=True,
        )
        # 對齊單字音檔的格式：AAC 32kbps 單聲道
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp3), "-c:a", "aac", "-b:a", "32k",
             "-ac", "1", "-ar", "24000", str(dst)],
            check=True, capture_output=True,
        )
        return sentence, True, f"{dst.stat().st_size // 1024} KB"
    except subprocess.CalledProcessError as e:
        return sentence, False, (e.stderr or b"").decode()[-200:]
    finally:
        mp3.unlink(missing_ok=True)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    force = "--force" in args
    names = [a for a in args if not a.startswith("--")]
    if "--all" in args:
        files = sorted(f for f in SITE_DIR.glob("*_data.js") if f.name != "shop_data.js")
    else:
        files = [SITE_DIR / n for n in names]

    EX_DIR.mkdir(parents=True, exist_ok=True)
    wanted: list[str] = []
    seen: set[str] = set()
    for f in files:
        if not f.exists():
            sys.exit(f"找不到 {f}")
        for s in sentences_in(f):
            if s not in seen:
                seen.add(s)
                wanted.append(s)

    todo = [s for s in wanted if force or not (EX_DIR / f"{slugify(s)}.m4a").exists()]
    print(f"{len(files)} 個檔、{len(wanted)} 句，要產生 {len(todo)} 句（已有 {len(wanted) - len(todo)} 句）")

    done = failed = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for sentence, ok, info in pool.map(synthesize, todo):
            if ok:
                done += 1
                print(f"  ✅ [{done + failed}/{len(todo)}] {sentence[:55]} … {info}")
            else:
                failed += 1
                print(f"  ❌ {sentence[:55]} … {info}")

    total = sum(p.stat().st_size for p in EX_DIR.glob("*.m4a"))
    print(f"\n完成 {done} 句，失敗 {failed} 句")
    print(f"audio/ex/ 共 {len(list(EX_DIR.glob('*.m4a')))} 檔、{total / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
