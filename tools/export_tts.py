#!/usr/bin/env python3
"""peek-dict TTS 快取 → 練習網音檔匯出。

掃描站內所有 *_data.js 的單字，到「一查究竟」的 TTS 快取
（~/Library/Caches/com.kenjishih.peekdict/tts/，SHA256 檔名）反查
對應 WAV，afconvert 轉成 m4a（AAC 32kbps，約 1/8 大小）放進 audio/。

用法：
    python3 tools/export_tts.py            # 匯出快取裡有的，列出缺的
    python3 tools/export_tts.py --force    # 已存在的 m4a 也重轉

快取裡沒有的字：去「一查究竟」app 查一次該單字即會生成，再重跑本腳本。
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

CACHE_DIR = Path.home() / "Library/Caches/com.kenjishih.peekdict/tts"
SITE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = SITE_DIR / "audio"
# 對齊 peek-dict TTSCache.swift 的 key 公式（單字一律小寫）
KEY_FMT = "gemini|gemini-2.5-flash-preview-tts|Achernar|{word}|wav-pcm24k16mono-v1"


def all_words() -> list[str]:
    words = set()
    for f in sorted(SITE_DIR.glob("*_data.js")):
        words.update(
            m.lower() for m in re.findall(r"word:\s*['\"]([^'\"]+)['\"]", f.read_text())
        )
    return sorted(words)


def cached_wav(word: str) -> Path | None:
    key = KEY_FMT.format(word=word)
    hexname = hashlib.sha256(key.encode()).hexdigest()
    path = CACHE_DIR / f"{hexname}.wav"
    return path if path.exists() else None


def main() -> None:
    force = "--force" in sys.argv
    AUDIO_DIR.mkdir(exist_ok=True)

    exported, skipped, missing = [], [], []
    for word in all_words():
        wav = cached_wav(word)
        if wav is None:
            missing.append(word)
            continue
        dst = AUDIO_DIR / f"{word}.m4a"
        if dst.exists() and not force:
            skipped.append(word)
            continue
        subprocess.run(
            ["afconvert", "-f", "m4af", "-d", "aac", "-b", "32000", str(wav), str(dst)],
            check=True, capture_output=True,
        )
        exported.append(word)

    print(f"✅ 新匯出 {len(exported)}: {', '.join(exported) or '—'}")
    print(f"⏭️ 已存在 {len(skipped)}")
    print(f"❌ 快取無 {len(missing)}（去一查究竟查過再重跑即可補）")
    if missing:
        print("   " + ", ".join(missing))


if __name__ == "__main__":
    main()
