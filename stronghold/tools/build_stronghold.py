"""Compile, package and smoke-test Stronghold for UZDoom 5.0.3.

Packaging never modifies production sources. Use --update-acs deliberately
after changing acs_src/strnghld.acs, then review the binary diff.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import socket
import subprocess
import sys
import time
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT.parent / "tutnt" / ".codex"
WORK = SHARED / "work" / "stronghold-build"
BUILDS = SHARED / "builds"
LOGS = SHARED / "logs" / "stronghold"
RUNTIME_DIRS = {
    "acs", "flats", "graphics", "hires", "maps", "materials", "models",
    "music", "patches", "shaders", "sounds", "sprites", "textures", "Zscript",
}
NON_RUNTIME_ROOT = {".todo.txt", "strnghld_v1.txt"}
REQUIRED = {"acs/strnghld.o", "SCRIPT00.lmp", "zscript.zc", "mapinfo.txt"}
MAPS = ("STR01", "STR21", "STR33")


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def compile_acs(acc: Path, update: bool) -> None:
    if not acc.is_file():
        raise RuntimeError(f"ACC compiler missing: {acc}")
    WORK.mkdir(parents=True, exist_ok=True)
    compiled = WORK / "strnghld.o"
    command = [str(acc), "-i", str(acc.parent),
               str(ROOT / "acs_src" / "strnghld.acs"), str(compiled)]
    result = subprocess.run(command, capture_output=True, text=True, errors="replace")
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / "acc.stdout.log").write_text(result.stdout, encoding="utf-8")
    (LOGS / "acc.stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode or not compiled.is_file():
        raise RuntimeError(f"ACC failed ({result.returncode}); see {LOGS / 'acc.stdout.log'}")
    production = ROOT / "acs" / "strnghld.o"
    if update:
        shutil.copyfile(compiled, production)
    if digest(compiled) != digest(production):
        raise RuntimeError("acs/strnghld.o differs from source build; run --update-acs and review it")
    print("ACS source matches the production object")


def runtime_files() -> list[Path]:
    files: list[Path] = []
    for entry in ROOT.iterdir():
        if entry.is_file() and entry.name not in NON_RUNTIME_ROOT and not entry.name.startswith("."):
            files.append(entry)
        elif entry.is_dir() and entry.name in RUNTIME_DIRS:
            files.extend(p for p in entry.rglob("*") if p.is_file())
    paths = {p.relative_to(ROOT).as_posix() for p in files}
    missing = REQUIRED - paths
    if missing:
        raise RuntimeError(f"Missing production resources: {sorted(missing)}")
    if len(paths) != len(files):
        raise RuntimeError("Duplicate package paths")
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix().lower())


def build_package(output: Path) -> None:
    files = runtime_files()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = WORK / "stronghold-package.tmp"
    WORK.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6, allowZip64=True) as archive:
        for path in files:
            name = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED,
                             compresslevel=6)
    with zipfile.ZipFile(temporary) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Package CRC validation failed")
        archived = set(archive.namelist())
        expected = {p.relative_to(ROOT).as_posix() for p in files}
        if archived != expected:
            raise RuntimeError("Package resources differ from the production tree")
    os.replace(temporary, output)
    print(f"Packaged {len(files)} production files: {output}")


def smoke(engine: Path, iwad: Path, mod: Path, seconds: int) -> None:
    if not engine.is_file() or not iwad.is_file():
        raise RuntimeError("--engine and --iwad must point to existing files")
    LOGS.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    saves = WORK / "saves"
    saves.mkdir(exist_ok=True)
    for map_name in MAPS:
        output = LOGS / f"{map_name.lower()}-uzdoom503.stdout.log"
        error = LOGS / f"{map_name.lower()}-uzdoom503.stderr.log"
        args = [str(engine), "-noautoload", "-nosound", "-config", str(WORK / "uzdoom.ini"),
                "-savedir", str(saves), "-iwad", str(iwad), "-file", str(mod),
                "-stdout", "+map", map_name]
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        with output.open("wb") as out, error.open("wb") as err:
            process = subprocess.Popen(args, stdout=out, stderr=err, creationflags=flags)
            try:
                time.sleep(seconds)
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
        log = output.read_text(errors="replace")
        if f"{map_name} -" not in log or "Script error" in log or "errors while parsing scripts" in log:
            raise RuntimeError(f"UZDoom smoke test failed for {map_name}: {output}")
        print(f"UZDoom loaded {map_name}")


def net_smoke(engine: Path, iwad: Path, mod: Path, seconds: int) -> None:
    if not engine.is_file() or not iwad.is_file():
        raise RuntimeError("--engine and --iwad must point to existing files")
    LOGS.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    processes: list[tuple[str, subprocess.Popen, object, object]] = []
    try:
        for role, net_args in (("host", ["-host", "2"]),
                               ("join", ["-join", "127.0.0.1"])):
            saves = WORK / f"net-{role}-saves"
            saves.mkdir(exist_ok=True)
            out = (LOGS / f"net-{role}.stdout.log").open("wb")
            err = (LOGS / f"net-{role}.stderr.log").open("wb")
            args = [str(engine), "-noautoload", "-nosound", "-config",
                    str(WORK / f"net-{role}.ini"), "-savedir", str(saves),
                    "-iwad", str(iwad), "-file", str(mod), "-stdout",
                    "-port", str(port), *net_args]
            try:
                process = subprocess.Popen(args, stdout=out, stderr=err,
                                           creationflags=flags)
            except OSError:
                out.close()
                err.close()
                raise
            processes.append((role, process, out, err))
            if role == "host":
                time.sleep(3)
        time.sleep(seconds)
    finally:
        for _, process, out, err in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            out.close()
            err.close()
    for role in ("host", "join"):
        output = LOGS / f"net-{role}.stdout.log"
        log = output.read_text(errors="replace")
        if ("Total players: 2" not in log or "STR01 -" not in log or
                "Script error" in log or "errors while parsing scripts" in log):
            raise RuntimeError(f"UZDoom network smoke test failed for {role}: {output}")
    print("UZDoom host and client both loaded STR01 with two players")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    found_acc = shutil.which("acc")
    parser.add_argument("--acc", type=Path, default=Path(found_acc) if found_acc else None)
    parser.add_argument("--update-acs", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--repro-check", action="store_true")
    parser.add_argument("--output", type=Path, default=BUILDS / "stronghold-uzdoom503.pk3")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--net-smoke", action="store_true")
    parser.add_argument("--engine", type=Path)
    parser.add_argument("--iwad", type=Path)
    parser.add_argument("--seconds", type=int, default=12)
    args = parser.parse_args()
    if args.acc is None:
        parser.error("Provide --acc or put acc on PATH")
    if (args.smoke or args.net_smoke) and (args.engine is None or args.iwad is None):
        parser.error("--smoke and --net-smoke require --engine and --iwad")
    if args.repro_check and not args.build:
        parser.error("--repro-check requires --build")
    compile_acs(args.acc, args.update_acs)
    subprocess.run([sys.executable, "-B", str(ROOT / "tools" / "check_clientside.py")],
                   check=True)
    package = args.output.resolve()
    if args.build:
        build_package(package)
        if args.repro_check:
            comparison = WORK / "stronghold-repro-check.pk3"
            try:
                build_package(comparison)
                if digest(package) != digest(comparison):
                    raise RuntimeError("Repeated package builds differ")
            finally:
                comparison.unlink(missing_ok=True)
            print("Repeated package builds have the same SHA-256 digest")
    if args.smoke:
        smoke(args.engine, args.iwad, package if args.build else ROOT, args.seconds)
    if args.net_smoke:
        net_smoke(args.engine, args.iwad, package if args.build else ROOT, args.seconds)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
