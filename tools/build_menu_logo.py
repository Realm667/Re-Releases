"""Encode the approved Reforged pixel artwork as the native M_DOOM menu patch."""
import argparse
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/artwork/menu-logo/pixel-source.png"
OUTPUT = ROOT / "tutnt/graphics/menu/M_DOOM.png"

def render():
    rgba = np.array(Image.open(SOURCE).convert("RGBA"))
    rgb = rgba[:, :, :3].astype(np.int16)
    # The source uses an explicit magenta key; dark metal and black outlines stay opaque.
    key = (rgb[:, :, 0] - rgb[:, :, 1] > 45) & (rgb[:, :, 2] - rgb[:, :, 1] > 45)
    rgba[key] = 0
    source = Image.fromarray(rgba)
    box = source.getbbox()
    if box is None:
        raise ValueError("Empty logo source")
    source = source.crop(box)
    source.thumbnail((284, 52), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (288, 56))
    canvas.paste(source, ((288-source.width)//2, (56-source.height)//2))
    rgb = canvas.convert("RGB")
    palette = Image.new("P", (1, 1))
    palette.putpalette((ROOT / "tutnt/PLAYPAL.pal").read_bytes()[:768])
    # Quantize once at the actual menu resolution: no faux high-resolution pixel grid.
    result = rgb.quantize(palette=palette, dither=Image.Dither.NONE).convert("RGBA")
    result.putalpha(canvas.getchannel("A").point(lambda a: 255 if a >= 112 else 0))
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    image = render()
    if args.check:
        existing = Image.open(OUTPUT).convert("RGBA")
        if existing.size != image.size or existing.tobytes() != image.tobytes():
            raise SystemExit("M_DOOM.png is stale; run tools/build_menu_logo.py")
        print("M_DOOM: 288x56, current palette, binary alpha, reproducible")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        image.save(OUTPUT, optimize=True)
        print(OUTPUT)

if __name__ == "__main__":
    main()
