"""Regression contracts for environment rendering data and GPU budgets."""
from pathlib import Path
import math
import re
import struct
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

class EnvironmentContracts(unittest.TestCase):
    def test_postprocess_parameters_fit_portable_push_constant_budget(self):
        for name in ("tutnt/GLDEFS.environment", "tools/fixtures/environment/GLDEFS"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for block in re.findall(r"HardwareShader PostProcess scene\s*\{([^}]+)\}", text):
                # Every scalar/vector is conservatively charged a full 16-byte slot.
                fields = re.findall(r"Uniform\s+(?:float|int|vec[234])\s+(\w+)", block)
                self.assertEqual(len(fields), len(set(fields)), name)
                self.assertLessEqual(len(fields) * 16, 128, name)

    def test_quantized_distance_is_conservative_and_float_exact(self):
        codes = []
        for distance in range(2049):
            code = math.floor(math.sqrt(distance / 2048) * 63)
            recovered = code * code * 2048 / 3969
            self.assertLessEqual(recovered, distance + 1e-9)
            self.assertLess(distance - recovered, 65)
            codes.append(code)
        for offset in range(0, len(codes) - 3):
            group = codes[offset:offset+4]
            packed = sum(code << (6 * j) for j, code in enumerate(group))
            as_float = struct.unpack("f", struct.pack("f", packed))[0]
            self.assertEqual(as_float, packed)
            self.assertEqual([int(as_float / 64**j) % 64 for j in range(4)], group)

    def test_dust_has_transparent_edges_and_bottom_pivot(self):
        path = ROOT / "tutnt/graphics/environment/mechanism-dust.png"
        with Image.open(path) as im:
            self.assertEqual(im.mode, "RGBA")
            w, h = im.size
            rim = [im.getpixel((x, y))[3] for x in range(w) for y in (0, h-1)]
            rim += [im.getpixel((x, y))[3] for y in range(h) for x in (0, w-1)]
            self.assertFalse(any(rim))
            self.assertGreater(im.getpixel((w//2, h//2))[3], 100)
        raw = path.read_bytes()
        marker = raw.index(b"grAb") + 4
        self.assertEqual(struct.unpack(">ii", raw[marker:marker+8]), (48, 96))

    def test_removed_scenic_lighting_has_no_runtime_references(self):
        for path in (ROOT / "tutnt").glob("LANGUAGE.*"):
            self.assertNotIn("UTNT_ENV_LIGHTS", path.read_text(encoding="utf-8"))
        self.assertFalse(list((ROOT / "tutnt/environment").glob("*-lights.txt")))
        self.assertNotIn("UTNTSceneLamp", (ROOT / "tutnt/zscript/UTNT_Environment.zc").read_text())

if __name__ == "__main__":
    unittest.main()
