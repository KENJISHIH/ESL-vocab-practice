"""
用現成的 chibi 角色 char_base.png 合成 PWA / iOS 加到主畫面用的 app icon。
產出 icons/icon-512.png、icon-192.png、apple-touch-icon.png(180)、favicon.ico。

用法:
    python tools/make_icon.py

設計：主題 cyan 軟漸層底 + 白色圓襯底 + 角色置中（頭部留白）。
iOS 會自動套圓角遮罩，所以這裡輸出滿版方形。
"""
from PIL import Image, ImageDraw
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


def build_master() -> Image.Image:
    canvas = gradient(MASTER, TOP, BOTTOM).convert("RGBA")
    d = ImageDraw.Draw(canvas)

    # 白色圓襯底（半透明，柔和）
    pad = int(MASTER * 0.12)
    d.ellipse([pad, pad, MASTER - pad, MASTER - pad], fill=(255, 255, 255, 235))

    # 角色：裁掉透明邊 → 等比縮放 fit 進圓內 → 置中略偏下
    char = Image.open("images/char_base.png").convert("RGBA")
    bbox = char.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    char = char.crop(bbox)
    target = int(MASTER * 0.62)
    ratio = min(target / char.width, target / char.height)
    char = char.resize((int(char.width * ratio), int(char.height * ratio)), Image.LANCZOS)
    x = (MASTER - char.width) // 2
    y = (MASTER - char.height) // 2 + int(MASTER * 0.04)
    canvas.alpha_composite(char, (x, y))
    return canvas


def main():
    master = build_master()
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
