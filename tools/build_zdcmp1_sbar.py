"""Build lossless SBAR mask geometry for native TEXTURES color blending.

Requires Pillow. Original PNG pixels are never rewritten: only red regions are
blended by the engine; metal, text, transparent pixels and portrait stay intact.
"""
import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BEGIN = "// BEGIN GENERATED CALM SBAR (tools/build_zdcmp1_sbar.py)\n"
END = "// END GENERATED CALM SBAR\n"


def rectangles(image):
    active, result = {}, []
    for y in range(image.height + 1):
        spans, start = [], None
        for x in range(image.width + 1):
            r, g, b, a = image.getpixel((x, y)) if x < image.width and y < image.height else (0, 0, 0, 0)
            red = a > 0 and r > g * 2 + 8 and r > b * 2 + 8
            if red and start is None:
                start = x
            if not red and start is not None:
                spans.append((start, x - start))
                start = None
        for span in list(active):
            if span not in spans:
                result.append(active.pop(span))
        for span in spans:
            if span in active:
                active[span][3] += 1
            else:
                active[span] = [span[0], y, span[1], 1]
    return result


def generated():
    source = "Graphics/sbar/stbar.png"
    with Image.open(ROOT / "zdcmp1" / source) as original:
        image = original.convert("RGBA")
    regions = rectangles(image)
    definitions = [BEGIN.rstrip()]
    for index, (x, y, w, h) in enumerate(regions):
        definitions.append(f'Graphic ZSR{index:03}, {w}, {h} {{ Patch "{source}", {-x}, {-y} {{ Blend 58, 16, 20, 0.88 }} }}')
    definitions += [f'Graphic STBAR, {image.width}, {image.height}', '{', f'    Patch "{source}", 0, 0']
    definitions += [f'    Patch ZSR{index:03}, {x}, {y}' for index, (x, y, _, _) in enumerate(regions)]
    definitions += ['}', END.rstrip()]
    return '\n'.join(definitions) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "zdcmp1/textures.txt"
    text = path.read_text()
    block = generated()
    if BEGIN in text:
        before, _, rest = text.partition(BEGIN)
        _, separator, after = rest.partition(END)
        if not separator:
            raise ValueError("Missing generated SBAR end marker")
        updated = before + block + after
    else:
        updated = block + '\n' + text
    if args.check:
        if text != updated:
            raise SystemExit("SBAR mask is stale: run tools/build_zdcmp1_sbar.py")
        print("SBAR red-only mask matches original artwork")
    else:
        path.write_text(updated)


if __name__ == "__main__":
    main()
