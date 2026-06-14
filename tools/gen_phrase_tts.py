#!/usr/bin/env python3
"""產生 UI 短語的 Achernar 發音（例：Quiz 的 Correct / Try again），直接輸出到 audio/。

與 batch_tts.py 同款請求（Say: 前綴 + Achernar），但繞過「單字表」過濾，
讓非單字的 UI 短語也能有真人感語音。檔名要對齊 index.html 裡 speak() 算出的
路徑：audio/<text.trim().toLowerCase()>.m4a。

用法：
    python3 tools/gen_phrase_tts.py "Correct:correct" "Try again:try again"
    每個參數格式 "要唸的文字:輸出檔名（不含副檔名）"
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from batch_tts import api_key, synthesize, wrap_wav
from export_tts import AUDIO_DIR


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    key = api_key()
    for arg in sys.argv[1:]:
        if ":" not in arg:
            sys.exit(f'參數格式錯誤：{arg}（應為 "文字:檔名"）')
        text, stem = arg.split(":", 1)
        pcm = synthesize(text, key)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wrap_wav(pcm))
            wav = tmp.name
        dst = AUDIO_DIR / f"{stem}.m4a"
        subprocess.run(
            ["afconvert", "-f", "m4af", "-d", "aac", "-b", "32000", wav, str(dst)],
            check=True,
        )
        Path(wav).unlink(missing_ok=True)
        print(f"✅ {text!r} → {dst} ({dst.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
