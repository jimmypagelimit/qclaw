#!/usr/bin/env python3
"""V7 旋转版：统一专辑主色背景、固定封面，仅黑胶材质顺时针旋转。

python3 _gen_video_bg_v7.py --test cover.jpg --output output/video_v7
python3 _gen_video_bg_v7.py --input cover_sources/input/歌单 --output output/video_v7/歌单

Pillow + NumPy + ffmpeg；1920×1080 / H.264 / yuv420p / 无声 MP4。
默认 30fps，6秒一圈，循环一圈；末帧不重复首帧。
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

from _gen_batch_bg_v7 import EXTENSIONS, W, H, disc, load_cover, palette, render

DISC_X, DISC_Y, DISC_SIZE = 414, 219, 642


class Scene:
    """Cache the approved static composition; all motion is restricted to exposed vinyl."""

    def __init__(self, cover: Image.Image):
        self.base = render(cover)
        self.roi = self.base.crop((DISC_X, DISC_Y, DISC_X + DISC_SIZE, DISC_Y + DISC_SIZE))
        _, accent = palette(cover)
        original = disc(accent)
        arr = np.asarray(original).copy()
        y, x = np.mgrid[:DISC_SIZE, :DISC_SIZE].astype(np.float32)
        r = np.hypot(x - 320.5, y - 320.5)
        theta = np.arctan2(y - 320.5, x - 320.5)
        sheen = np.exp(-(np.sin(theta - .65) / .27) ** 2) * 15
        grooves = (r >= 98) & (r < 319)
        light = np.zeros((DISC_SIZE, DISC_SIZE), dtype=np.float32)
        light[grooves] = sheen[grooves]
        material = arr[:, :, :3].astype(np.float32) - light[..., None]
        self.material = Image.fromarray(np.clip(material, 0, 255).astype(np.uint8)).convert('RGBA')
        self.material.putalpha(original.getchannel('A'))
        ink = ImageDraw.Draw(self.material)
        label_ink = tuple(int(v * .27 + 16) for v in accent) + (255,)
        # Abstract printed label markings, without invented album metadata.
        ink.arc((248, 248, 393, 393), 12, 145, fill=label_ink, width=2)
        ink.arc((256, 256, 385, 385), 188, 278, fill=label_ink, width=1)
        ink.line((341, 288, 379, 288), fill=label_ink, width=3)
        ink.line((341, 297, 368, 297), fill=label_ink, width=2)
        ink.line((288, 350, 310, 350), fill=label_ink, width=3)
        # Sparse, quiet pressing details make rotation legible beyond concentric grooves.
        ink.arc((29, 29, 612, 612), 23, 57, fill=(48, 49, 49, 255), width=1)
        ink.arc((54, 54, 587, 587), 212, 229, fill=(37, 38, 39, 255), width=1)
        self.light = light[..., None]
        self.visible = original.getchannel('A')
        mask = ImageDraw.Draw(self.visible)
        # The stationary sleeve occludes the moving record, including all cover pixels.
        mask.rectangle((0, 32, 329, 609), fill=0)
        # Preserve the stationary lower registration mark.
        mask.rectangle((334, 615, 351, 629), fill=0)
        mask.line((0, 623, 316, 623), fill=0, width=1)

    def frame(self, clockwise_degrees: float) -> Image.Image:
        angle = clockwise_degrees % 360
        if math.isclose(angle, 0, abs_tol=1e-10):
            rotated = self.material
        else:
            rotated = self.material.rotate(-angle, resample=Image.Resampling.BICUBIC,
                                           expand=False, center=(320.5, 320.5))
        rgb = np.asarray(rotated, dtype=np.float32)[:, :, :3] + self.light
        moving = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
        region = Image.composite(moving, self.roi, self.visible)
        frame = self.base.copy()
        frame.paste(region, (DISC_X, DISC_Y))
        return frame


def process_video(source: Path, destination: Path, fps: int = 30,
                  turn_seconds: float = 6, loops: int = 1) -> bool:
    if source.resolve() == destination.resolve():
        print('[ERROR] 不能覆盖输入封面', file=sys.stderr)
        return False
    if fps <= 0 or not math.isfinite(turn_seconds) or turn_seconds <= 0 or loops < 1:
        print('[ERROR] fps、每圈秒数和圈数必须为正数', file=sys.stderr)
        return False
    frames_per_turn = fps * turn_seconds
    if not math.isclose(frames_per_turn, round(frames_per_turn), abs_tol=1e-8):
        print('[ERROR] fps × 每圈秒数必须为整数，以保证无缝循环', file=sys.stderr)
        return False
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        print('[ERROR] 找不到 ffmpeg', file=sys.stderr)
        return False
    process = None
    try:
        scene = Scene(load_cover(source))
        count = int(round(frames_per_turn)) * loops
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Encode beside the destination, atomically replacing only after successful completion.
        with tempfile.TemporaryDirectory(prefix='.v7-render-', dir=destination.parent) as work:
            output = Path(work) / 'render.mp4'
            command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y',
                       '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', f'{W}x{H}',
                       '-framerate', str(fps), '-i', 'pipe:0', '-an',
                       '-vf', 'scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p',
                       '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '2',
                       '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
                       '-color_range', 'tv', '-movflags', '+faststart', str(output)]
            with tempfile.TemporaryFile() as errors:
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                           stderr=errors)
                try:
                    for i in range(count):
                        frame = scene.frame(360 * (i % int(round(frames_per_turn))) / frames_per_turn)
                        process.stdin.write(frame.tobytes())
                        if i % fps == 0:
                            print(f'[FRAME] {i}/{count} {source.name}', flush=True)
                    process.stdin.close()
                    result = process.wait(timeout=120)
                except BaseException:
                    process.kill()
                    process.wait()
                    raise
                if result:
                    errors.seek(0)
                    raise OSError(errors.read().decode('utf-8', errors='replace')[-3000:])
            output.replace(destination)
        print(f'[OK] {destination} ({count / fps:g}s, {fps}fps)', flush=True)
        return True
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'[ERROR] {source}: {exc}', file=sys.stderr, flush=True)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description='V7 统一主色 / 黑胶旋转 MP4')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--test', type=Path, help='单张封面')
    mode.add_argument('--input', type=Path, help='封面目录，不递归')
    parser.add_argument('--output', type=Path, help='独立输出目录，默认 output/video_v7')
    parser.add_argument('--fps', type=int, choices=[24, 30, 60], default=30)
    parser.add_argument('--turn-seconds', type=float, default=6, help='每圈秒数，默认6')
    parser.add_argument('--loops', type=int, default=1, help='完整圈数，默认1')
    args = parser.parse_args()
    if not math.isfinite(args.turn_seconds) or args.turn_seconds <= 0 or args.loops < 1:
        parser.error('每圈秒数必须大于0，圈数至少为1')
    if not math.isclose(args.fps * args.turn_seconds, round(args.fps * args.turn_seconds), abs_tol=1e-8):
        parser.error('fps × 每圈秒数必须为整数')
    root = Path(__file__).resolve().parent
    output = args.output or root / 'output' / 'video_v7'
    if args.test:
        files = [args.test]
    else:
        source = args.input or root / 'cover_sources' / 'input'
        if not source.is_dir():
            parser.error(f'输入目录不存在: {source}')
        if source.resolve() == output.resolve():
            parser.error('输入与输出目录必须分开')
        files = sorted(p for p in source.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS)
    if not files:
        print('[WARN] 没有图片；请用 --input 指定歌单目录')
        return 0
    count = sum(process_video(p, output / (p.stem + '_v7.mp4'), args.fps,
                              args.turn_seconds, args.loops) for p in files)
    print(f'完成: {count}/{len(files)}', flush=True)
    return 0 if count == len(files) else 1


if __name__ == '__main__':
    raise SystemExit(main())
