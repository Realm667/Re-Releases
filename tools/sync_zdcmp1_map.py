"""Extract or compile MAP01 ACS without rewriting geometry or nodes (ACC 1.60)."""
import argparse
from pathlib import Path
import subprocess
import tempfile

from build_utnt import read_wad, write_wad
from check_engine import ROOT


def sync(root, acc, write=False):
    wad = root / "Maps/map01.wad"
    source = root / "source/maps/map01.acs"
    magic, lumps = read_wad(wad)
    with tempfile.TemporaryDirectory(prefix="zdc-map-acs-") as directory:
        output = Path(directory) / "map01.o"
        result = subprocess.run([str(acc.resolve()), "-i", str(acc.resolve().parent),
                                 str(source.resolve()), str(output)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        replacements = {b"SCRIPTS": source.read_bytes(), b"BEHAVIOR": output.read_bytes()}
    names = [n.rstrip(b"\0") for n, _ in lumps]
    if any(names.count(n) != 1 for n in replacements):
        raise ValueError("Expected exactly one SCRIPTS and BEHAVIOR lump")
    updated = [(n, replacements.get(n.rstrip(b"\0"), data)) for n, data in lumps]
    if updated != lumps:
        if not write:
            raise ValueError("MAP01 ACS is stale; run sync_zdcmp1_map.py --acc ACC --write")
        with tempfile.TemporaryDirectory(dir=wad.parent) as directory:
            temporary = Path(directory) / "map01.wad"
            temporary.write_bytes(write_wad(magic, updated))
            temporary.replace(wad)
    print("MAP01 source and bytecode match; other lumps preserved")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT / "zdcmp1")
    parser.add_argument("--acc", type=Path)
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.extract:
        path = args.root / "source/maps/map01.acs"
        path.parent.mkdir(parents=True, exist_ok=True)
        lumps = read_wad(args.root / "Maps/map01.wad")[1]
        with path.open("xb") as output:
            output.write(next(d for n, d in lumps if n.rstrip(b"\0") == b"SCRIPTS"))
    elif args.acc:
        sync(args.root, args.acc, args.write)
    else:
        parser.error("--acc or --extract required")


if __name__ == "__main__":
    main()
