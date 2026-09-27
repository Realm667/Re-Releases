"""Native automap markers, quest transitions, save/load and SBAR skin regression."""
import argparse
import os
from pathlib import Path
import sys
import tempfile
import zipfile

from check_engine import ROOT, run_case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", default=os.environ.get("UTNT_ENGINE"), required=not os.environ.get("UTNT_ENGINE"))
    parser.add_argument("--iwad", default=os.environ.get("UTNT_IWAD"), required=not os.environ.get("UTNT_IWAD"))
    parser.add_argument("--mod", type=Path, default=ROOT / "zdcmp1")
    parser.add_argument("--renderer", choices=("0", "1"), default="1")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        addon = Path(directory) / "automap.pk3"
        with zipfile.ZipFile(addon, "w") as archive:
            archive.write(ROOT / "tools/zdcmp1-tests/automap.zc", "zscript.zc")
            archive.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers="ZDCMapCheck", "ZDCMapUICheck" }\n')
        script = "con_notifytime 0; language de; wait 35; "
        if sys.platform == "darwin":
            script += "vid_hidpi false; wait 35; "
        # Geometry reveal is restricted to screenshot fixtures; runtime never sets am_cheat.
        script += (
            "vid_setsize 1280 720; wait 35; netevent zdcmapseed; wait 5; save zdc-map; wait 5; "
            "load zdc-map; wait 35; netevent zdcmapsaved; wait 5; am_overlay 0; am_cheat 1; "
            "togglemap; wait 10; event zdcmapui 0; screenshot logs/zdc-map.png; wait 5; "
            "am_rotate 1; wait 10; screenshot logs/zdc-map-rotated.png; wait 5; "
            "am_rotate 0; am_gobig; wait 10; screenshot logs/zdc-map-overview.png; wait 5; "
            "togglemap; am_overlay 1; togglemap; wait 10; event zdcmapui 1; "
            "screenshot logs/zdc-map-overlay.png; wait 5; togglemap; "
            "netevent zdcmapprogress; wait 5; ZDCMP1_mapcompleted true; wait 5; netevent zdcmapcomplete; "
            "wait 5; ZDCMP1_mapmarkers false; wait 5; netevent zdcmapdisabled; wait 5; "
            "echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit\n")
        result = run_case(args.engine, args.iwad, mod=args.mod, addon=addon, mapname="MAP01",
                          renderer=args.renderer, playerclass="ZDCMPPlayer", label=f"zdc-map-{args.renderer}",
                          timeout=60, regression=True, commands=script,
                          settings=[("use_mouse", False), ("use_joystick", False),
                                    ("i_pauseinbackground", False), ("vid_activeinbackground", True)])
        if not result["ok"] or result["assertions"] != 24:
            print(Path(result["log"]).read_text()[-9000:])
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
