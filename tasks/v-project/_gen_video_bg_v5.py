"""_gen_video_bg_v5.py — V5 动画版背景视频

在 V4 精致版基础上加入：
- 唱片缓慢旋转（CD封面旋转动画）
- 可选脉冲光晕呼吸效果
- 输出为 MP4 视频片段

用法:
    python _gen_video_bg_v5.py --test 封面路径
    python _gen_video_bg_v5.py --input DIR --output DIR
"""

import os, sys, math, random, argparse, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ═══════════════════════════════════════════════════
# 参数
# ═══════════════════════════════════════════════════
W, H = 1920, 1080
COVER_X = 180
COVER_SIZE = 550
CD_BORDER = 16
CD_LINE_COLOR = (60, 50, 64)
CD_INNER_R = 55
CD_HOLE_R = 14
VIGNETTE_STRENGTH = 0.65
RIGHT_FADE_START = COVER_X + COVER_SIZE + 50
RIGHT_FADE_END = W - 50

# 动画参数
FPS = 24
DURATION = 3.0  # 秒
TOTAL_FRAMES = int(FPS * DURATION)
ROTATION_DEG_PER_SEC = 30  # 每秒旋转 30 度（12秒转一圈，缓慢优雅）
PULSE_AMPLITUDE = 0.05  # 脉冲幅度


# ═══════════════════════════════════════════════════
# 核心函数（V4 保留）
# ═══════════════════════════════════════════════════

def extract_dominant_color(img):
    """提取封面主色"""
    small = img.copy().resize((50, 50))
    if small.mode != 'RGB':
        small = small.convert('RGB')
    pixels = np.array(small).reshape(-1, 3)
    median = np.median(pixels, axis=0).astype(int)
    return tuple(median)


def make_vignette(w, h, strength=VIGNETTE_STRENGTH):
    """椭圆渐变暗角"""
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    rx, ry = w * 0.72, h * 0.60
    d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    d = np.clip(d, 0, 1)
    alpha = (1 - np.clip(1 - d, 0, 1) ** 2) * strength
    alpha = (alpha * 255).astype(np.uint8)
    return Image.fromarray(alpha, 'L')


def make_right_fade(w, h, fade_start, fade_end):
    """右侧缓慢渐暗"""
    fade = Image.new('L', (w, h), 0)
    x = np.arange(w)
    alpha = np.clip((x - fade_start) / (fade_end - fade_start), 0, 1)
    alpha = 1 - (1 - alpha) ** 2
    alpha = (alpha * 180).astype(np.uint8)
    fade_arr = np.array(fade, dtype=np.uint8)
    for row in range(h):
        fade_arr[row] = alpha
    return Image.fromarray(fade_arr, 'L')


