import random, os, math
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

SRC_DIR = r"C:\Users\qujt\.qclaw\workspace\video_thumbs\20th_century_indie"
OUT_DIR = r"C:\Users\qujt\.qclaw\workspace\video_thumbs\20th_century_indie_bg"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1920, 1080
CARD_W, CARD_H = 520, 520
blur_radius = 30
CARD_X = 80
CARD_Y = (H - CARD_H) // 2

covers = sorted(os.listdir(SRC_DIR))

for idx, fname in enumerate(covers, 1):
    src_path = os.path.join(SRC_DIR, fname)
    out_path = os.path.join(OUT_DIR, f"bg_{idx:02d}_{fname.replace('.jpg','.png')}")
    
    orig = Image.open(src_path).convert("RGB").resize((W, H), Image.LANCZOS)
    blurred = orig.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # dark overlay + vignette
    dark = Image.new("RGB", (W, H), (8, 6, 12))
    vign_arr = np.zeros((H, W), dtype=np.float32)
    for y in range(H):
        for x in range(W):
            d = max(abs(x - W//2) / (W/2), abs(y - H//2) / (H/2))
            vign_arr[y, x] = max(0.0, 1.0 - d * 0.75)
    vign_mask = Image.fromarray((vign_arr * 255).astype(np.uint8), mode="L")
    blurred.paste(dark, mask=vign_mask)
    
    # 完整封面（不做任何裁切）
    card_raw = orig.resize((CARD_W, CARD_H), Image.LANCZOS)
    blurred.paste(card_raw, (CARD_X, CARD_Y))
    
    # CD 外圈：深色边框
    ring_thick = 16
    draw_bg = ImageDraw.Draw(blurred)
    draw_bg.rectangle([CARD_X - ring_thick, CARD_Y - ring_thick,
                       CARD_X + CARD_W + ring_thick - 1, CARD_Y + CARD_H + ring_thick - 1],
                      fill=(10, 8, 16))
    blurred.paste(card_raw, (CARD_X, CARD_Y))
    
    # CD 外圈细线
    draw_bg.rectangle([CARD_X - 2, CARD_Y - 2,
                       CARD_X + CARD_W + 1, CARD_Y + CARD_H + 1],
                      fill=(60, 50, 80))
    blurred.paste(card_raw, (CARD_X, CARD_Y))
    
    # CD 内圈圆环
    inner_r = 55
    hole_r = 14
    cx_cc = CARD_X + CARD_W // 2
    cy_cc = CARD_Y + CARD_H // 2
    for r in range(inner_r, hole_r, -1):
        gray = max(10, 30 - (inner_r - r) * 0.4)
        col = (int(gray), int(gray * 0.8), int(gray * 1.1))
        draw_bg.ellipse([cx_cc - r, cy_cc - r, cx_cc + r, cy_cc + r], outline=col)
    draw_bg.ellipse([cx_cc - hole_r, cy_cc - hole_r, cx_cc + hole_r, cy_cc + hole_r],
                    fill=(8, 6, 12))
    
    # 镜面高光（左上角）
    hl_mask = Image.new("L", (W, H), 0)
    hl_draw = ImageDraw.Draw(hl_mask)
    hl_x0 = CARD_X
    hl_y0 = CARD_Y
    hl_w = CARD_W
    hl_h = CARD_H
    for angle in range(0, 90, 2):
        rad = math.radians(angle)
        for t in [0.0, 0.3, 0.6]:
            px = int(hl_x0 + (hl_w * 0.55) * math.cos(rad) * (1 - t * 0.7))
            py = int(hl_y0 + (hl_h * 0.55) * math.sin(rad) * (1 - t * 0.7))
            r2 = max(2, int(12 * (1 - t)))
            for dy2 in range(-r2, r2 + 1):
                for dx2 in range(-r2, r2 + 1):
                    if dx2*dx2 + dy2*dy2 <= r2*r2:
                        sx, sy = px + dx2, py + dy2
                        if 0 <= sx < W and 0 <= sy < H:
                            alpha_cur = max(0, int(55 * (1 - t) * math.sin(rad)))
                            cur = hl_mask.getpixel((sx, sy))
                            if isinstance(cur, int):
                                hl_mask.putpixel((sx, sy), min(255, cur + alpha_cur))
                            else:
                                hl_mask.putpixel((sx, sy), min(255, cur[0] + alpha_cur))
    hl_color = Image.new("RGB", (W, H), (255, 252, 245))
    blurred.paste(hl_color, mask=hl_mask)
    
    # 右侧文字区渐暗
    fade_x = CARD_X + CARD_W + 80
    fade_arr = np.zeros((H, W), dtype=np.uint8)
    for x in range(W):
        if x >= fade_x:
            fade_arr[:, x] = min(120, int((x - fade_x) / 4))
    fade_img = Image.fromarray(fade_arr, mode="L")
    dark_r = Image.new("RGB", (W, H), (5, 4, 10))
    blurred.paste(dark_r, mask=fade_img)
    
    # 右上装饰
    dd = ImageDraw.Draw(blurred)
    dd.ellipse([W-200, 80, W-188, 92], fill=(255, 200, 80))
    dd.ellipse([W-172, 98, W-166, 104], fill=(255, 200, 80))
    dd.ellipse([W-158, 76, W-154, 80], fill=(180, 140, 50))
    
    # 封面右侧分隔线
    dd.line([CARD_X + CARD_W + 30, CARD_Y, CARD_X + CARD_W + 30, CARD_Y + CARD_H],
            fill=(255, 200, 80, 80), width=1)
    
    blurred.save(out_path)
    name = out_path.split("\\")[-1]
    sz = os.path.getsize(out_path) // 1024
    print(f"[{idx:02d}] {name} ({sz} KB)")