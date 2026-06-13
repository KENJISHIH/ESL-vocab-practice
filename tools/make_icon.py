"""
合成 PWA / iOS 加到主畫面用的 app icon。
產出 icons/icon-512.png、icon-192.png、apple-touch-icon.png(180)、favicon.ico。

用法:
    python tools/make_icon.py                                   # 素顏站姿（cyan 漸層底 + 白圓）
    python tools/make_icon.py images/outfit_princess.png images/bg_castle.png   # 場景模式（換裝 + 背景）

設計：
    - 預設模式：主題 cyan 軟漸層底 + 白色圓襯底 + char_base 角色置中
    - 場景模式：背景圖填滿 + 角色身後加柔光暈分離 + 換裝全身圖置中
iOS 會自動套圓角遮罩，所以這裡輸出滿版方形。
"""
import sys
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

TOP = (77, 208, 225)      # #4dd0e1 淺 cyan
BOTTOM = (38, 198, 218)    # #26c6da 主題 cyan
MASTER = 1024


def gradient(size, top, bottom):
    base = Image.new("RGB", (1, size), top)
    for y in range(size):
        t = y / (size - 1)
        base.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return base.resize((size, size))


def fit_char(char_path: str, frac: float) -> Image.Image:
    char = Image.open(char_path).convert("RGBA")
    bbox = char.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    char = char.crop(bbox)
    target = int(MASTER * frac)
    ratio = min(target / char.width, target / char.height)
    return char.resize((int(char.width * ratio), int(char.height * ratio)), Image.LANCZOS)


def build_master(outfit: str | None = None, bg: str | None = None) -> Image.Image:
    if outfit and bg:
        # 場景模式：背景填滿 + 角色身後柔光暈 + 換裝全身圖
        canvas = Image.open(bg).convert("RGBA").resize((MASTER, MASTER), Image.LANCZOS)
        char = fit_char(outfit, 0.58)
        x = (MASTER - char.width) // 2
        y = (MASTER - char.height) // 2 + int(MASTER * 0.03)
        # 柔光暈：取角色 alpha 放大模糊成白色光，墊在角色後面分離背景
        glow = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
        halo = Image.new("RGBA", char.size, (255, 255, 255, 0))
        halo.putalpha(char.getchannel("A").point(lambda v: int(v * 0.55)))
        glow.alpha_composite(halo, (x, y))
        glow = glow.filter(ImageFilter.GaussianBlur(MASTER * 0.03))
        canvas.alpha_composite(glow)
        canvas.alpha_composite(char, (x, y))
        return canvas

    # 預設模式：cyan 漸層底 + 白圓襯底 + char_base
    canvas = gradient(MASTER, TOP, BOTTOM).convert("RGBA")
    d = ImageDraw.Draw(canvas)
    pad = int(MASTER * 0.12)
    d.ellipse([pad, pad, MASTER - pad, MASTER - pad], fill=(255, 255, 255, 235))
    char = fit_char("images/char_base.png", 0.62)
    x = (MASTER - char.width) // 2
    y = (MASTER - char.height) // 2 + int(MASTER * 0.04)
    canvas.alpha_composite(char, (x, y))
    return canvas


def main():
    outfit = sys.argv[1] if len(sys.argv) > 1 else None
    bg = sys.argv[2] if len(sys.argv) > 2 else None
    master = build_master(outfit, bg)
    out = Path("icons")
    out.mkdir(exist_ok=True)

    for name, size in [("icon-512.png", 512), ("icon-192.png", 192), ("apple-touch-icon.png", 180)]:
        master.resize((size, size), Image.LANCZOS).convert("RGB").save(out / name)
        print(f"✅ icons/{name} ({size}x{size})")

    fav = master.resize((64, 64), Image.LANCZOS).convert("RGB")
    fav.save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("✅ favicon.ico")


if __name__ == "__main__":
    main()