def render_frame(cover_path, rotation_deg, pulse_factor):
    """渲染单帧画面"""
    cover = Image.open(cover_path).convert('RGB')
    dom_color = extract_dominant_color(cover)
    border_color = dom_color

    # 随机种子（基于路径，每张图固定）
    rand_seed = hash(cover_path) % 10000
    random.seed(rand_seed)
    blur_radius = random.uniform(35, 50)
    color_temp = random.uniform(-15, 15)
    grain_std = random.uniform(2, 6)
    shadow_intensity = random.uniform(0.25, 0.45)

    # 1. 模糊背景
    bg = cover.copy().resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(blur_radius))

    # 色温偏移
    if color_temp > 0:
        r_mul, g_mul, b_mul = 1 + color_temp / 100, 1, 1 - color_temp / 200
    else:
        r_mul, g_mul, b_mul = 1 + color_temp / 200, 1, 1 - color_temp / 100
    bg_arr = np.array(bg, dtype=np.float32)
    bg_arr[:, :, 0] = np.clip(bg_arr[:, :, 0] * r_mul, 0, 255)
    bg_arr[:, :, 2] = np.clip(bg_arr[:, :, 2] * b_mul, 0, 255)
    bg = Image.fromarray(bg_arr.astype(np.uint8))

    # 2. 暗角
    vig = make_vignette(W, H, VIGNETTE_STRENGTH)
    bg_arr = np.array(bg, dtype=np.float32)
    vig_arr = np.array(vig, dtype=np.float32)[:, :, None]
    bg_arr = bg_arr * (1 - vig_arr / 255)
    bg = Image.fromarray(bg_arr.astype(np.uint8))

    # 3. 右侧渐暗
    rf = make_right_fade(W, H, RIGHT_FADE_START, RIGHT_FADE_END)
    bg_arr = np.array(bg, dtype=np.float32)
    rf_arr = np.array(rf, dtype=np.float32)[:, :, None]
    bg_arr = bg_arr * (1 - rf_arr / 255)
    bg = Image.fromarray(bg_arr.astype(np.uint8))

    # 4. 胶片颗粒
    grain = np.random.normal(0, grain_std, (H, W, 3)).astype(np.int16)
    bg_arr = np.array(bg, dtype=np.int16)
    bg_arr = np.clip(bg_arr + grain, 0, 255).astype(np.uint8)
    bg = Image.fromarray(bg_arr)

    # 5. 封面阴影
    cover_y = (H - COVER_SIZE) // 2
    shadow_full = Image.new('L', (W, H), 0)
    sd = ImageDraw.Draw(shadow_full)
    sd.ellipse([COVER_X - 12, cover_y - 2,
                COVER_X + COVER_SIZE + 12, cover_y + COVER_SIZE + 2],
               fill=int(80 * shadow_intensity))
    shadow_full = shadow_full.filter(ImageFilter.GaussianBlur(12))
    bg_arr = np.array(bg, dtype=np.float32)
    sh_arr = np.array(shadow_full, dtype=np.float32)[:, :, None]
    bg_arr = bg_arr * (1 - sh_arr / 255)
    bg = Image.fromarray(bg_arr.astype(np.uint8))

    # 6. 旋转的封面
    cover_size_pulse = int(COVER_SIZE * (1 + pulse_factor * 0.003))
    cover_resized = cover.copy().resize((cover_size_pulse, cover_size_pulse))
    cover_rotated = cover_resized.rotate(rotation_deg, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0))

    # 裁切旋转后的封面到原始大小
    rw, rh = cover_rotated.size
    cx2, cy2 = rw // 2, rh // 2
    half = cover_size_pulse // 2
    cover_rotated = cover_rotated.crop((cx2 - half, cy2 - half, cx2 + half, cy2 + half))
    cover_rotated = cover_rotated.resize((COVER_SIZE, COVER_SIZE), Image.LANCZOS)

    # 粘贴封面
    bg.paste(cover_rotated, (COVER_X, cover_y))

    # 7. CD 装饰（深色边框）
    draw = ImageDraw.Draw(bg)

    # 外边框
    for i in range(CD_BORDER):
        bw = CD_BORDER - i
        draw.rectangle([COVER_X - bw, cover_y - bw,
                        COVER_X + COVER_SIZE + bw, cover_y + COVER_SIZE + bw],
                       outline=CD_LINE_COLOR, width=1)

    # 中心孔
    center_x = COVER_X + COVER_SIZE // 2
    center_y = cover_y + COVER_SIZE // 2
    draw.ellipse([center_x - CD_INNER_R, center_y - CD_INNER_R,
                  center_x + CD_INNER_R, center_y + CD_INNER_R],
                 outline=(80, 70, 85), width=3)
    draw.ellipse([center_x - CD_HOLE_R, center_y - CD_HOLE_R,
                  center_x + CD_HOLE_R, center_y + CD_HOLE_R],
                 fill=(20, 18, 22))

    # 8. 封面边框（动态配色）
    border_width = 3
    draw.rectangle([COVER_X, cover_y, COVER_X + COVER_SIZE, cover_y + COVER_SIZE],
                   outline=border_color, width=border_width)

    # 9. 镜面高光
    highlight = Image.new('RGBA', (COVER_SIZE, COVER_SIZE), (0, 0, 0, 0))
    hd = ImageDraw.Draw(highlight)
    hd.pieslice([0, 0, COVER_SIZE * 2, COVER_SIZE * 2],
                start=330, end=360 + 30, fill=(255, 255, 255, 18))
    hd.pieslice([0, 0, COVER_SIZE * 2, COVER_SIZE * 2],
                start=330, end=360 + 30, fill=(255, 255, 255, 8))
    highlight = highlight.filter(ImageFilter.GaussianBlur(8))
    highlight = highlight.resize((COVER_SIZE, COVER_SIZE), Image.LANCZOS)
    # 旋转高光跟随封面
    highlight = highlight.rotate(rotation_deg * 0.3, resample=Image.BICUBIC)
    bg = bg.convert('RGBA')
    bg.alpha_composite(highlight, (COVER_X, cover_y))
    bg = bg.convert('RGB')

    # 10. 脉冲光晕
    if pulse_factor > 0.01:
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        glow_radius = int(COVER_SIZE * 0.6 * (1 + pulse_factor * 0.5))
        glow_alpha = int(15 * pulse_factor)
        gd.ellipse([center_x - glow_radius, center_y - glow_radius,
                    center_x + glow_radius, center_y + glow_radius],
                   fill=(*border_color, glow_alpha))
        glow = glow.filter(ImageFilter.GaussianBlur(30))
        bg = bg.convert('RGBA')
        bg.alpha_composite(glow)
        bg = bg.convert('RGB')

    return bg


