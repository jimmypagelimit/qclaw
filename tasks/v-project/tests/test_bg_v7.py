"""Rendering invariants, without network or production inputs."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image, ImageDraw

spec = importlib.util.spec_from_file_location('bg_v7', Path(__file__).resolve().parents[1] / '_gen_batch_bg_v7.py')
v7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v7)


class RenderTests(unittest.TestCase):
    def test_cover_is_preserved_and_title_area_remains_quiet(self):
        cover = Image.new('RGB', (550, 550), (34, 100, 140))
        ImageDraw.Draw(cover).rectangle((90, 80, 430, 400), fill=(222, 171, 93))
        image = v7.render(cover)
        self.assertEqual(image.size, (1920, 1080))
        self.assertEqual(image.mode, 'RGB')
        self.assertEqual(image.crop((180, 265, 730, 815)).tobytes(), cover.tobytes())
        right = np.asarray(image)[200:880, 1150:1800]
        self.assertLess(float(np.quantile(right, .99)), 120)
        luminance = right @ np.array([.2126, .7152, .0722])
        self.assertLess(float(luminance.std()), 3)
        self.assertEqual(hashlib.sha256(image.tobytes()).digest(),
                         hashlib.sha256(v7.render(cover).tobytes()).digest())

    def test_filename_does_not_change_pixels_and_source_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            one, two = root / '封面 01.png', root / 'renamed.png'
            Image.new('RGBA', (700, 500), (130, 95, 160, 120)).save(one)
            two.write_bytes(one.read_bytes())
            self.assertEqual(v7.render(v7.load_cover(one)).tobytes(),
                             v7.render(v7.load_cover(two)).tobytes())
            before = one.read_bytes()
            self.assertFalse(v7.process_v7(one, one))
            self.assertEqual(one.read_bytes(), before)
            bad = root / 'corrupt.png'
            bad.write_bytes(b'not an image')
            self.assertFalse(v7.process_v7(bad, root / 'result.png'))
            self.assertFalse((root / 'result.png').exists())

    def test_background_really_tracks_album_hues(self):
        red = v7.render(Image.new('RGB', (550, 550), (190, 40, 30)))
        blue = v7.render(Image.new('RGB', (550, 550), (30, 70, 190)))
        red_mean = np.asarray(red)[60:210, 150:1050].mean(axis=(0, 1))
        blue_mean = np.asarray(blue)[60:210, 150:1050].mean(axis=(0, 1))
        self.assertGreater(float(red_mean[0] - red_mean[2]), 20)
        self.assertGreater(float(blue_mean[2] - blue_mean[0]), 20)
        mono = v7.render(Image.new('RGB', (550, 550), (160, 160, 160)))
        mono_mean = np.asarray(mono)[60:210, 150:1050].mean(axis=(0, 1))
        self.assertLess(float(mono_mean.max() - mono_mean.min()), 6)

    def test_background_has_no_left_right_colour_split(self):
        cover = Image.new('RGB', (550, 550), (190, 50, 35))
        ImageDraw.Draw(cover).rectangle((275, 0, 549, 549), fill=(25, 90, 180))
        ambient, _ = v7.palette(cover)
        image = np.asarray(v7.background(cover, ambient, np.random.default_rng(42)), dtype=float)
        left = image[:, :640].mean(axis=(0, 1))
        right = image[:, -640:].mean(axis=(0, 1))
        self.assertLess(float(np.abs(left - right).max()), .2)
        self.assertLess(float(np.abs(image[:, 950].mean(axis=0) - left).max()), 3)

    def test_exif_rotation_is_applied_before_square_crop(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'oriented.jpg'
            image = Image.new('RGB', (60, 100), 'navy')
            ImageDraw.Draw(image).rectangle((0, 0, 29, 99), fill='orange')
            exif = image.getexif()
            exif[274] = 6
            image.save(path, exif=exif)
            result = v7.load_cover(path)
            self.assertEqual(result.size, (550, 550))
            self.assertGreater(result.getpixel((275, 20))[0], 150)
            self.assertLess(result.getpixel((275, 530))[0], 50)


if __name__ == '__main__':
    unittest.main()
