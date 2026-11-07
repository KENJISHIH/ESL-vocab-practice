#!/usr/bin/env python3
"""補「🔀 易混淆練習區」需要的音檔（Edge TTS，en-US-JennyNeural，語速 -25%，跟例句同一個聲音）。

要補兩種：
  1) 變化形單字（scratched、giggled…）→ audio/<單字小寫>.m4a   （原形多半已有 Achernar 音檔，只補缺的）
  2) 填入正解後的完整例句          → audio/ex/<句子 slug>.m4a （slug 規則同 gen_example_tts.py／index.html exAudioPath）

清單從 confusable_sets.js 抽（用 node 載入題庫，不靠正則猜）。冪等：已存在的跳過，--force 全部重做。
沒有音檔 iPad 會整個無聲（瀏覽器語音在非手勢內常被擋），所以新增題庫後一定要跑這支。

用法：
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 tools/gen_confusable_tts.py
    ... tools/gen_confusable_tts.py --force
    ... tools/gen_confusable_tts.py --dry-run     # 只列清單，不產生
需要：node、~/.local/bin/edge-tts（403 時先 `uv tool upgrade edge-tts`）、ffmpeg。
"""
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = SITE_DIR / "audio"
EX_DIR = AUDIO_DIR / "ex"
VOICE = "en-US-JennyNeural"
RATE = "-25%"
WORKERS = 4
EDGE_TTS = Path.home() / ".local/bin/edge-tts"

NODE_DUMP = r"""
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.argv[1];
let src = fs.readFileSync(path.join(root, 'confusable_sets.js'), 'utf8') + '\n';
src += fs.readFileSync(path.join(root, 'confusable.js'), 'utf8') + '\n';
src += 'this.__out = (() => { const words = new Set(), sents = new Set();'
    + ' CONFUSABLE_SETS.forEach(s => { s.words.forEach(w => { words.add(w.w); words.add(w.show); (w.forms||[]).forEach(f => words.add(f)); });'
    + ' s.questions.forEach(q => { words.add(q.a); sents.add(confFilledSentence(q)); }); });'
    + ' return { words: [...words], sentences: [...sents] }; })();';
// confusable.js 用到 dictation.js 的函式只在呼叫時才需要，這裡只用 confFilledSentence，不必載入
const ctx = {}; vm.createContext(ctx); vm.runInContext(src, ctx);
console.log(JSON.stringify(ctx.__out));
"""


def slugify(sentence: str) -> str:
    # 必須與 index.html 的 exAudioPath() 完全一致
    return re.sub(r"[^a-z0-9]+", "-", sentence.lower()).strip("-")[:80].rstrip("-")


def load_lists() -> tuple[list[str], list[str]]:
    out = subprocess.run(["node", "-e", NODE_DUMP, str(SITE_DIR)], check=True, capture_output=True, text=True).stdout
    data = json.loads(out)
    return sorted(data["words"], key=str.lower), data["sentences"]


def synthesize(text: str, dst: Path) -> tuple[str, bool, str]:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        mp3 = Path(tmp.name)
    try:
        subprocess.run(
            [str(EDGE_TTS), "--voice", VOICE, f"--rate={RATE}", "--text", text, "--write-media", str(mp3)],
            check=True, capture_output=True,
        )
        # 對齊既有音檔格式：AAC 32kbps 單聲道
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp3), "-c:a", "aac", "-b:a", "32k", "-ac", "1", "-ar", "24000", str(dst)],
            check=True, capture_output=True,
        )
        return text, True, f"{dst.stat().st_size // 1024} KB"
    except subprocess.CalledProcessError as e:
        return text, False, (e.stderr or b"").decode()[-200:]
    finally:
        mp3.unlink(missing_ok=True)


def main() -> None:
    force = "--force" in sys.argv
    dry = "--dry-run" in sys.argv
    words, sentences = load_lists()

    jobs: list[tuple[str, Path]] = []
    for w in words:
        dst = AUDIO_DIR / f"{w.strip().lower()}.m4a"
        if force or not dst.exists():
            jobs.append((w, dst))
    n_words = len(jobs)
    for s in sentences:
        dst = EX_DIR / f"{slugify(s)}.m4a"
        if force or not dst.exists():
            jobs.append((s, dst))
    n_sents = len(jobs) - n_words

    print(f"單字形式 {len(words)} 個（要補 {n_words}）、例句 {len(sentences)} 句（要補 {n_sents}）")
    if dry:
        for text, dst in jobs:
            print(f"  - {dst.relative_to(SITE_DIR)}  ←  {text}")
        return

    EX_DIR.mkdir(parents=True, exist_ok=True)
    done = failed = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for text, ok, info in pool.map(lambda j: synthesize(*j), jobs):
            if ok:
                done += 1
                print(f"  ✅ [{done + failed}/{len(jobs)}] {text[:60]} … {info}")
            else:
                failed += 1
                print(f"  ❌ {text[:60]} … {info}")
    print(f"\n完成 {done}，失敗 {failed}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
