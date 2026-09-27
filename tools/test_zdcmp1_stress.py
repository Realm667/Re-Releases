"""Fixed-seed Max-quality frame-time and real-time soak tests (isolated saves).

Run benchmarks without other engine processes. Soak tests sample resident memory
on macOS/Linux, but do not pretend RSS is a portable leak detector.
"""
import argparse
import json
import math
import os
from pathlib import Path
import re
import statistics
import subprocess
import tempfile
import time
import zipfile

from check_engine import ROOT
from test_zdcmp1_effects import fixture

SCENES = {"weather": 0, "smoke": 1, "fire": 2, "gore": 3, "mixed": 4}


def stress_fixture(path, scene):
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory) / "base.pk3"
        fixture(base)
        with zipfile.ZipFile(base) as source, zipfile.ZipFile(path, "w") as target:
            wad = source.read("maps/zdcftest.wad")
            if scene in ("weather", "mixed"):
                from build_utnt import read_wad, write_wad
                temporary = Path(directory) / "map.wad"
                temporary.write_bytes(wad)
                magic, entries = read_wad(temporary)
                entries = [(name, data.replace(b'"FLAT5_4"', b'"QLAVA"')) for name, data in entries]
                wad = write_wad(magic, entries)
            target.writestr("maps/zdcftest.wad", wad)
            target.write(ROOT / "tools/zdcmp1-tests/stress.zc", "zscript.zc")
            target.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers = "ZDCMP1Stress", "ZDCMP1Frames" }\n')


def commands(scene, seconds, soak):
    start = f"unbindall; wait 35; netevent zdcstress {SCENES[scene]}; wait 175; "
    if soak:
        # Ten checkpoints include explicit save/load, not just idle runtime.
        interval = math.ceil(seconds * 35 / 10)
        body = ""
        for i in range(10):
            body += (f"wait {interval}; netevent zdcsnapshot; save zdc-soak-{i}; wait 10; "
                     f"load zdc-soak-{i}; wait 35; netevent zdcsnapshot; ")
    else:
        body = f"event zdcframes 1; wait {math.ceil(seconds * 35)}; event zdcframes 0; netevent zdcsnapshot; profilethinkers -t 12; profilecsthinkers -t 12; "
    return (start + body + "wait 5; netevent zdcstop; ZDCMP1_weatherfx false; wait 350; netevent zdcsnapshot; wait 5; "
            "echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit\n")


