"""Build ZDCMP1/ZDCMP2 BigFont and SmallFont from original ZDCMP2 artwork.

The source FON2 is kept under zdcmp2/source/fonts because a root-level
DBIGFONT.fon2 overrides the Unicode folder at runtime. Both mods receive the
same glyph artwork and explicit Latin-language accent coverage.
"""

from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_localized_fonts import read_fon2, read_patch, extend, png

MODS = ("zdcmp1", "zdcmp2")
REQUIRED = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    "ÀÁÂÄÇÈÉÊËÎÏÔÖÙÛÜŸàáâäçèéêëîïôöùûüÿ"
    "Ññ¡¿ßẞÄÖÜäöüÌÍÒÓÚìíòóúŒœÆæ"
    " .,;:!?'-/()&%+="
)


def generated() -> dict[Path, bytes]:
    original = ROOT / "zdcmp2" / "source" / "fonts" / "DBIGFONT.fon2"
    big, big_palette, big_height, big_kerning = read_fon2(original)
    palette_bytes = (ROOT / "zdcmp2" / "PLAYPAL.pal").read_bytes()
    small_palette = [tuple(palette_bytes[i:i+3]) for i in range(0, 768, 3)]
    patches = ROOT / "zdcmp2" / "graphics"
    small = {int(path.name[5:]): read_patch(path) for path in patches.glob("STCFN*")
             if path.name[5:].isdigit()}
    small_height = max(g.height for g in small.values())
    big = extend(big, big_palette, False)
    small = extend(small, small_palette, True)
    for name, glyphs in (("bigfont", big), ("smallfont", small)):
        missing = sorted(set(map(ord, REQUIRED)) - glyphs.keys())
        if missing:
            raise ValueError(f"{name} is missing: {''.join(map(chr, missing))}")
    result: dict[Path, bytes] = {}
    specs = (
        ("bigfont", big, big_palette, big_height, big_kerning, big[32].width),
        ("smallfont", small, small_palette, small_height, 0, 4),
    )
    for mod in MODS:
        for name, glyphs, palette, height, kerning, space in specs:
            directory = Path(mod) / "fonts" / name
            info = f"Scale 1\nFontHeight {height}\nSpaceWidth {space}\nKerning {kerning}\n"
            result[directory / "font.inf"] = info.encode("ascii")
            for code, glyph in sorted(glyphs.items()):
                result[directory / f"{code:04X}.png"] = png(glyph, palette)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = generated()
    stale = []
    for relative, payload in data.items():
        path = ROOT / relative
        if args.check:
            if not path.is_file() or path.read_bytes() != payload:
                stale.append(str(relative))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    if stale:
        raise SystemExit(f"{len(stale)} generated font files are missing/stale: {', '.join(stale[:10])}")
    print(json.dumps({"files": len(data), "glyphs_per_font": (len(data)//4-1), "mods": MODS, "checked": args.check}))


if __name__ == "__main__":
    main()
