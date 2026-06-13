"""
用 Gemini 圖像模型生一張「換裝物件」原始 PNG，存到 images/_raw/<name>.png。
生完用 place_item.py 對齊到 char_base 即可。

用法:
    python gen_item.py <name> "<物件描述>"

範例:
    python gen_item.py round_glasses "a pair of cute round eyeglasses with thin gold frames, clear lenses"

說明:
    - API key 從 ~/.gemini/.env 讀 (GEMINI_API_KEY 或 GOOGLE_API_KEY)
    - 統一套用 char_base 的 3D chibi 軟萌渲染風格 + 純色背景 (交給 rembg 去背)
    - 物件單獨置中、無角色、無陰影，方便 place_item.py 裁切對齊
"""
import os
import sys
from pathlib import Path

from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash-image"

STYLE = (
    "3D rendered, soft smooth shading, cute kawaii toy style, Pixar-like soft "
    "studio lighting, glossy pastel colors. A single isolated object only, "
    "no person, no character, no hands, no body. Centered, front view, "
    "no drop shadow, on a plain flat solid light grey (#cccccc) background. "
    "High detail product render."
)


def load_key() -> str:
    env = Path.home() / ".gemini" / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
                if line.startswith(k + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        if os.environ.get(k):
            return os.environ[k]
    raise SystemExit("❌ 找不到 GEMINI_API_KEY / GOOGLE_API_KEY")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    name = sys.argv[1]
    desc = sys.argv[2]
    out = Path("images/_raw") / f"{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    client = genai.Client(api_key=load_key())
    prompt = f"{desc}. {STYLE}"
    print(f"🎨 生圖中: {name}\n   prompt: {desc}")

    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )

    saved = False
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            out.write_bytes(part.inline_data.data)
            saved = True
            break
    if not saved:
        raise SystemExit(f"❌ 回應沒有影像資料: {resp.candidates[0].content.parts}")
    print(f"✅ 已存 {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
