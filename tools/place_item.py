"""
把 AI 生的原始物件 PNG 對齊到 char_base 對應位置，輸出 512x512 透明畫布。

用法:
    python place_item.py <preset> <input.png> [output.png]

範例:
    python place_item.py bottom images/_raw/blue_jeans.png images/bottom_blue_jeans.png
    python place_item.py shirt  images/_raw/galaxy_dress.png images/shirt_galaxy_dress.png

支援的 preset:
    shirt, bottom, shoes, hat, glasses, necklace, halo, wings, pet, bg

流程:
    1. 開啟原圖、轉 RGBA
    2. 自動裁掉透明邊緣 (getbbox)
    3. 等比縮放到 preset 指定寬高
    4. 貼到 512x512 透明畫布的指定中心
    5. 背景類 (bg) 直接 resize 填滿 512x512

char_base 量到的關鍵 y 座標 (512px 高度):
    頭頂 95 / 下巴 220 / 肩 250 / 腰 340 / 大腿頂 360 / 膝 430 / 腳底 508
"""
from PIL import Image
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

CANVAS = 512

# (cx, cy, max_w, max_h) — 物件中心點 + 最大寬高 (等比縮放)
# 對 char_base_short.png 校準 (中軸 x=263, 腰 y=370, 膝 y=420, 腳 y=490)
PRESETS = {
    "shirt":    (263, 305, 240, 200),  # 蓋胸+腰 + 袖子 (中心對齊背心中央)
    "bottom":   (263, 405, 110, 140),  # 腰到大腿中段 (capri/chibi 比例)
    "shoes":    (263, 495, 160, 100),  # 腳底 (cy 對齊腳踝)
    "hat":      (263,  90, 200, 130),  # 頭頂上方 (環狀冠/耳朵/皇冠)
    "glasses":  (263, 200, 150,  70),  # 眼睛位置
    "necklace": (263, 280, 130,  55),  # 脖子
    "halo":     (263,  70, 160,  45),  # 頭頂上方
    "wings":    (263, 320, 460, 280),  # 背後
    "pet":      (400, 460, 150, 160),  # 右下角
}


def needs_bg_removal(img: Image.Image) -> bool:
    """偵測是否為「假透明」(alpha 全滿、背景被畫進像素)"""
    alpha = img.getchannel("A")
    return alpha.getextrema()[0] > 250  # 最小 alpha > 250 → 沒有透明區域


def auto_remove_bg(src_path: Path) -> Path:
    """呼叫 rembg CLI 把背景去掉，回傳 tmp 檔路徑"""
    if not shutil.which("rembg"):
        raise SystemExit(
            "❌ 偵測到原圖背景不透明 (AI 生圖把棋盤格畫進像素了)，需要先去背。\n"
            "   請安裝 rembg：\n"
            "     uv tool install 'rembg[cpu]'\n"
            "   裝完再跑一次本指令。"
        )
    tmp = Path(tempfile.gettempdir()) / f"rembg_{src_path.stem}.png"
    print(f"   🪄 偵測到假透明，跑 rembg 去背中... (第一次會下載模型 ~170MB)")
    subprocess.run(["rembg", "i", str(src_path), str(tmp)], check=True)
    return tmp


def place(preset: str, src_path: Path, out_path: Path) -> None:
    img = Image.open(src_path).convert("RGBA")

    if preset == "bg":
        img.resize((CANVAS, CANVAS), Image.LANCZOS).save(out_path)
        print(f"✅ [bg] {src_path.name} → {out_path.name} (filled {CANVAS}x{CANVAS})")
        return

    if preset == "outfit":
        # outfit = 整套全身圖，對齊到 char_base.png 的 alpha bbox 同樣位置
        if needs_bg_removal(img):
            cleaned = auto_remove_bg(src_path)
            img = Image.open(cleaned).convert("RGBA")
        # 取 char_base.png 的 bbox 當對齊目標
        ref = Image.open("images/char_base.png").convert("RGBA")
        ref_alpha = ref.getchannel("A")
        ref_bbox = ref_alpha.point(lambda v: 255 if v > 32 else 0).getbbox()
        if ref_bbox is None:
            raise SystemExit("❌ char_base.png 無 alpha 內容")
        # 取本圖 bbox
        src_bbox = img.getchannel("A").point(lambda v: 255 if v > 32 else 0).getbbox()
        if src_bbox is None:
            raise SystemExit(f"❌ {src_path} 去背後完全空白")
        cropped = img.crop(src_bbox)
        target_w = ref_bbox[2] - ref_bbox[0]
        target_h = ref_bbox[3] - ref_bbox[1]
        # 等比縮放，fit 在 target box 內
        ratio = min(target_w / cropped.width, target_h / cropped.height)
        new_w = int(cropped.width * ratio)
        new_h = int(cropped.height * ratio)
        resized = cropped.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        # 置中於 ref_bbox
        cx = (ref_bbox[0] + ref_bbox[2]) // 2
        cy = (ref_bbox[1] + ref_bbox[3]) // 2
        canvas.paste(resized, (cx - new_w // 2, cy - new_h // 2), resized)
        canvas.save(out_path)
        print(f"✅ [outfit] {src_path.name} → {out_path.name}")
        print(f"   原圖 {img.size} → bbox {cropped.size} → 縮放 {(new_w, new_h)} → 對齊到 char_base bbox {ref_bbox}")
        return

    if preset not in PRESETS:
        raise SystemExit(f"❌ 未知 preset: {preset}. 可用: {', '.join(PRESETS)}, bg, outfit")

    cx, cy, max_w, max_h = PRESETS[preset]

    # 先檢查是不是「假透明」，是的話跑 rembg
    if needs_bg_removal(img):
        cleaned = auto_remove_bg(src_path)
        img = Image.open(cleaned).convert("RGBA")

    # Alpha bbox + 閾值：只把 alpha > 32 的像素當內容，避免邊緣 artifact 干擾
    alpha = img.getchannel("A")
    mask = alpha.point(lambda v: 255 if v > 32 else 0)
    bbox = mask.getbbox()
    if bbox is None:
        raise SystemExit(f"❌ {src_path} 去背後完全空白，請檢查原圖")

    cropped = img.crop(bbox)
    src_w, src_h = cropped.size

    # 等比縮放，符合 max_w / max_h
    ratio = min(max_w / src_w, max_h / src_h)
    new_w, new_h = int(src_w * ratio), int(src_h * ratio)
    resized = cropped.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    paste_x = cx - new_w // 2
    paste_y = cy - new_h // 2
    canvas.paste(resized, (paste_x, paste_y), resized)
    canvas.save(out_path)

    print(f"✅ [{preset}] {src_path.name} → {out_path.name}")
    print(f"   原圖 {img.size} → 裁掉透明邊 {cropped.size} → 縮放 {(new_w, new_h)} → 貼到 ({paste_x}, {paste_y})")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    preset = sys.argv[1]
    src = Path(sys.argv[2])
    if not src.exists():
        raise SystemExit(f"❌ 找不到檔案: {src}")

    if len(sys.argv) >= 4:
        out = Path(sys.argv[3])
    else:
        # 預設輸出到 images/<preset>_<原檔名>.png
        out = Path("images") / f"{preset}_{src.stem}.png"

    out.parent.mkdir(parents=True, exist_ok=True)
    place(preset, src, out)


if __name__ == "__main__":
    main()
