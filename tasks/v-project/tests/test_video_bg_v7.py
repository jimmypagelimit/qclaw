"""V7 animation invariants: only exposed vinyl moves; exact mathematical loop."""
import sys
from pathlib import Path
import unittest
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _gen_video_bg_v7 import Scene, DISC_X, DISC_Y, DISC_SIZE


class AnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cover = Image.new('RGB', (550, 550), (95, 60, 150))
        ImageDraw.Draw(cls.cover).rectangle((60, 180, 480, 360), fill=(210, 160, 50))
        cls.scene = Scene(cls.cover)

    def test_stationary_cover_and_background(self):
        frame = self.scene.frame(120)
        self.assertEqual(frame.crop((180, 265, 730, 815)).tobytes(), self.cover.tobytes())
        base = np.asarray(self.scene.base)
        animated = np.asarray(frame)
        changed = np.any(base != animated, axis=2)
        changed[DISC_Y:DISC_Y + DISC_SIZE, DISC_X:DISC_X + DISC_SIZE] = False
        self.assertFalse(changed.any())
        self.assertEqual(frame.crop((1100, 0, 1920, 1080)).tobytes(),
                         self.scene.base.crop((1100, 0, 1920, 1080)).tobytes())

    def test_record_moves_and_loops_without_changing_geometry(self):
        first = self.scene.frame(0)
        quarter = self.scene.frame(90)
        self.assertEqual(first.size, (1920, 1080))
        self.assertEqual(first.mode, 'RGB')
        self.assertNotEqual(first.tobytes(), quarter.tobytes())
        self.assertEqual(first.tobytes(), self.scene.frame(360).tobytes())
        self.assertEqual(quarter.tobytes(), self.scene.frame(450).tobytes())
        a, b = np.asarray(first), np.asarray(quarter)
        self.assertGreater(int(np.any(a != b, axis=2).sum()), 1000)
        # Adjacent frames across the loop should differ about as much as ordinary frames.
        last = np.asarray(self.scene.frame(358)).astype(float)
        next_frame = np.asarray(self.scene.frame(2)).astype(float)
        a = a.astype(float)
        cross_boundary = np.abs(last - a).mean()
        ordinary_step = np.abs(next_frame - a).mean()
        self.assertLess(cross_boundary, ordinary_step * 3 + .01)


if __name__ == '__main__':
    unittest.main()
