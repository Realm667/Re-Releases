"""Build a deterministic ZDCMP1 PK3 and optionally verify tracked ACS with ACC 1.60."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile
import zipfile

from check_engine import ROOT

EXCLUDED_DIRS = {".git", ".vscode", ".codex", "#psd", "tools", "__pycache__"}
EXCLUDED_SUFFIXES = {".psd", ".otf", ".ttf", ".rar", ".zip", ".bat", ".dbs", ".pyc"}


def runtime_files(root):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or path.is_symlink():
            continue
        if any(part.lower() in EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.name.startswith(".") or path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        if ".backup" in path.name.lower() or ".autosave" in path.name.lower():
            continue
        yield path, relative.as_posix()


def check_acs(root, acc):
    acc = acc.resolve()
    with tempfile.TemporaryDirectory(prefix="zdc-acs-") as directory:
        for source in sorted((root / "source").glob("*.acs")):
            output = Path(directory) / (source.stem + ".o")
            subprocess.run([str(acc), "-i", str(acc.parent), str(source.resolve()), str(output)], check=True,
                           cwd=directory, capture_output=True)
            tracked = root / "acs" / output.name
            if output.read_bytes() != tracked.read_bytes():
                raise ValueError(f"Stale ACS: {tracked}; recompile {source} with ACC 1.60")
            print(f"ACS matches: {tracked}")


def package(root, output):
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Package output must be outside the mod directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Replace only after the entire archive has been built and checked.
    with tempfile.TemporaryDirectory(dir=output.parent) as directory:
        temporary = Path(directory) / "mod.pk3"
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path, name in runtime_files(root):
                entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, path.read_bytes())
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip():
                raise ValueError("Corrupt PK3")
        temporary.replace(output)
    print(f"PK3: {output} SHA256={hashlib.sha256(output.read_bytes()).hexdigest()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT / "zdcmp1")
    parser.add_argument("--output", type=Path, default=ROOT / "zdcmp1.pk3")
    parser.add_argument("--acc", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if args.check_only and not args.acc:
        parser.error("--check-only requires --acc")
    if args.acc:
        check_acs(args.root, args.acc)
    if not args.check_only:
        package(args.root, args.output)


if __name__ == "__main__":
    main()