def process_animated(cover_path, output_path):
    """生成动画 MP4"""
    print(f'  ⏳ 生成中...', end='', flush=True)

    frames_dir = tempfile.mkdtemp()
    try:
        for i in range(TOTAL_FRAMES):
            t = i / FPS
            rotation = t * ROTATION_DEG_PER_SEC
            pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 1.5)  # 1.5Hz 呼吸

            frame = render_frame(cover_path, rotation, pulse)
            frame_path = os.path.join(frames_dir, f'frame_{i:04d}.png')
            frame.save(frame_path)

        # 用 ffmpeg 合成 MP4
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-framerate', str(FPS),
            '-i', os.path.join(frames_dir, 'frame_%04d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '18',
            '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)

        # 同时输出 GIF
        gif_path = output_path.replace('.mp4', '.gif')
        cmd_gif = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-framerate', str(FPS),
            '-i', os.path.join(frames_dir, 'frame_%04d.png'),
            '-vf', 'fps=12,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
            '-loop', '0',
            gif_path
        ]
        try:
            subprocess.run(cmd_gif, check=True, capture_output=True, timeout=60)
            print(f'✅ MP4+GIF → {os.path.basename(output_path)}', end='')
        except:
            print(f'✅ MP4 → {os.path.basename(output_path)}', end='')

    finally:
        import shutil
        shutil.rmtree(frames_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description='V5 动画版背景视频')
    parser.add_argument('--input', help='输入目录（封面图片）')
    parser.add_argument('--output', help='输出目录')
    parser.add_argument('--test', help='测试单张封面')
    args = parser.parse_args()

    if args.test:
        out = args.test.rsplit('.', 1)[0] + '_v5.mp4'
        print(f'[TEST] {args.test}')
        process_animated(args.test, out)
        print(f'  → {out}')
        return

    if args.input and args.output:
        os.makedirs(args.output, exist_ok=True)
        covers = sorted([f for f in os.listdir(args.input)
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        total = len(covers)
        for idx, fname in enumerate(covers, 1):
            inp = os.path.join(args.input, fname)
            out_name = fname.rsplit('.', 1)[0] + '_v5.mp4'
            out_path = os.path.join(args.output, out_name)
            print(f'[{idx}/{total}] {fname} ... ', end='', flush=True)
            process_animated(inp, out_path)
            print()
        print(f'\n完成: {total}/{total} 张')
        return

    parser.print_help()


if __name__ == '__main__':
    main()