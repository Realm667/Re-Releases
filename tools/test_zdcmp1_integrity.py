"""Fast, engine-independent release contracts for ZDCMP1."""
from pathlib import Path
import hashlib
import re
import struct
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
        self.assertIn("user float ZDCMP1_weaponflash = 1.0;", text)
        self.assertIn("server bool ZDCMP1_weaponshake = true;", text)

    def test_map_source_and_geometry_contract(self):
        lumps = dict((n.rstrip(b"\0"), d) for n, d in read_wad(ROOT / "zdcmp1/Maps/map01.wad")[1])
        self.assertEqual(lumps[b"SCRIPTS"], (ROOT / "zdcmp1/source/maps/map01.acs").read_bytes().replace(b"\r\n", b"\n"))
        for name, digest in {
            b"TEXTMAP": "ffc7616ae08789a9a584e9efa8ee05612cf1c992e32bfb075ed8612f44ee6b52",
            b"ZNODES": "0d781b7ba95f742303c8211cca61af5de5264d17ef9482c1de5e9d832f9f92f5",
        }.items():
            self.assertEqual(hashlib.sha256(lumps[name]).hexdigest(), digest)

    def test_skybox_cube_contract(self):
        root = ROOT / "zdcmp1"
        lumps = dict((n.rstrip(b"\0"), d) for n, d in read_wad(root / "Maps/map01.wad")[1])
        data = udmf(lumps[b"TEXTMAP"].decode())
        for sector, ceiling, top, bottom in (
            (740, 464, "ZD_TOP", "ZD_BOT"),
            (2635, 312, "ZH_TOP", "ZH_BOT"),
        ):
            box = data["sector"][sector]
            self.assertEqual(box["special"], 90)
            self.assertEqual(box["heightceiling"], ceiling)
            self.assertEqual(box["textureceiling"], top)
            self.assertEqual(box["texturefloor"], bottom)
        self.assertEqual(data["thing"][265]["height"], 156.0)
        self.assertEqual(data["thing"][1292]["height"], 156.0)
        self.assertEqual(data["thing"][1292]["x"], 3812.0)
        mapinfo = (root / "mapinfo.def").read_text()
        map01 = mapinfo.split('map MAP01 "ZDoom Community Map #1"', 1)[1].split("}", 1)[0]
        self.assertIn("disableskyboxao", map01)
        groups = (
            ("ZD", (("N", (6950, 6952)), ("W", (6964, 6954)),
                    ("S", (6962, 6956)), ("E", (6960, 6958)))),
            ("ZH", (("N", (31226, 31239)), ("W", (32360, 31233)),
                    ("S", (31230, 31237)), ("E", (31228, 31235)))),
        )
        for prefix, faces in groups:
            for face, sides in faces:
                for half, index in enumerate(sides):
                    side = data["sidedef"][index]
                    self.assertEqual(side["texturemiddle"], f"{prefix}_{face}{half}")
                    self.assertEqual(side.get("offsetx", 0), 0)
                    self.assertEqual(side.get("offsety", 0), 0)
                    self.assertTrue(side["nofakecontrast"])
        # Self-referencing wall rings must face the camera. A mirrored ring
        # renders its untextured backs, hiding the landscape in the Hell sky.
        for sector, camera, bounds in ((740, (2848, 2272), (2688, 3008, 2112, 2432)),
                                       (2635, (3812, -2272), (3652, 3972, -2432, -2112))):
            points = []
            for line in data["linedef"]:
                side = data["sidedef"][line["sidefront"]]
                if side["sector"] != sector:
                    continue
                a, b = (data["vertex"][line[k]] for k in ("v1", "v2"))
                points.extend((a, b))
                if side.get("texturemiddle", "").startswith(("ZD_", "ZH_")):
                    cross = ((b["x"]-a["x"])*(camera[1]-a["y"])
                             -(b["y"]-a["y"])*(camera[0]-a["x"]))
                    self.assertLess(cross, 0)
            self.assertEqual((min(p["x"] for p in points), max(p["x"] for p in points),
                              min(p["y"] for p in points), max(p["y"] for p in points)), bounds)
        textures = (root / "textures.txt").read_text()
        animations = (root / "animdefs.def").read_text()
        for prefix, name in (("ZD", "outdoor"), ("ZH", "hell")):
            self.assertIn(f"flat {prefix}_TOP", animations)
            for frame in range(8):
                label = f"{prefix}_TOP" if frame == 0 else f"{prefix}_T{frame:02d}"
                self.assertIn(f"Flat {label}, 1024, 1024", textures)
                self.assertIn(f"pic {label} tics 20", animations)
                self.assertTrue((root / "PATCHES/skybox/cube" / f"{name}-top-{frame:02d}.png").is_file())
            for face in "nwse":
                for half in (0, 1):
                    self.assertTrue((root / "PATCHES/skybox/cube" / f"{name}-{face}{half}.png").is_file())
            self.assertTrue((root / "source/art/skybox" / f"{name}-source.png").is_file())

    def test_consolidated_options_and_release_references(self):
        menu = (ROOT / "zdcmp1/menudef.txt").read_text()
        for parent in ("OptionsMenu", "OptionsMenuSimple"):
            block = re.search(r'AddOptionMenu "' + parent + r'"\s*\{([^}]+)\}', menu)[1]
            self.assertEqual(block.count("Submenu"), 1)
            self.assertIn('"ZDCMP1OptionsMenu"', block)
        self.assertNotIn('protected', menu)
        self.assertFalse((ROOT / "zdcmp1/menudef.zsimple").exists())
        cvars = (ROOT / "zdcmp1/cvarinfo.txt").read_text()
        for name in ("ZDCMP1_weaponflash", "ZDCMP1_weaponshake", "ZDCMP1_skippablefinale", "ZDCMP1_logbook", "ZDCMP1_footstepvolume"):
            self.assertIn('"' + name + '"', menu)
            self.assertIn(name, cvars)
        self.assertIn('statscreen_single = "ZPackStatusScreen"', (ROOT / "zdcmp1/mapinfo.def").read_text())
        self.assertIn('class ZPackStatusScreen', (ROOT / "zdcmp1/zscript/ZDCMP1_Inter.zc").read_text())

    def test_remaster_localization(self):
        language = (ROOT / "zdcmp1/language.enu").read_text()
        keys = set(re.findall(r'(?m)^(\w+)\s*=', language))
        for path in (ROOT / "zdcmp1/menudef.txt", ROOT / "zdcmp1/zscript/ZDCMP1_Remaster.zc", ROOT / "zdcmp1/zscript/ZDCMP1_Logbook.zc", ROOT / "zdcmp1/zscript/ZDCMP1_Automap.zc", ROOT / "zdcmp1/zscript/ZDCMP1_Results.zc"):
            references = set(re.findall(r'\$(ZDC_[A-Z0-9_]+)(?=["\s])', path.read_text()))
            self.assertFalse(references - keys)
        self.assertTrue(all(f"ZDC_HINT{i}" in keys for i in range(13)))
        german = set(re.findall(r'(?m)^(\w+)\s*=', (ROOT / "zdcmp1/language.deu").read_text()))
        for prefix in ("ZDC_TITLE", "ZDC_BODY", "ZDC_SOURCE", "ZDC_STATE"):
            for i in range(13):
                self.assertIn(f"{prefix}{i}", keys & german)
        self.assertTrue(all(key in german for key in keys if key.startswith("ZDC_RESULT_")))

    def test_map01_completion_report_contract(self):
        mapinfo = (ROOT / "zdcmp1/mapinfo.def").read_text()
        map01 = mapinfo.split('map MAP01 "ZDoom Community Map #1"', 1)[1].split("cluster 1", 1)[0]
        self.assertIn("nointermission", map01)
        self.assertIn('"ZDCMP1Results"', mapinfo)
        acs = (ROOT / "zdcmp1/source/maps/map01.acs").read_text()
        self.assertEqual(acs.count("acs_execute(271,0)"), 3)
        self.assertIn('ScriptCall("ZDCMP1Results", "Begin")', acs)
        self.assertIn('script "ZDC_ShowCredits"', acs)
        results = (ROOT / "zdcmp1/zscript/ZDCMP1_Results.zc").read_text()
        for metric in ("healthLost", "distanceUnits", "ammoSpent", "shots", "hits", "frozenTime",
                       "frozenKills", "frozenItems", "frozenSecrets", "frozenTotalMonsters",
                       "frozenTotalItems", "frozenTotalSecrets"):
            self.assertIn(metric, results)
        self.assertIn("distanceUnits[i] / 64.", results)
        self.assertNotIn("deathcount", results)
        self.assertTrue((ROOT / "zdcmp1/Graphics/ZDCRESBG.png").exists())

    def test_logbook_option_ownership(self):
        menu = (ROOT / "zdcmp1/menudef.txt").read_text()
        block = re.search(r'OptionMenu "ZDCMP1HintsMenu"\s*\{([^}]+)\}', menu)[1]
        cvars = (ROOT / "zdcmp1/cvarinfo.txt").read_text()
        for name in ("logbook", "hintnotifications", "hintsize", "hintduration", "hintposition", "hintsound"):
            self.assertIn(f'"ZDCMP1_{name}"', block)
            self.assertRegex(cvars, rf'user (?:bool|int) ZDCMP1_{name}\s*=')
        self.assertIn('user int ZDCMP1_hintduration = 6;', cvars)
        self.assertEqual(menu.count('Control "$ZDC_JOURNAL"'), 1)

    def test_automap_anchors_and_skin(self):
        lumps = dict((n.rstrip(b"\0"), d) for n, d in read_wad(ROOT / "zdcmp1/Maps/map01.wad")[1])
        data = udmf(lumps[b"TEXTMAP"].decode())
        for index, expected_id, expected_script in ((6183, 56, None), (4080, None, 8),
                (16183, None, 9), (15634, 4, None), (26576, None, 45), (23199, None, 52)):
            line = data["linedef"][index]
            if expected_id is not None:
                self.assertEqual(line["id"], expected_id)
            if expected_script is not None:
                self.assertEqual((line["special"], line["arg0"]), (80, expected_script))
        gear = next(t for t in data["thing"] if t.get("id") == 13)
        self.assertEqual((gear["x"], gear["y"]), (1120, 352))
        textures = (ROOT / "zdcmp1/textures.txt").read_text()
        self.assertIn('Graphic ZDCBOT, 32, 3 { Patch ZDCTOP, 0, 0 { FlipY } }', textures)
        self.assertIn('Graphic ZDCDISPLAY, 32, 16 { Patch STBAR, -8, -5 }', textures)
        menu = (ROOT / "zdcmp1/menudef.txt").read_text()
        block = re.search(r'OptionMenu "ZDCMP1AutomapMenu"\s*\{([^}]+)\}', menu)[1]
        for name in ("ZDCMP1_mapmarkers", "ZDCMP1_mapcompleted", "am_customcolors"):
            self.assertIn('"' + name + '"', block)

    def test_navigation_anchors_and_option(self):
        lumps = dict((n.rstrip(b"\0"), d) for n, d in read_wad(ROOT / "zdcmp1/Maps/map01.wad")[1])
        data = udmf(lumps[b"TEXTMAP"].decode())
        self.assertEqual((data["linedef"][15012]["special"], data["linedef"][15012]["arg0"]), (80, 18))
        console = data["thing"][1966]
        self.assertEqual((console["x"], console["y"], console["special"], console["arg0"]),
                         (5056, 824, 80, 46))
        menu = (ROOT / "zdcmp1/menudef.txt").read_text()
        cvars = (ROOT / "zdcmp1/cvarinfo.txt").read_text()
        self.assertIn('"ZDCMP1_wayfinding"', menu)
        self.assertIn('user bool ZDCMP1_wayfinding = true;', cvars)
        self.assertIn('#include "zscript/ZDCMP1_Navigation.zc"',
                      (ROOT / "zdcmp1/zscript.zc").read_text())
        for name in ("zdcmapbg", "zdcmapgo", "zdnav0"):
            self.assertTrue((ROOT / f"zdcmp1/Graphics/hud/{name}.png").exists())

    def test_terrain_references_resolve(self):
        text = "\n".join(p.read_text() for p in (ROOT / "zdcmp1").glob("terrain*"))
        text = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)
        definitions = set(re.findall(r"(?im)^\s*terrain\s+(\w+)", text))
        uses = set(re.findall(r"(?im)^\s*floor\s+\S+\s+(\w+)", text))
        self.assertEqual(uses - definitions, set())

    def test_remaster_assets_and_controls(self):
        root = ROOT / "zdcmp1"
        for manifest in (root / "zscript.zc", root / "gldefs.txt", root / "modeldef.txt",
                         root / "gldefs/brightm.txt"):
            for include in re.findall(r'(?m)^#include\s+"?([^"\s]+)"?', manifest.read_text()):
                self.assertTrue((root / include).is_file(), f"{manifest.name}: {include}")
        shaders = (root / "gldefs/shaders.txt").read_text()
        for path in re.findall(r'Shader "(shaders/zdc_[^"]+)"', shaders):
            self.assertTrue((root / path).is_file(), path)
        brightmaps = (root / "gldefs/remaster.txt").read_text()
        for texture, path in re.findall(r'brightmap texture (SCREEN[123]) \{ map "([^"]+)" \}', brightmaps):
            source = root / "Textures" / f"{texture}.png"
            target = root / path
            self.assertEqual(source, target)
            image = target.read_bytes()
            self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", image[16:24]), (128, 104))
        self.assertNotIn("warp flat WATER", (root / "animdefs.def").read_text())
        menu = (root / "menudef.txt").read_text()
        cvars = (root / "cvarinfo.txt").read_text()
        for name in ("ZDCMP1_interactionprompts", "ZDCMP1_comfortpreset"):
            self.assertIn(f'"{name}"', menu)
            self.assertIn(f"user bool {name}", cvars)
        self.assertIn('Control "$ZDC_PING", "netevent zdc_ping"', menu)
        self.assertIn("class OblivionTelegraph", (root / "zscript/monsters/ZDCMP1_Oblivion.zc").read_text())
        acs = (root / "source/maps/map01.acs").read_text()
        self.assertIn('script "ZDC_MilestoneAutosave"', acs)
        self.assertIn('set != lastSoloCheckpoint', acs)

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
