"""UZDoom 5.0.3 parse, map, actor, and save/load smoke checks for ZDCMP2."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile
import time
import zipfile

from check_engine import ROOT, run_case


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", default=os.environ.get("UTNT_ENGINE"), required=not os.environ.get("UTNT_ENGINE"))
    parser.add_argument("--iwad", default=os.environ.get("UTNT_IWAD"), required=not os.environ.get("UTNT_IWAD"))
    parser.add_argument("--mod", type=Path, default=ROOT / "tutnt/.codex/builds/zdcmp2-release.pk3")
    parser.add_argument("--acc", type=Path, required=True)
    parser.add_argument("--renderer", choices=("0", "1"), default="1")
    args = parser.parse_args()
    local = ROOT / "tutnt/.codex"
    local.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.mod) as archive:
        names = {name.lower() for name in archive.namelist()}
        required = {"zscript.zc", "mapinfo.def", "acs/zdcmp2.o", "actors/weapons.zc", "maps/zdcmp2.wad"}
        if not required <= names or "decorate.txt" in names:
            raise SystemExit(f"Bad package layout: missing {sorted(required - names)}")
        if archive.testzip():
            raise SystemExit("Corrupt PK3")

    label = f"zdcmp2-5-parse-{args.renderer}"
    parsed = run_case(args.engine, args.iwad, root=local, mod=args.mod, label=label, timeout=60)
    parse_log = Path(parsed["log"]).read_text(errors="replace")
    if not parsed["ok"] or "Script warning," in parse_log or "Unknown flat " in parse_log:
        raise SystemExit(f"UZDoom parse failed: {parsed['log']}")

    label = f"zdcmp2-5-map-{args.renderer}"
    map_started = time.time()
    commands = ("god; notarget; wait 70; give Nailgun; use Nailgun; summon HellWarrior; "
                "summon PlasmaGlobe; wait 35; save zdcmp2-smoke; wait 10; "
                "load zdcmp2-smoke; wait 70; echo UTNT_TEST_END; quit\n")
    played = run_case(args.engine, args.iwad, root=local, mod=args.mod,
                      mapname="ZDCMP2", playerclass="ZDCMP2Player",
                      renderer=args.renderer, label=label, timeout=120,
                      commands=commands,
                      settings=[("i_pauseinbackground", False),
                                ("vid_activeinbackground", True)])
    if not played["ok"]:
        raise SystemExit(f"UZDoom runtime failed: {played['log']}")
    smoke_save = local / "logs/saves/zdcmp2-smoke.zds"
    if not smoke_save.exists() or smoke_save.stat().st_mtime < map_started - 1:
        raise SystemExit(f"Save command produced no fresh game: {smoke_save}")

    fixture = ROOT / "tools/fixtures/zdcmp2/message_fixture.acs"
    overlay = local / "builds/zdcmp2-message-test.pk3"
    overlay.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="zdcmp2-test-acs-") as directory:
        output = Path(directory) / "z2test.o"
        subprocess.run([str(args.acc.resolve()), "-i", str(args.acc.resolve().parent),
                        "-i", str(ROOT / "zdcmp2/source"), str(fixture), str(output)],
                       cwd=directory, check=True, capture_output=True)
        with zipfile.ZipFile(overlay, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(output, "acs/z2test.o")
            archive.writestr("loadacs.txt", (ROOT / "zdcmp2/loadacs.txt").read_text() + "\nz2test\n")
    label = f"zdcmp2-5-message-{args.renderer}"
    message_started = time.time()
    notified = run_case(args.engine, args.iwad, root=local, mod=args.mod, addon=overlay,
                        mapname="ZDCMP2", playerclass="ZDCMP2Player",
                        renderer=args.renderer, label=label, timeout=90,
                        commands=("wait 35; pukename ZDCMP2TestNotify; wait 35; "
                                  "save zdcmp2-message; wait 10; load zdcmp2-message; "
                                  "wait 300; echo UTNT_TEST_END; quit\n"),
                        settings=[("i_pauseinbackground", False),
                                  ("vid_activeinbackground", True)])
    notification_log = Path(notified["log"]).read_text(errors="replace")
    if not notified["ok"] or "ZDCMP2_FIXTURE_CALLED" not in notification_log or "ZDCMP2_QUEUE_REMAINING=0" not in notification_log:
        raise SystemExit(f"ACS-to-ZScript message dispatch failed: {notified['log']}")
    message_save = local / "logs/saves/zdcmp2-message.zds"
    if not message_save.exists() or message_save.stat().st_mtime < message_started - 1:
        raise SystemExit(f"Queued-message save was not written: {message_save}")


if __name__ == "__main__":
    main()
