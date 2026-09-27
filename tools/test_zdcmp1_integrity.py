"""Fast, engine-independent release contracts for ZDCMP1."""
from pathlib import Path
import re
import tempfile
import unittest
import zipfile

from audit_campaign import udmf
from build_utnt import read_wad
from build_zdcmp1 import package, runtime_files
from check_engine import ROOT
from test_zdcmp1_stress import stress_fixture, commands


class ZDCMP1Integrity(unittest.TestCase):
    def test_max_defaults(self):
        text = (ROOT / "zdcmp1/cvarinfo.txt").read_text()
        self.assertRegex(text, r"server int ZDCMP1_fxquality\s*=\s*2\s*;")
        for name in ("motionblur", "ZDCMP1_heartbeat", "ZDCMP1_injuryoverlay", "ZDCMP1_weatherfx", "ZDCMP1_shaderoverlayswitch"):
            self.assertRegex(text, rf"\b{name}\s*=\s*true\s*;")

    def test_terrain_references_resolve(self):
        text = "\n".join(p.read_text() for p in (ROOT / "zdcmp1").glob("terrain*"))
        text = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)
        definitions = set(re.findall(r"(?im)^\s*terrain\s+(\w+)", text))
        uses = set(re.findall(r"(?im)^\s*floor\s+\S+\s+(\w+)", text))
        self.assertEqual(uses - definitions, set())

    def test_map_activation_has_no_unused_arguments(self):
        lumps = dict((n.rstrip(b"\0"), data) for n, data in read_wad(ROOT / "zdcmp1/Maps/map01.wad")[1])
        data = udmf(lumps[b"TEXTMAP"].decode())
        self.assertEqual(data["linedef"][23532]["special"], 130)
        self.assertEqual(data["linedef"][23532].get("arg0", 0), 0)
        for line in data["linedef"]:
            if line.get("special") == 130:
                self.assertTrue(all(line.get(f"arg{i}", 0) == 0 for i in range(1, 5)))

    def test_package_filters_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "mod"
            root.mkdir()
            for name in ("zscript.zc", "Maps/map01.wad", "#PSD/test.psd", ".codex/private.txt", "tools/check.py", "map.wad.backup1", ".DS_Store"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture")
            self.assertEqual({n for _, n in runtime_files(root)}, {"zscript.zc", "Maps/map01.wad"})
            a, b = Path(directory) / "a.pk3", Path(directory) / "b.pk3"
            package(root, a)
            package(root, b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            with self.assertRaises(ValueError):
                package(root, root / "recursive.pk3")

    def test_stress_fixture_lump_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            for scene in ("weather", "smoke", "fire", "gore", "mixed"):
                pk3 = Path(directory) / "test.pk3"
                stress_fixture(pk3, scene)
                with zipfile.ZipFile(pk3) as archive:
                    wad = Path(directory) / "map.wad"
                    wad.write_bytes(archive.read("maps/zdcftest.wad"))
                lumps = dict((n.rstrip(b"\0"), d) for n, d in read_wad(wad)[1])
                data = udmf(lumps[b"TEXTMAP"].decode())
                self.assertEqual(len(data["vertex"]), 4)
                self.assertEqual(data["sector"][0]["texturefloor"], "QLAVA" if scene in ("weather", "mixed") else "FLAT5_4")

    def test_soak_save_load_contract(self):
        script = commands("mixed", 1800, True)
        self.assertEqual(script.count("save zdc-soak-"), 10)
        self.assertEqual(script.count("load zdc-soak-"), 10)
        self.assertEqual(script.count("wait 6300;"), 10)
        self.assertIn("netevent zdcsnapshot; wait 5;", script)


if __name__ == "__main__":
    unittest.main()
