"""
_gen_batch_bg.py — CD风格视频背景图批量生成

参数敲定版（2026-05-23）：
- 尺寸: 1920×1080 (16:9)
- 封面: 左侧180px，垂直居中
- 封面尺寸: 550px（加大）
- 模糊背景: GaussianBlur radius=30
- 暗角: vignette 强度0.75
- CD外圈: 深色边框16px + 细线 #3C3240
- CD内圈: 圆环 inner_r=55, hole_r=14
- 镜面高光: 左上角弧形白带
- 右侧渐暗: fade_x=封面右边缘+80px
- 右上装饰: 三颗金色小圆点
- 封面边框: 金色分隔线

用法:
    python _gen_batch_bg.py [--input DIR] [--output DIR]
"""

import os, sys, math, argparse
from PIL import Image, ImageDraw, ImageFilter

# ── 参数 ────────────────────────────────────────────
W, H = 1920, 1080                # 输出尺寸
COVER_X = 180                    # 封面距左边缘（加大留白）
COVER_SIZE = 550                 # 封面显示尺寸（加大）
BLUR_RADIUS = 30                 # 背景模糊强度
VIGNETTE_STRENGTH = 0.75         # 暗角强度
CD_BORDER = 16                   # CD外圈深色边框宽
CD_LINE_COLOR = (60, 50, 64)     # CD细线 #3C3240
CD_INNER_R = 55                  # CD内圈半径
CD_HOLE_R = 14                   # CD中心孔半径
FADE_MARGIN = 80                 # 右侧渐暗：封面右边缘+FADE_MARGIN
DOT_COLOR = (212, 175, 55)       # 金色圆点
DOT_RADIUS = 6                   # 圆点半径
DOT_GAP = 30                     # 圆点间距
DOT_TOP = 30                     # 圆点距顶

TEMPLATES_DIR = os.path.dirname(os.path.abspath(__file__))

def make_vignette(w, h, strength=0.75):
    """生成径向暗角图层"""
    img = Image.new('L', (w, h), 255)
    draw = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2
    max_r = math.sqrt(cx**2 + cy**2)
    for y in range(h):
        for x in range(w):
            d = math.sqrt((x - cx)**2 + (y - cy)**2) / max_r
            v = int(255 * (1 - strength * (1 - d)))
            draw.point((x, y), min(255, max(0, v)))
    return img

def make_fade_gradient(w, h, start_x, end_x):
    """从start_x到end_x从透明到黑色渐变"""
    img = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(img)
    for x in range(start_x, min(end_x, w)):
        ratio = (x - start_x) / (end_x - start_x) if end_x > start_x else 1
        v = int(255 * ratio)
        draw.rectangle([x, 0, x, h], fill=min(255, v))
    return img

def make_highlight(w, h):
    """左上角弧形镜面高光"""
    img = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = 150, 150
    r = 250
    for i in range(0, 360, 1):
        angle = math.radians(i)
        x = int(cx + r * math.cos(angle))
        y = int(cy + r * math.sin(angle))
        if x < w and y < h and x >= 0 and y >= 0:
            # 只保留左上扇形（约300度方向到30度方向）
            a = (i + 90) % 360
            if 270 <= a or a <= 60:
                draw.point((x, y), 180)
    img = img.filter(ImageFilter.GaussianBlur(20))
    return img

