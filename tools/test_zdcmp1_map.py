"""MAP01 startup/save-load on all five skills. Not a full-map playthrough."""
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
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory() as directory:
        addon = Path(directory) / "map-check.pk3"
        with zipfile.ZipFile(addon, "w") as archive:
            archive.write(ROOT / "tools/zdcmp1-tests/map-check.zc", "zscript.zc")
            archive.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers="ZDCMP1MapCheck" }\n')
        for skill in range(5):
            label = f"zdc-map-{args.renderer}-skill{skill}"
            commands = (f"unbindall; wait 70; netevent zdcmapcheck; wait 5; save zdc-map; wait 10; "
                        f"load zdc-map; wait 70; netevent zdcmapcheck; wait 5; screenshot logs/{label}.png; "
                        "wait 5; echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit\n")
            result = run_case(args.engine, args.iwad, mod=args.mod, addon=addon, mapname="MAP01",
                              renderer=args.renderer, playerclass="ZDCMPPlayer", label=label,
                              timeout=90, commands=commands, regression=True,
                              settings=[("skill", skill), ("use_mouse", False), ("use_joystick", False),
                                        ("i_pauseinbackground", False), ("vid_activeinbackground", True)])
            text = Path(result["log"]).read_text()
            if result["assertions"] != 6:
                result["ok"] = False
                result["errors"].append("missing map assertions")
            for warning in ("Unknown terrain", "Line 23532", "Unknown class", "Unknown texture"):
                if warning in text:
                    result["ok"] = False
                    result["errors"].append(warning)
            results.append(result)
            if not result["ok"]:
                print(text[-6000:])
                break
    (ROOT / "logs" / f"zdc-map-{args.renderer}-results.json").write_text(json.dumps(results, indent=2) + "\n")
    if len(results) != 5 or not all(r["ok"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
