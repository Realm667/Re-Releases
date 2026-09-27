"""Two real local peers; test death, respawn, cameras and independent local effects."""
import argparse
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time
import zipfile

from check_engine import ROOT
from test_zdcmp1_edges import geometry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", default=os.environ.get("UTNT_ENGINE"), required=not os.environ.get("UTNT_ENGINE"))
    parser.add_argument("--iwad", default=os.environ.get("UTNT_IWAD"), required=not os.environ.get("UTNT_IWAD"))
    parser.add_argument("--mod", type=Path, default=ROOT / "zdcmp1")
    parser.add_argument("--renderer", choices=("0", "1"), default="1")
    args = parser.parse_args()
    logs = ROOT / "logs" / f"zdc-coop-{args.renderer}"
    logs.mkdir(parents=True, exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    peers = []
    results = []
    with tempfile.TemporaryDirectory() as directory:
        addon = Path(directory) / "coop.pk3"
        with zipfile.ZipFile(addon, "w") as archive:
            archive.writestr("maps/zdcedge.wad", geometry())
            archive.write(ROOT / "tools/zdcmp1-tests/coop.zc", "zscript.zc")
            archive.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers="ZDCMP1Coop", "ZDCMP1CoopUI" }\n')
        try:
            for i in range(2):
                config = logs / f"peer-{i}.ini"
                config.write_text("[GlobalSettings]\nvid_fullscreen=false\nvid_defwidth=640\nvid_defheight=480\nvid_hidpi=false\nwin_w=640\nwin_h=480\n")
                log = logs / f"peer-{i}.log"
                log.write_text("")
                script = logs / f"peer-{i}.cfg"
                script.write_text("wait 420; quit\n")
                command = [str(Path(args.engine).resolve()), "-iwad", str(Path(args.iwad).resolve()),
                           "-file", str(args.mod.resolve()), str(addon), "-config", str(config),
                           "-noautoload", "-nosound", "-stdout", "-noidle", "-rngseed", "667",
                           "+vid_fullscreen", "false", "+vid_preferbackend", args.renderer,
                           "+vid_maxfps", "60", "+vid_vsync", "false", "+i_pauseinbackground", "false", "+vid_activeinbackground", "true",
                           "+use_mouse", "false", "+use_joystick", "false", "+motionblur", "true" if i else "false",
                           "+playerclass", "ZDCMPPlayer", "+map", "ZDCEDGE", "+exec", str(script)]
                command += ["-host", "2", "-port", str(port)] if i == 0 else ["-join", f"127.0.0.1:{port}"]
                output = log.open("wb")
                try:
                    child = subprocess.Popen(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
                except BaseException:
                    output.close()
                    raise
                peers.append((child, output, log))
                if i == 0:
                    time.sleep(1)
            deadline = time.monotonic() + 75
            while time.monotonic() < deadline:
                texts = [log.read_text(errors="replace") for _, _, log in peers]
                if all("ZDC_COOP_COMPLETE" in t and "ZDC_COOP_UI_COMPLETE" in t for t in texts):
                    break
                if all(child.poll() is not None for child, _, _ in peers):
                    break
                if any("Script error," in t or "VM execution aborted" in t for t in texts):
                    break
                time.sleep(0.2)
            for i, (child, _, log) in enumerate(peers):
                text = log.read_text(errors="replace")
                errors = [m for m in ("UTNT_ASSERT FAIL", "VM execution aborted", "Script error,", "mismatched client-side handling") if m in text]
                complete = "ZDC_COOP_COMPLETE" in text and "ZDC_COOP_UI_COMPLETE" in text
                if not complete:
                    errors.append("missing completion markers")
                state = re.search(r"ZDC_COOP_STATE (.*)", text)
                result = {"peer": i, "ok": complete and not errors and text.count("UTNT_ASSERT PASS") == 16,
                          "errors": errors, "assertions": text.count("UTNT_ASSERT PASS"),
                          "state": state[1] if state else None, "log": str(log), "teardown": "runner stops only its two peers after checks"}
                results.append(result)
        finally:
            for child, output, _ in peers:
                if child.poll() is None:
                    child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
                output.close()
    if len(results) == 2 and results[0]["state"] != results[1]["state"]:
        for result in results:
            result["ok"] = False
            result["errors"].append("peer state differs")
    (logs / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    if len(results) != 2 or not all(r["ok"] for r in results):
        for result in results:
            print(Path(result["log"]).read_text()[-5000:])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
