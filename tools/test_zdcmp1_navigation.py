"""Native MAP01 route, teleporter, collision and HUD checks."""

import argparse
import os
from pathlib import Path
import sys
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
    parser.add_argument("--renderer", choices=("0", "1"), default="1")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        addon = Path(directory) / "navigation.pk3"
        with zipfile.ZipFile(addon, "w") as archive:
            archive.write(ROOT / "tools/zdcmp1-tests/navigation.zc", "zscript.zc")
            archive.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers="ZDCNavigationCheck", "ZDCNavigationUICheck" }\n')
        script = "con_notifytime 0; language de; wait 35; "
        if sys.platform == "darwin":
            script += "vid_hidpi false; wait 35; "
        script += (
            "vid_setsize 1280 720; ZDCMP1_hintnotifications false; wait 35; "
            "netevent zdcnavseed; wait 10; "
            "screenshot logs/zdc-navigation-hud.png; netevent zdcnavturn; wait 5; "
            "screenshot logs/zdc-navigation-turned.png; save zdc-nav; wait 5; "
            "load zdc-nav; wait 35; netevent zdcnavsaved; wait 5; event zdcnavui; wait 5; "
            "ZDCMP1_wayfinding false; wait 5; event zdcnavoff; "
            "screenshot logs/zdc-navigation-off.png; wait 5; "
            "netevent zdcnavspawn; wait 5; "
            "echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit\n"
        )
        result = run_case(args.engine, args.iwad, mod=args.mod, addon=addon, mapname="MAP01",
                          renderer=args.renderer, playerclass="ZDCMPPlayer",
                          label=f"zdc-navigation-{args.renderer}", timeout=60,
                          regression=True, commands=script,
                          settings=[("use_mouse", False), ("use_joystick", False),
                                    ("i_pauseinbackground", False), ("vid_activeinbackground", True)])
        if not result["ok"] or result["assertions"] != 18:
            print(Path(result["log"]).read_text()[-9000:])
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
