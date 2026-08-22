"""_gen_video_bg_v5.py — V5 黑胶唱片动画版

视觉效果：
- 唱片机效果：黑胶外圈大、中心封面（标签）小 → 真实比例
- 唱片缓慢旋转（40 RPM，3秒整2圈 → 自循环无卡顿）
- 唱片纹路 + 反光高光扫过
- 均衡器跳动在唱片右侧
- 背景模糊、暗角、颗粒保留 V4 精致版

用法:
    python _gen_video_bg_v5.py --test 封面路径
    python _gen_video_bg_v5.py --input DIR --output DIR
"""

import os, sys, math, random, argparse, subprocess, tempfile, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ═══════════════════════════════════════════════════
# 参数
# ═══════════════════════════════════════════════════
W, H = 1920, 1080
COVER_X = 200
VINYL_DIAMETER = 500        # 唱片总直径
COVER_DIAMETER = 300        # 封面（中心标签）直径
VINYL_RING = (VINYL_DIAMETER - COVER_DIAMETER) // 2  # 黑胶外圈宽度
VINYL_HOLE_R = 8
VIGNETTE_STRENGTH = 0.60
RIGHT_FADE_START = COVER_X + VINYL_DIAMETER + 100
RIGHT_FADE_END = W - 50

# 动画参数（自循环：3秒整2圈 → 首尾帧无缝衔接）
FPS = 24
DURATION = 3.0
TOTAL_FRAMES = int(FPS * DURATION)
ROTATION_SPEED = 720 / DURATION       # 3秒转2圈 = 240°/s → 无缝
PULSE_SPEED = 1.2                      # 呼吸脉冲频率
# 均衡器：每个频段在 DURATION 内完成整数周期 → 无缝循环
EQ_CYCLES = [2, 3, 4, 5, 3, 2]        # 每根柱的周期数（整数→无缝）
# 背景微动（Ken Burns：3秒内缓慢缩放来回，无缝）
BG_ZOOM_AMPLITUDE = 0.025              # 缩放幅度 ±2.5%
BG_ZOOM_CYCLES = 1                     # 3秒完成1次完整呼吸


def extract_dominant_color(img):
    small = img.copy().resize((50, 50)).convert('RGB')
    pixels = np.array(small).reshape(-1, 3)
    median = np.median(pixels, axis=0).astype(int)
    return tuple(median)


def make_vignette(w, h, strength=VIGNETTE_STRENGTH):
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    rx, ry = w * 0.72, h * 0.60
    d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    d = np.clip(d, 0, 1)
    alpha = (1 - np.clip(1 - d, 0, 1) ** 2) * strength
    alpha = (alpha * 255).astype(np.uint8)
    return Image.fromarray(alpha, 'L')


def make_right_fade(w, h):
    fade = Image.new('L', (w, h), 0)
    x = np.arange(w)
    alpha = np.clip((x - RIGHT_FADE_START) / (RIGHT_FADE_END - RIGHT_FADE_START), 0, 1)
    alpha = 1 - (1 - alpha) ** 2
    alpha = (alpha * 180).astype(np.uint8)
    arr = np.array(fade, dtype=np.uint8)
    for row in range(h):
        arr[row] = alpha
    return Image.fromarray(arr, 'L')


def create_vinyl_base(cover_path):
    """创建唱片底图（与旋转无关的部分）"""
    cover = Image.open(cover_path).convert('RGB')
    dom_color = extract_dominant_color(cover)
    border_color = dom_color

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
    rf = make_right_fade(W, H)
    bg_arr = np.array(bg, dtype=np.float32)
    rf_arr = np.array(rf, dtype=np.float32)[:, :, None]
    bg_arr = bg_arr * (1 - rf_arr / 255)
    bg = Image.fromarray(bg_arr.astype(np.uint8))

    # 4. 胶片颗粒
    grain = np.random.normal(0, grain_std, (H, W, 3)).astype(np.int16)
    bg_arr = np.array(bg, dtype=np.int16)
    bg_arr = np.clip(bg_arr + grain, 0, 255).astype(np.uint8)
    bg = Image.fromarray(bg_arr)

    return bg, cover, dom_color, border_color, shadow_intensity


