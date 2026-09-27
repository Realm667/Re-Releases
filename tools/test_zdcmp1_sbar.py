"""Verify the native red-only SBAR mask preserves every non-red source pixel."""
import unittest

from PIL import Image
from build_zdcmp1_sbar import ROOT, generated, rectangles


class SBarMask(unittest.TestCase):
    def test_exact_red_coverage_without_overlap(self):
        with Image.open(ROOT / "zdcmp1/Graphics/sbar/stbar.png") as original:
            image = original.convert("RGBA")
        covered = set()
        for x, y, w, h in rectangles(image):
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    self.assertNotIn((xx, yy), covered)
                    covered.add((xx, yy))
        expected = {(x, y) for y in range(image.height) for x in range(image.width)
                    for r, g, b, a in [image.getpixel((x, y))]
                    if a > 0 and r > g * 2 + 8 and r > b * 2 + 8}
        self.assertEqual(covered, expected)
        self.assertGreater(len(covered), 4000)

    def test_generated_composition_is_current(self):
        self.assertIn(generated(), (ROOT / "zdcmp1/textures.txt").read_text())


if __name__ == "__main__":
    unittest.main()