def run(engine, iwad, mod, addon, renderer, scene, seconds, soak, label):
    directory = ROOT / "logs" / label
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "saves").mkdir(exist_ok=True)
    config = directory / "engine.ini"
    config.write_text("[GlobalSettings]\nvid_fullscreen=false\nvid_defwidth=1280\nvid_defheight=720\nvid_hidpi=false\nwin_w=1280\nwin_h=720\n")
    script = directory / "run.cfg"
    script.write_text(commands(scene, seconds, soak))
    args = [str(Path(engine).resolve()), "-iwad", str(Path(iwad).resolve()), "-file", str(mod.resolve()), str(addon),
            "-config", str(config), "-savedir", str(directory / "saves"), "-noautoload", "-nosound", "-stdout", "-noidle",
            "-rngseed", "667", "+vid_fullscreen", "false", "+vid_preferbackend", renderer,
            "+vid_vsync", "false", "+vid_maxfps", "60" if soak else "0", "+cl_capfps", "false",
            "+i_pauseinbackground", "false", "+vid_activeinbackground", "true", "+vid_lowerinbackground", "false",
            "+use_mouse", "false", "+use_joystick", "false", "+ZDCMP1_fxquality", "2", "+nashgore_maxgore", "1024",
            "+playerclass", "ZDCMPPlayer", "+map", "ZDCFTEST", "+exec", str(script)]
    started = time.monotonic()
    rss = []
    log = directory / "engine.log"
    timed_out = False
    with log.open("wb") as output:
        child = subprocess.Popen(args, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        try:
            next_sample = started
            while child.poll() is None:
                now = time.monotonic()
                if any(marker in log.read_text(errors="replace") for marker in
                       ("Script error,", "VM execution aborted", "Execution could not continue")):
                    child.kill()
                    break
                if now - started > seconds * 1.5 + 120:
                    timed_out = True
                    child.kill()
                    break
                if soak and os.name == "posix" and now >= next_sample:
                    value = subprocess.run(["ps", "-o", "rss=", "-p", str(child.pid)], capture_output=True, text=True)
                    if value.stdout.strip().isdigit():
                        rss.append({"seconds": round(now - started, 2), "rss_kib": int(value.stdout)})
                    next_sample = now + 30
                time.sleep(0.2)
        finally:
            if child.poll() is None:
                child.kill()
            code = child.wait()
    text = log.read_text(errors="replace")
    errors = [s for s in ("UTNT_ASSERT FAIL", "VM execution aborted", "Script error,", "Execution could not continue",
                          "errors while parsing", "mismatched client-side handling") if s in text]
    if timed_out or "UTNT_TEST_END" not in text or "UTNT_REGRESSION_COMPLETE" not in text:
        errors.append("timeout or missing completion markers")
    assertions = text.count("UTNT_ASSERT PASS")
    if assertions != (21 if soak else 2):
        errors.append(f"unexpected assertion count: {assertions}")
    elapsed = time.monotonic() - started
    if soak and elapsed < seconds:
        errors.append("soak did not run for the requested wall-clock duration")
    samples = [float(n) for line in re.findall(r"ZDC_FRAME_MS ([\d.,]+)", text) for n in line.split(",")]
    result = {"label": label, "ok": code in (0, 1337) and not errors, "exit": code, "seconds": round(elapsed, 2),
              "scene": scene, "renderer": renderer, "mod": str(mod.resolve()), "errors": errors,
              "assertions": assertions, "rss": rss, "log": str(log)}
    resolution = re.search(r"Resolution: (\d+) x (\d+)", text)
    result["resolution"] = list(map(int, resolution.groups())) if resolution else None
    result["objects"] = [dict(zip(("tick", "lights", "smoke", "gore", "weather"), map(int, row)))
                         for row in re.findall(r"ZDC_COUNTS tick=(\d+) lights=(\d+) smoke=(\d+) gore=(\d+) weather=(\d+)", text)]
    settled = [row for row in rss if row["seconds"] >= 180]
    if len(settled) >= 4:
        midpoint = len(settled) // 2
        first = statistics.median(row["rss_kib"] for row in settled[:midpoint]) / 1024
        last = statistics.median(row["rss_kib"] for row in settled[midpoint:]) / 1024
        result["rss_mib"] = {"early_median": first, "late_median": last, "change": last - first,
                             "peak": max(row["rss_kib"] for row in settled) / 1024,
                             "note": "Resident CPU memory only; allocator/GPU caches require separate interpretation."}
    if not soak:
        if len(samples) < 100:
            result["ok"] = False
            errors.append("fewer than 100 frame samples")
        elif all(math.isfinite(n) and n > 0 for n in samples):
            ordered = sorted(samples)
            result["frame_ms"] = {"count": len(samples), "median": statistics.median(samples),
                                  "p95": ordered[math.ceil(len(samples) * .95) - 1],
                                  "p99": ordered[math.ceil(len(samples) * .99) - 1], "max": max(samples)}
        else:
            result["ok"] = False
            errors.append("invalid frame samples")
    (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", default=os.environ.get("UTNT_ENGINE"), required=not os.environ.get("UTNT_ENGINE"))
    parser.add_argument("--iwad", default=os.environ.get("UTNT_IWAD"), required=not os.environ.get("UTNT_IWAD"))
    parser.add_argument("--mod", type=Path, default=ROOT / "zdcmp1")
    parser.add_argument("--compare", type=Path, help="Immutable baseline; alternate AB/BA between repeats")
    parser.add_argument("--scene", choices=SCENES, default="mixed")
    parser.add_argument("--renderer", choices=("0", "1"), default="1")
    parser.add_argument("--seconds", type=float, default=15)
    parser.add_argument("--soak", action="store_true", help="Use --seconds 1800 for a 30-minute run")
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--label", default="zdc-stress")
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds <= 0 or args.repeats < 1:
        parser.error("seconds and repeats must be positive")
    results = []
    with tempfile.TemporaryDirectory(prefix="zdc-stress-") as directory:
        addon = Path(directory) / "fixture.pk3"
        stress_fixture(addon, args.scene)
        for repeat in range(args.repeats):
            packages = [("after", args.mod)]
            if args.compare:
                packages.insert(0, ("before", args.compare))
                if repeat % 2:
                    packages.reverse()
            for version, package in packages:
                label = f"{args.label}-{args.scene}-{args.renderer}-{repeat}-{version}"
                result = run(args.engine, args.iwad, package, addon, args.renderer, args.scene, args.seconds, args.soak, label)
                results.append(result)
                if not result["ok"]:
                    print(Path(result["log"]).read_text()[-5000:])
                    return 1
    (ROOT / "logs" / f"{args.label}-results.json").write_text(json.dumps(results, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
