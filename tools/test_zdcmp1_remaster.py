"""Real MAP01 hint, preview, save/load and finale tests plus menu screenshots."""
import argparse
import json
import os
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
    parser.add_argument("--full-finale", action="store_true", help="Also let the entire credits sequence finish naturally")
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory() as directory:
        addon = Path(directory) / "remaster.pk3"
        with zipfile.ZipFile(addon, "w") as archive:
            archive.write(ROOT / "tools/zdcmp1-tests/remaster.zc", "zscript.zc")
            archive.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers="ZDCMP1RemasterCheck", "ZDCMP1MenuCheck" }\n')
        scripts = {
            "story": ("wait 35; netevent zdcrstart; wait 185; netevent zdcrpreview; wait 2; "
                      "save zdc-remaster; wait 5; load zdc-remaster; wait 5; netevent zdcrpreview; "
                      "wait 180; netevent zdcrreturn; wait 5; netevent zdcrshared; wait 5; netevent zdcrmetrics; wait 5; "
                      "openmenu ZDCMP1JournalMenu; wait 10; event zdcuimenu 0; screenshot logs/zdc-journal.png; wait 5; "),
            "finale": ("wait 35; netevent zdcrfinale; wait 5; netevent zdcrfinalecheck; wait 5; "
                       "save zdc-finale; wait 5; load zdc-finale; wait 5; netevent zdcrfinalecheck; "
                       "ZDCMP1_skippablefinale false; wait 35; netevent zdcrblocked; "
                       "wait 5; netevent zdcrstillhere; "
                       "ZDCMP1_skippablefinale true; wait 35; netevent zdcrskip; "
                       "wait 70; netevent zdcrreportcheck; screenshot logs/zdc-finale-exit.png; wait 5; "),
            "credits-skip": ("wait 35; netevent zdcrcredits; wait 35; netevent zdcrfinalecheck; "
                             "+use; wait 3; -use; wait 70; netevent zdcrreportcheck; wait 5; "),
        }
        if args.full_finale:
            scripts["credits"] = ("ZDCMP1_skippablefinale false; wait 35; netevent zdcrfinale; wait 5; netevent zdcrfinalecheck; "
                                  "wait 400; +use; wait 2; -use; wait 10000; screenshot logs/zdc-credits-exit.png; wait 5; ")
        for name, script in scripts.items():
            result = run_case(args.engine, args.iwad, mod=args.mod, addon=addon, mapname="MAP01",
                              renderer=args.renderer, playerclass="ZDCMPPlayer", label=f"zdc-remaster-{name}-{args.renderer}",
                              timeout=400 if name == "credits" else 90, regression=True,
                              settings=[("use_mouse", False), ("use_joystick", False),
                                        ("i_pauseinbackground", False), ("vid_activeinbackground", True)],
                              commands=script + "echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit\n")
            expected = {"story": 24, "finale": 8, "credits-skip": 3, "credits": 3}[name]
            if result["assertions"] != expected:
                result["ok"] = False
                result["errors"].append(f"expected {expected} assertions")
            results.append(result)
            if not result["ok"]:
                print(Path(result["log"]).read_text()[-7000:])
                break
        if all(r["ok"] for r in results):
            script = "wait 35; "
            for name in ("Options", "Display", "HUD", "Audio", "Comfort", "Hints", "Effects"):
                script += (f"openmenu ZDCMP1{name}Menu; wait 5; event zdcuimenu 1; "
                           f"screenshot logs/zdc-menu-{name}-{args.renderer}.png; wait 5; closemenu; wait 5; ")
            result = run_case(args.engine, args.iwad, mod=args.mod, addon=addon, mapname="MAP01",
                              renderer=args.renderer, playerclass="ZDCMPPlayer", label=f"zdc-remaster-menus-{args.renderer}",
                              timeout=60, regression=True,
                              settings=[("use_mouse", False), ("use_joystick", False),
                                        ("i_pauseinbackground", False), ("vid_activeinbackground", True)],
                              commands=script + "echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit\n")
            result["ok"] = result["ok"] and result["assertions"] == 7
            results.append(result)
    (ROOT / "logs" / f"zdc-remaster-{args.renderer}-results.json").write_text(json.dumps(results, indent=2) + "\n")
    return 0 if len(results) == (5 if args.full_finale else 4) and all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
