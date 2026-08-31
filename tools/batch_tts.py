#!/usr/bin/env python3
"""批次產生單字 TTS：直打 Gemini API（Achernar），寫進 peek-dict 快取。

與「一查究竟」app 同款請求（Say: 前綴 + prebuiltVoiceConfig），產出的 WAV
以同一套 SHA256 key 存進 app 快取目錄 —— app 之後查同字也直接命中。
跑完自動呼叫 export_tts.py 轉 m4a 進 audio/。

用法：
    python3 tools/batch_tts.py spring2026_week17_data.js spring2026_week19_data.js
    python3 tools/batch_tts.py --all          # 全站所有還缺音檔的字

API key 讀 ~/.gemini/.env 的 GEMINI_API_KEY（paid tier；單字 token 極少費用可忽略）。
"""
import base64
import json
import re
import ssl
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import certifi

# 系統 Python 沒掛 CA bundle（macOS 經典雷），明確用 certifi 的
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

from export_tts import AUDIO_DIR, CACHE_DIR, KEY_FMT, SITE_DIR, all_words, cached_wav
import hashlib

MODEL = "gemini-2.5-flash-preview-tts"
VOICE = "Achernar"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
PACE_SEC = 8  # 請求間隔；preview TTS 模型 RPM 很低，3 秒實測會被 429 轟炸


class QuotaExhausted(Exception):
    """撞到每日請求上限（RPD）—— 再跑下去只是空燒，整批中止。"""


def is_daily_quota(body: str) -> bool:
    """從 429 回應內容判斷是「每日上限」還是「每分鐘節流」。

    Gemini 429 的 error.details 會帶 QuotaFailure，violation 的 quotaId /
    quotaMetric 形如 GenerateRequestsPerDayPerProjectPerModel（每日）或
    ...PerMinute...（短期節流）。只有前者要中止整批。
    """
    low = body.lower()
    return any(k in low for k in ("perday", "per_day", "per day", "daily limit"))


def api_key() -> str:
    for line in (Path.home() / ".gemini/.env").read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("找不到 GEMINI_API_KEY（~/.gemini/.env）")


def words_from_files(files: list[str]) -> list[str]:
    words = set()
    for name in files:
        f = SITE_DIR / name
        if not f.exists():
            sys.exit(f"找不到資料檔：{name}")
        words.update(
            m.lower() for m in re.findall(r"word:\s*['\"]([^'\"]+)['\"]", f.read_text())
        )
    return sorted(words)


def wrap_wav(pcm: bytes, rate: int = 24000) -> bytes:
    """裸 PCM（16-bit mono）補 RIFF header，對齊 peek-dict wav-pcm24k16mono-v1。"""
    return (
        b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt "
        + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16)
        + b"data" + struct.pack("<I", len(pcm)) + pcm
    )


def synthesize(word: str, key: str) -> bytes:
    body = json.dumps({
        "contents": [{"parts": [{"text": f"Say: {word}"}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
        },
    }).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as resp:
                payload = json.load(resp)
            b64 = payload["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            return base64.b64decode(b64)
        except (KeyError, IndexError):
            if attempt < 4:
                time.sleep(3)  # preview 模型間歇回空回應（無 content），重試
                continue
            raise RuntimeError("重試後回應仍無音訊")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                if is_daily_quota(e.read().decode("utf-8", "replace")):
                    raise QuotaExhausted("回應標示每日請求上限（RPD）已用完")
                if attempt < 4:
                    time.sleep(30 * (attempt + 1))  # 限流退避（30/60/90/120s）
                    continue
                # 保守判定：RPM 節流撐不過 30+60+90+120 秒的等待，還被擋就是配額沒了
                raise QuotaExhausted("429 重試 5 次仍被擋（等超過 300 秒），視同配額用完")
            if e.code == 500 and attempt < 4:
                time.sleep(3)  # Google 端暫時性錯誤（同 app 的重試邏輯）
                continue
            raise
    raise RuntimeError(f"{word}: 重試後仍失敗")


def store_in_cache(word: str, wav: bytes) -> None:
    hexname = hashlib.sha256(KEY_FMT.format(word=word).encode()).hexdigest()
    (CACHE_DIR / f"{hexname}.wav").write_bytes(wav)


def main() -> None:
    if "--all" in sys.argv:
        words = all_words()
    else:
        files = [a for a in sys.argv[1:] if not a.startswith("-")]
        if not files:
            sys.exit(__doc__)
        words = words_from_files(files)

    todo = [w for w in words if cached_wav(w) is None and not (AUDIO_DIR / f"{w}.m4a").exists()]
    print(f"目標 {len(words)} 字，其中 {len(todo)} 字需要產生（其餘已有快取或音檔）", flush=True)

    key = api_key()
    failed = []
    ok = 0
    quota_hit = False
    for i, word in enumerate(todo, 1):
        try:
            pcm = synthesize(word, key)
            store_in_cache(word, wrap_wav(pcm))
            ok += 1
            print(f"[{i}/{len(todo)}] ✅ {word}", flush=True)
        except QuotaExhausted as e:
            quota_hit = True
            print(f"\n⛔ 今日配額已用完（{word}: {e}）", flush=True)
            print(f"   本次已產生 {ok} 字，還剩 {len(todo) - i + 1} 字沒補", flush=True)
            print("   配額於太平洋時間午夜重置（約台北隔天 15:00 之後），"
                  "明天再跑一次就會接著補", flush=True)
            break
        except Exception as e:
            failed.append(word)
            print(f"[{i}/{len(todo)}] ❌ {word}: {e}", flush=True)
        time.sleep(PACE_SEC)

    if failed:
        print(f"\n失敗 {len(failed)}: {', '.join(failed)}（重跑本腳本會自動只補這些）")
    print("\n--- 轉檔 ---")
    subprocess.run([sys.executable, str(Path(__file__).parent / "export_tts.py")], check=True)
    if quota_hit:
        sys.exit(2)  # 給 補單字音檔.command 判斷用：因配額中止（音檔仍要 commit）


if __name__ == "__main__":
    main()
