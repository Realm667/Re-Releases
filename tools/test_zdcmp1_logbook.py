"""Field-terminal input, state, notification and bilingual layout regression."""
import argparse
import os
import sys
from pathlib import Path
import tempfile
import zipfile

from check_engine import ROOT, run_case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", default=os.environ.get("UTNT_ENGINE"), required=not os.environ.get("UTNT_ENGINE"))
    parser.add_argument("--iwad", default=os.environ.get("UTNT_IWAD"), required=not os.environ.get("UTNT_IWAD"))
    parser.add_argument("--mod", type=Path, default=ROOT / "zdcmp1")
    parser.add_argument("--renderer", choices=("0", "1"), default="1")
    parser.add_argument("--visual-matrix", action="store_true", help="Also verify 16:9, 4:3 and ultrawide window sizes")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        addon = Path(directory) / "logbook.pk3"
        with zipfile.ZipFile(addon, "w") as archive:
            archive.write(ROOT / "tools/zdcmp1-tests/logbook.zc", "zscript.zc")
            archive.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers="ZDCFieldCheck", "ZDCFieldUICheck" }\n')
        script = (
            "language enu; con_notifytime 0; wait 35; netevent zdcfieldseed; wait 35; event zdcfieldqueue; "
            "screenshot logs/zdc-field-notice.png; wait 210; event zdcfieldadvanced 2 2; "
            "screenshot logs/zdc-field-gear-notice.png; wait 210; event zdcfieldadvanced 1 5; "
            "screenshot logs/zdc-field-power-notice.png; wait 5; openmenu ZDCMP1JournalMenu; wait 10; "
            "event zdcfieldnavigate; wait 10; event zdcfieldpaused; screenshot logs/zdc-field-journal.png; wait 5; closemenu; "
            "wait 35; netevent zdcfieldread; wait 35; save zdc-field; wait 35; load zdc-field; wait 35; "
            "netevent zdcfieldread; wait 35; netevent zdcfieldall; wait 35; openmenu ZDCMP1JournalMenu; "
            "wait 10; event zdcfieldscroll; ZDCMP1_hintsize 2; wait 5; event zdcfieldlayout 0; "
            "screenshot logs/zdc-field-large-en.png; wait 5; language de; wait 5; event zdcfieldlayout 0; "
            "screenshot logs/zdc-field-large-de.png; wait 5; closemenu; fullhud_statspos 0; wait 35; "
            "event zdcfieldlayout 1; screenshot logs/zdc-field-notice-de.png; wait 5; "
            "ZDCMP1_logbook false; ZDCMP1_hintnotifications false; wait 35; openmenu ZDCMP1JournalMenu; "
            "wait 5; event zdcfieldhidden; screenshot logs/zdc-field-hidden.png; wait 5; "
            "echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit\n")
        result = run_case(args.engine, args.iwad, mod=args.mod, addon=addon, mapname="MAP01",
                          renderer=args.renderer, playerclass="ZDCMPPlayer", label=f"zdc-field-{args.renderer}",
                          timeout=90, regression=True, commands=script,
                          settings=[("use_mouse", False), ("use_joystick", False),
                                    ("i_pauseinbackground", False), ("vid_activeinbackground", True)])
        if not result["ok"] or result["assertions"] != 32:
            print(Path(result["log"]).read_text()[-9000:])
            return 1
        if args.visual_matrix:
            script = ("con_notifytime 0; wait 35; netevent zdcfieldseed; wait 35; netevent zdcfieldall; "
                      "wait 35; language de; ZDCMP1_hintsize 2; openmenu ZDCMP1JournalMenu; wait 10; ")
            if sys.platform == "darwin":
                script += "vid_hidpi false; wait 35; "
            for width, height in ((1280, 720), (960, 720), (1680, 720)):
                script += (f"vid_setsize {width} {height}; wait 35; event zdcfieldviewport {width} {height}; "
                           f"screenshot logs/zdc-field-{width}x{height}.png; wait 5; ")
            result = run_case(args.engine, args.iwad, mod=args.mod, addon=addon, mapname="MAP01",
                              renderer=args.renderer, playerclass="ZDCMPPlayer", label=f"zdc-field-views-{args.renderer}",
                              timeout=60, regression=True,
                              commands=script + "echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit\n",
                              settings=[("use_mouse", False), ("use_joystick", False),
                                        ("i_pauseinbackground", False), ("vid_activeinbackground", True)])
            if not result["ok"] or result["assertions"] != 9:
                print(Path(result["log"]).read_text()[-9000:])
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
