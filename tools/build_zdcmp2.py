"""Verify ZDCMP2 ACS and build its deterministic UZDoom package."""
import argparse
from pathlib import Path
import subprocess
import tempfile

from build_zdcmp1 import package
from check_engine import ROOT


def check_acs(acc: Path) -> None:
    acc = acc.resolve()
    source = ROOT / "zdcmp2/source/zdcmp2.acs"
    tracked = ROOT / "zdcmp2/acs/zdcmp2.o"
    with tempfile.TemporaryDirectory(prefix="zdcmp2-acs-") as directory:
        output = Path(directory) / "zdcmp2.o"
        subprocess.run([str(acc), "-i", str(acc.parent), str(source), str(output)],
                       cwd=directory, check=True, capture_output=True)
        if output.read_bytes() != tracked.read_bytes():
            raise ValueError(f"Stale ACS bytecode: {tracked}")
    print(f"ACS matches: {tracked}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acc", type=Path, required=True)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "tutnt/.codex/builds/zdcmp2-release.pk3")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    check_acs(args.acc)
    if not args.check_only:
        package(ROOT / "zdcmp2", args.output)


if __name__ == "__main__":
    main()