def build_vinyl_layer(cover, dom_color, border_color, rotation_deg):
    """构建旋转后的唱片图层（含封面、纹路、高光、中心孔）"""
    vr = VINYL_DIAMETER // 2
    cr = COVER_DIAMETER // 2
    cx = cy = vr

    # 唱片底图（透明背景）
    vinyl = Image.new('RGBA', (VINYL_DIAMETER, VINYL_DIAMETER), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vinyl)

    # 黑胶外圈（深色，带微弱纹理）
    vd.ellipse([0, 0, VINYL_DIAMETER - 1, VINYL_DIAMETER - 1], fill=(22, 18, 25))

    # 唱片纹路（同心圆）
    for i in range(1, 12):
        r = vr - i * (VINYL_RING // 12)
        alpha = 30 - i * 2
        if alpha < 8:
            alpha = 8
        vd.ellipse([vr - r, vr - r, vr + r, vr + r],
                   outline=(alpha, alpha - 2, alpha + 5), width=1)

    # 中心封面（裁成圆形）
    cover_resized = cover.copy().resize((COVER_DIAMETER, COVER_DIAMETER), Image.LANCZOS)
    mask = Image.new('L', (COVER_DIAMETER, COVER_DIAMETER), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, COVER_DIAMETER - 1, COVER_DIAMETER - 1], fill=255)
    cover_masked = Image.new('RGBA', (COVER_DIAMETER, COVER_DIAMETER), (0, 0, 0, 0))
    cover_masked.paste(cover_resized, (0, 0), mask)
    vinyl.paste(cover_masked, (VINYL_RING, VINYL_RING))

    # 封面边框（圆形，强调圆形切割）
    vd.ellipse([VINYL_RING - 1, VINYL_RING - 1,
                VINYL_DIAMETER - VINYL_RING, VINYL_DIAMETER - VINYL_RING],
               outline=border_color, width=3)
    # 内圈细线（强化圆形视觉）
    inner = VINYL_RING + 2
    vd.ellipse([inner, inner, VINYL_DIAMETER - inner - 1, VINYL_DIAMETER - inner - 1],
               outline=(40, 35, 45), width=1)

    # 中心孔
    vd.ellipse([cx - VINYL_HOLE_R, cy - VINYL_HOLE_R,
                cx + VINYL_HOLE_R, cy + VINYL_HOLE_R],
               fill=(15, 12, 18))

    # 旋转
    vinyl_rotated = vinyl.rotate(rotation_deg, expand=False, resample=Image.BICUBIC)

    # 唱片高光（扫过唱片表面的反光）
    highlight = Image.new('RGBA', (VINYL_DIAMETER, VINYL_DIAMETER), (0, 0, 0, 0))
    hd = ImageDraw.Draw(highlight)
    light_angle = rotation_deg * 0.5  # 高光随唱片同步旋转
    for offset in range(-25, 26):
        angle = light_angle + offset * 0.8
        rad = math.radians(angle)
        a = max(0, 10 - abs(offset) * 0.4)
        if a <= 0:
            continue
        hd.pieslice([0, 0, VINYL_DIAMETER - 1, VINYL_DIAMETER - 1],
                     start=angle - 1, end=angle + 1,
                     fill=(255, 255, 255, int(a)))
    highlight = highlight.filter(ImageFilter.GaussianBlur(4))
    highlight_rotated = highlight.rotate(rotation_deg, expand=False, resample=Image.BICUBIC)

    # 合并高光到唱片
    vinyl_rotated = vinyl_rotated.convert('RGBA')
    vinyl_rotated.alpha_composite(highlight_rotated)

    return vinyl_rotated


def draw_tonearm(frame, cx, cy, vr, pulse_factor):
    """画唱针（唱臂从右上角伸向唱片）"""
    draw = ImageDraw.Draw(frame)
    # 唱臂底座（右上角）
    base_x = cx + vr + 60
    base_y = cy - vr - 60
    # 唱臂本体（从底座到唱片中心偏左的位置）
    arm_end_x = cx + vr * 0.15
    arm_end_y = cy + vr * 0.05

    # 唱臂阴影
    draw.line([base_x + 3, base_y + 3, arm_end_x + 3, arm_end_y + 3],
              fill=(0, 0, 0, 90), width=5)
    # 唱臂主体（深色细杆）
    draw.line([base_x, base_y, arm_end_x, arm_end_y],
              fill=(45, 42, 50), width=4)
    # 唱臂高光
    draw.line([base_x - 1, base_y - 1, arm_end_x - 1, arm_end_y - 1],
              fill=(90, 85, 95), width=1)
    # 唱头（末端小方块）
    head_size = 14
    head_angle = math.atan2(arm_end_y - base_y, arm_end_x - base_x)
    hx = arm_end_x - math.cos(head_angle) * 8
    hy = arm_end_y - math.sin(head_angle) * 8
    draw.polygon([
        (hx, hy),
        (hx + math.cos(head_angle + math.pi/2) * head_size * 0.6,
         hy + math.sin(head_angle + math.pi/2) * head_size * 0.6),
        (hx + math.cos(head_angle) * head_size,
         hy + math.sin(head_angle) * head_size),
        (hx + math.cos(head_angle - math.pi/2) * head_size * 0.6,
         hy + math.sin(head_angle - math.pi/2) * head_size * 0.6),
    ], fill=(35, 32, 40))

    # 底座圆
    draw.ellipse([base_x - 12, base_y - 12, base_x + 12, base_y + 12],
                 fill=(50, 46, 55), outline=(70, 66, 75), width=2)
    draw.ellipse([base_x - 5, base_y - 5, base_x + 5, base_y + 5],
                 fill=(30, 27, 35))