def process_cover(cover_path, output_path, cover_x=COVER_X, cover_size=COVER_SIZE):
    """单张封面 → CD风格背景图"""
    try:
        cover = Image.open(cover_path).convert('RGB')
    except Exception as e:
        print(f'  [SKIP] 无法打开 {cover_path}: {e}')
        return False

    # 1. 模糊背景
    bg = cover.copy().resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))

    # 2. 裁剪封面为正方形
    size = min(cover.size)
    left = (cover.width - size) // 2
    top = (cover.height - size) // 2
    cover_sq = cover.crop((left, top, left + size, top + size))
    cover_resized = cover_sq.resize((cover_size, cover_size), Image.LANCZOS)

    # 封面垂直居中位置
    cover_y = (H - cover_size) // 2

    # 3. 暗角
    vignette = make_vignette(W, H, VIGNETTE_STRENGTH)
    bg.putalpha(vignette)
    # 转回RGB
    bg_rgb = Image.new('RGB', (W, H), (0, 0, 0))
    bg_rgb.paste(bg, (0, 0), bg)

    # 4. 右侧渐暗
    fade_start = cover_x + cover_size + FADE_MARGIN
    fade_end = W
    fade_mask = make_fade_gradient(W, H, fade_start, fade_end)
    bg_faded = Image.composite(
        Image.new('RGB', (W, H), (0, 0, 0)),
        bg_rgb,
        fade_mask
    )

    # 5. 绘制CD装饰
    draw = ImageDraw.Draw(bg_faded)
    cd_cx = cover_x + cover_size // 2   # CD中心X
    cd_cy = cover_y + cover_size // 2   # CD中心Y
    cd_outer_r = cover_size // 2 + CD_BORDER

    # 5a. CD外圈深色边框
    draw.ellipse([
        cd_cx - cd_outer_r, cd_cy - cd_outer_r,
        cd_cx + cd_outer_r, cd_cy + cd_outer_r
    ], outline=CD_LINE_COLOR, width=CD_BORDER)

    # 5b. CD内圈装饰
    draw.ellipse([
        cd_cx - CD_INNER_R, cd_cy - CD_INNER_R,
        cd_cx + CD_INNER_R, cd_cy + CD_INNER_R
    ], outline=CD_LINE_COLOR, width=2)

    # 5c. CD中心孔
    draw.ellipse([
        cd_cx - CD_HOLE_R, cd_cy - CD_HOLE_R,
        cd_cx + CD_HOLE_R, cd_cy + CD_HOLE_R
    ], fill=(30, 30, 35), outline=CD_LINE_COLOR, width=1)

    # 6. 镜面高光
    highlight = make_highlight(W, H)
    hl = Image.new('RGB', (W, H), (255, 255, 255))
    hl.putalpha(highlight)
    bg_faded.paste(hl, (0, 0), hl)

    # 7. 右上角金色装饰圆点
    for i in range(3):
        dx = DOT_TOP + i * (DOT_RADIUS * 2 + DOT_GAP)
        draw.ellipse([
            W - dx - DOT_RADIUS, DOT_TOP,
            W - dx + DOT_RADIUS, DOT_TOP + DOT_RADIUS * 2
        ], fill=DOT_COLOR)

    # 8. 粘贴封面（在最上层）
    bg_faded.paste(cover_resized, (cover_x, cover_y))

    # 9. 封面边框（金色分隔线）
    border_color = DOT_COLOR
    draw.rectangle(
        [cover_x - 1, cover_y - 1, cover_x + cover_size, cover_y + cover_size],
        outline=border_color, width=2
    )

    bg_faded.save(output_path, 'PNG')
    return True


def main():
    parser = argparse.ArgumentParser(description='CD风格视频背景图批量生成')
    parser.add_argument('--input', default=None,
                        help='封面源目录（默认: 项目目录下的cover_sources/input/）')
    parser.add_argument('--output', default=None,
                        help='输出目录（默认: 项目目录下的output/bg/）')
    args = parser.parse_args()

    # 确定输入输出目录
    if args.input:
        input_dir = args.input
    else:
        input_dir = os.path.join(TEMPLATES_DIR, 'cover_sources', 'input')

    if args.output:
        output_dir = args.output
    else:
        output_dir = os.path.join(TEMPLATES_DIR, 'output', 'bg')

    if not os.path.isdir(input_dir):
        print(f'[ERROR] 输入目录不存在: {input_dir}')
        print('请将封面图片放入 cover_sources/input/ 目录，或使用 --input 指定')
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # 获取封面文件（按文件名排序）
    exts = ('.jpg', '.jpeg', '.png', '.webp')
    files = sorted([f for f in os.listdir(input_dir)
                    if f.lower().endswith(exts)])

    if not files:
        print(f'[WARN] 输入目录中没有封面图片: {input_dir}')
        sys.exit(0)

    total = len(files)
    success = 0
    for i, fname in enumerate(files, 1):
        cover_path = os.path.join(input_dir, fname)
        name_noext = os.path.splitext(fname)[0]
        out_name = f'bg_{i:02d}_{name_noext}.png'
        out_path = os.path.join(output_dir, out_name)

        print(f'[{i}/{total}] {fname} ...', end=' ')
        if process_cover(cover_path, out_path):
            print('OK')
            success += 1
        else:
            print('FAIL')

    print(f'\n完成: {success}/{total} 张背景图已生成')
    print(f'输出目录: {output_dir}')


if __name__ == '__main__':
    main()
