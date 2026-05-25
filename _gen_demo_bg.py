import random, sqlite3, os, sys
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

db_path = r'G:\原创计划\music'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums ORDER BY RANDOM() LIMIT 1")
row = c.fetchone()
conn.close()

album_id, album_name, artist, cover_rel = row
cover_dir = r'C:\Users\qujt\.qclaw\workspace\covers'
cover_path = os.path.join(cover_dir, os.path.basename(cover_rel))
print(f"album: {artist} - {album_name} (id={album_id})")

W, H = 1920, 1080
CARD_W, CARD_H = 520, 520
blur_radius = 30
CARD_X = 80
CARD_Y = (H - CARD_H) // 2
cx_c = CARD_W // 2
cy_c = CARD_H // 2

orig = Image.open(cover_path).convert('RGB').resize((W, H), Image.LANCZOS)
blurred = orig.filter(ImageFilter.GaussianBlur(radius=blur_radius))

# dark overlay + vignette
dark = Image.new('RGB', (W, H), (8, 6, 12))
vign_arr = np.zeros((H, W), dtype=np.float32)
for y in range(H):
    for x in range(W):
        d = max(abs(x - W//2) / (W/2), abs(y - H//2) / (H/2))
        vign_arr[y, x] = max(0.0, 1.0 - d * 0.75)
vign_mask = Image.fromarray((vign_arr * 255).astype(np.uint8), mode='L')
blurred.paste(dark, mask=vign_mask)

# 完整封面（不做任何裁切）
card_raw = orig.resize((CARD_W, CARD_H), Image.LANCZOS)
blurred.paste(card_raw, (CARD_X, CARD_Y))

# CD 外圈：用深色边框盖在封面四边（不做圆形裁切）
ring_thick = 16
outer_color = (10, 8, 16)
# 上下左右四条边框
draw_bg = ImageDraw.Draw(blurred)
draw_bg.rectangle([CARD_X - ring_thick, CARD_Y - ring_thick,
                   CARD_X + CARD_W + ring_thick - 1, CARD_Y + CARD_H + ring_thick - 1],
                  fill=outer_color)
# 再把封面贴回去（只有边框露出来）
blurred.paste(card_raw, (CARD_X, CARD_Y))

# CD 外圈细线
outer_line_color = (60, 50, 80)
draw_bg.rectangle([CARD_X - 2, CARD_Y - 2,
                   CARD_X + CARD_W + 1, CARD_Y + CARD_H + 1],
                  fill=outer_line_color)
blurred.paste(card_raw, (CARD_X, CARD_Y))

# CD 内圈圆环（贴在内圈中心，不遮挡封面主要区域）
# 内圈半径 55px，中心孔 14px（保持专辑封面完整）
inner_r = 55
hole_r = 14
draw_bg = ImageDraw.Draw(blurred)
cx_cc = CARD_X + cx_c
cy_cc = CARD_Y + cy_c
# 画内圈圆环（填充为深色，中心透明）
for r in range(inner_r, hole_r, -1):
    alpha_int = int(255 * (1 - (inner_r - r) / (inner_r - hole_r)) * 0.9)
    gray = max(10, 30 - (inner_r - r) * 0.4)
    col = (int(gray), int(gray * 0.8), int(gray * 1.1))
    draw_bg.ellipse([cx_cc - r, cy_cc - r, cx_cc + r, cy_cc + r], outline=col)

# 中心孔（透出背景）
draw_bg.ellipse([cx_cc - hole_r, cy_cc - hole_r, cx_cc + hole_r, cy_cc + hole_r],
                fill=(8, 6, 12))

# 镜面高光（左上角弧形白色反光带，模拟CD光泽）
hl_mask = Image.new('L', (W, H), 0)
hl_draw = ImageDraw.Draw(hl_mask)
hl_x0 = CARD_X
hl_y0 = CARD_Y
hl_w = CARD_W
hl_h = CARD_H
# 画弧形高光（从左上角斜向右下的弧线）
for angle in range(0, 90, 2):
    import math
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

hl_color = Image.new('RGB', (W, H), (255, 252, 245))
blurred.paste(hl_color, mask=hl_mask)

# 右侧文字区渐暗
fade_x = CARD_X + CARD_W + 80
fade_arr = np.zeros((H, W), dtype=np.uint8)
for x in range(W):
    if x >= fade_x:
        fade_arr[:, x] = min(120, int((x - fade_x) / 4))
fade_img = Image.fromarray(fade_arr, mode='L')
dark_r = Image.new('RGB', (W, H), (5, 4, 10))
blurred.paste(dark_r, mask=fade_img)

# 右上装饰小圆点
dd = ImageDraw.Draw(blurred)
dd.ellipse([W-200, 80, W-188, 92], fill=(255, 200, 80))
dd.ellipse([W-172, 98, W-166, 104], fill=(255, 200, 80))
dd.ellipse([W-158, 76, W-154, 80], fill=(180, 140, 50))

# 封面右侧分隔线
dd.line([CARD_X + CARD_W + 30, CARD_Y, CARD_X + CARD_W + 30, CARD_Y + CARD_H],
        fill=(255, 200, 80, 80), width=1)

out_dir = r'C:\Users\qujt\.qclaw\workspace\video_thumbs'
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, f'demo_bg_cd2_{album_id}.png')
blurred.save(out_path)
sz = os.path.getsize(out_path) // 1024
print(f"[OK] saved: {out_path} ({sz} KB)")