def render_frame(cover, bg, dom_color, border_color, shadow_intensity,
                 rotation_deg, pulse_factor, frame_idx, bg_zoom):
    """渲染单帧"""
    hw = H // 2
    cx = COVER_X + VINYL_DIAMETER // 2
    cy = hw
    vr = VINYL_DIAMETER // 2

    # --- 背景微动（Ken Burns 缩放）---
    if abs(bg_zoom - 1.0) > 0.001:
        new_w = int(W * bg_zoom)
        new_h = int(H * bg_zoom)
        zoomed = bg.resize((new_w, new_h), Image.LANCZOS)
        # 居中裁剪
        left = (new_w - W) // 2
        top = (new_h - H) // 2
        frame = zoomed.crop((left, top, left + W, top + H))
    else:
        frame = bg.copy()

    # --- 粘贴唱片 ---
    vinyl_layer = build_vinyl_layer(cover, dom_color, border_color, rotation_deg)
    frame = frame.convert('RGBA')
    frame.alpha_composite(vinyl_layer, (COVER_X, cy - vr))
    frame = frame.convert('RGB')

    # --- 唱针 ---
    draw_tonearm(frame, cx, cy, vr, pulse_factor)

    # --- 均衡器（无缝循环：每个频段整数周期）---
    draw = ImageDraw.Draw(frame)
    eq_x = COVER_X + VINYL_DIAMETER + 30
    eq_y = cy - vr + 30
    eq_h = vr * 2 - 60
    eq_w = 5
    num_bars = len(EQ_CYCLES)
    bar_gap = 3
    t = frame_idx / FPS
    for i in range(num_bars):
        # 多个正弦叠加 → 更像真实音频频谱，且整数周期无缝
        w = 2 * math.pi * EQ_CYCLES[i] / DURATION
        v = (0.5 + 0.5 * math.sin(w * t)) * 0.6 \
            + (0.5 + 0.5 * math.sin(w * 2 * t + i)) * 0.4
        bar_height = int(eq_h * (0.15 + 0.85 * v))
        bar_y = eq_y + (eq_h - bar_height) // 2
        bar_color = tuple(min(255, c + 30) for c in border_color)
        draw.rectangle([eq_x + i * (eq_w + bar_gap), bar_y,
                        eq_x + i * (eq_w + bar_gap) + eq_w, bar_y + bar_height],
                       fill=bar_color)

    # --- 脉冲光晕 ---
    if pulse_factor > 0.05:
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        glow_r = int(vr * 0.8 * (1 + pulse_factor * 0.3))
        glow_alpha = int(12 * pulse_factor)
        gd.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r],
                   fill=(*dom_color, glow_alpha))
        glow = glow.filter(ImageFilter.GaussianBlur(25))
        frame = frame.convert('RGBA')
        frame.alpha_composite(glow)
        frame = frame.convert('RGB')

    return frame


def process_animated(cover_path, output_path):
    print(f'  ⏳ 生成中...', end='', flush=True)
    frames_dir = tempfile.mkdtemp()

    bg, cover, dom_color, border_color, shadow_intensity = create_vinyl_base(cover_path)

    try:
        for i in range(TOTAL_FRAMES):
            t = i / FPS
            # 旋转角度 = 刚好在 DURATION 秒内完成整数圈 → 首尾帧无缝
            rotation = i * (ROTATION_SPEED / FPS)
            pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi * PULSE_SPEED)
            # 背景缩放：1 个完整周期 → 无缝
            bg_zoom = 1.0 + BG_ZOOM_AMPLITUDE * math.sin(2 * math.pi * BG_ZOOM_CYCLES * t / DURATION)

            frame = render_frame(cover, bg, dom_color, border_color,
                                 shadow_intensity, rotation, pulse, i, bg_zoom)
            frame_path = os.path.join(frames_dir, f'frame_{i:04d}.png')
            frame.save(frame_path)

        # MP4
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-framerate', str(FPS),
            '-i', os.path.join(frames_dir, 'frame_%04d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '18',
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)

        # GIF
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
        shutil.rmtree(frames_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description='V5 黑胶唱片动画版')
    parser.add_argument('--input', help='输入目录')
    parser.add_argument('--output', help='输出目录')
    parser.add_argument('--test', help='测试单张')
    args = parser.parse_args()

    if args.test:
        out = args.test.rsplit('.', 1)[0] + '_v5.mp4'
        print(f'[TEST] {args.test}')
        process_animated(args.test, out)
        print(f'\n  → {out}')
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