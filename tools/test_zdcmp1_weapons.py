"""Sustained weapon fire at both comfort extremes; optional movement baseline."""
import argparse
import json
import os
from pathlib import Path
import re
import tempfile
import zipfile

from check_engine import ROOT, run_case
from test_zdcmp1_effects import fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", default=os.environ.get("UTNT_ENGINE"), required=not os.environ.get("UTNT_ENGINE"))
    parser.add_argument("--iwad", default=os.environ.get("UTNT_IWAD"), required=not os.environ.get("UTNT_IWAD"))
    parser.add_argument("--mod", type=Path, default=ROOT / "zdcmp1")
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--renderer", choices=("0", "1"), default="1")
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory) / "base.pk3"
        addon = Path(directory) / "weapons.pk3"
        fixture(base)
        with zipfile.ZipFile(base) as source, zipfile.ZipFile(addon, "w") as archive:
            archive.writestr("maps/zdcftest.wad", source.read("maps/zdcftest.wad"))
            archive.write(ROOT / "tools/zdcmp1-tests/weapons.zc", "zscript.zc")
            archive.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers="ZDCMP1WeaponCheck" }\n')
        def run(mod, label, script):
            result = run_case(args.engine, args.iwad, mod=mod, addon=addon, mapname="ZDCFTEST",
                              renderer=args.renderer, playerclass="ZDCMPPlayer", label=label, timeout=90,
                              settings=[("use_mouse", False), ("use_joystick", False),
                                        ("i_pauseinbackground", False), ("vid_activeinbackground", True)],
                              commands=script + "echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit\n", regression=True)
            results.append(result)
            if not result["ok"]:
                raise RuntimeError(Path(result["log"]).read_text()[-7000:])
            return Path(result["log"]).read_text()
        weapon_samples = []
        for value in (0, 1, 2):
            setting = 1 if value else 0
            preset = "true" if value == 2 else "false"
            script = (f"unbindall; ZDCMP1_weaponflash {setting}; ZDCMP1_weaponshake {setting}; "
                      f"ZDCMP1_comfortpreset {preset}; wait 35; "
                      "netevent zdcwstart; wait 5; use Freezer; wait 70; +attack; wait 175; -attack; "
                      "wait 35; use NukeLauncher; wait 70; +altattack; wait 175; -altattack; "
                      "wait 35; netevent zdcwstop; wait 350; netevent zdcwcheck; wait 5; "
                      "netevent zdcwrocketstart; wait 5; +attack; wait 9; -attack; "
                      "wait 35; netevent zdcwrocketcheck; wait 5; ")
            text = run(args.mod, f"zdc-weapons-{args.renderer}-{value}", script)
            if results[-1]["assertions"] != 8:
                raise RuntimeError("Missing weapon assertions")
            weapon_samples.append(re.findall(r"ZDC_WEAPONS .*", text))
        if not weapon_samples[0] or any(sample != weapon_samples[0] for sample in weapon_samples[1:]):
            raise RuntimeError(f"Comfort settings changed weapon workload/ammo: {weapon_samples}")
        if args.compare:
            script = ("unbindall; wait 35; netevent zdcmove; +forward; wait 20; netevent zdcmove; "
                      "+jump; wait 8; netevent zdcmove; -jump; -forward; wait 35; netevent zdcmove; "
                      "+moveleft; wait 10; netevent zdcmove; -moveleft; wait 35; netevent zdcmove; wait 5; ")
            samples = []
            for name, mod in (("baseline", args.compare), ("current", args.mod)):
                text = run(mod, f"zdc-movement-{args.renderer}-{name}", script)
                samples.append(re.findall(r"ZDC_MOVE .*", text))
            if len(samples[0]) != 6 or samples[0] != samples[1]:
                raise RuntimeError(f"Movement differs: {samples}")
    (ROOT / "logs" / f"zdc-weapons-{args.renderer}-results.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
