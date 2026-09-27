"""Capture repeatable MAP01 water, CRT and exterior review frames."""
import argparse
import os
from pathlib import Path
import tempfile
import zipfile

from check_engine import ROOT, run_case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", default=os.environ.get("UTNT_ENGINE"),
                        required=not os.environ.get("UTNT_ENGINE"))
    parser.add_argument("--iwad", default=os.environ.get("UTNT_IWAD"),
                        required=not os.environ.get("UTNT_IWAD"))
    parser.add_argument("--mod", type=Path, default=ROOT / "zdcmp1")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        addon = Path(directory) / "visual.pk3"
        with zipfile.ZipFile(addon, "w") as archive:
            archive.write(ROOT / "tools/zdcmp1-tests/visual.zc", "zscript.zc")
            archive.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers="ZDCMP1VisualCheck" }\n')
        script = "con_notifytime 0; wait 35; "
        for index, name in enumerate(("water", "crt", "exterior")):
            script += (f"netevent zdcvisual {index}; wait 25; "
                       f"screenshot logs/zdc-visual-{name}.png; wait 5; ")
        script += "echo UTNT_TEST_END; quit\n"
        result = run_case(args.engine, args.iwad, mod=args.mod, addon=addon,
                          mapname="MAP01", playerclass="ZDCMPPlayer",
                          label="zdc-visual-review", timeout=60, commands=script,
                          settings=[("use_mouse", False), ("use_joystick", False),
                                    ("i_pauseinbackground", False),
                                    ("vid_activeinbackground", True)])
        if not result["ok"]:
            print(Path(result["log"]).read_text()[-5000:])
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
