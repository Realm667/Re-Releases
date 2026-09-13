"""Encode the approved Reforged pixel artwork as the native M_DOOM menu patch."""
import argparse
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/artwork/menu-logo/alpha-key-source.png"
OUTPUT = ROOT / "tutnt/graphics/menu/M_DOOM.png"
HIRES = ROOT / "tutnt/hires/graphics/M_DOOM.png"

def bleed_transparent_rgb(image):
    """Extend edge colors into invisible texels to prevent filtering halos."""
    pixels = np.array(image)
    known = pixels[:, :, 3] > 0
    if not known.any():
        raise ValueError("Empty logo")
    height, width = known.shape
    while not known.all():
        neighbors = np.pad(known, 1)
        colors = np.pad(pixels[:, :, :3], ((1, 1), (1, 1), (0, 0)))
        filled = known.copy()
        for dy, dx in ((0, 1), (2, 1), (1, 0), (1, 2)):
            valid = neighbors[dy:dy + height, dx:dx + width] & ~filled
            pixels[valid, :3] = colors[dy:dy + height, dx:dx + width][valid]
            filled |= valid
        known = filled
    return Image.fromarray(pixels)


def render(scale=1):
    rgba = np.array(Image.open(SOURCE).convert("RGBA"))
    rgb = rgba[:, :, :3].astype(np.int16)
    # Remove the key only; the repaired source retains intentional dark metal.
    key = (rgb[:, :, 0] - rgb[:, :, 1] > 45) & (rgb[:, :, 2] - rgb[:, :, 1] > 45)
    rgba[key] = 0
    source = Image.fromarray(rgba)
    box = source.getbbox()
    if box is None:
        raise ValueError("Empty logo source")
    source = source.crop(box).convert("RGBa")
    # Resample premultiplied colors, then restore straight alpha for PNG.
    source.thumbnail((284 * scale, 52 * scale), Image.Resampling.LANCZOS)
    source = source.convert("RGBA")
    canvas = Image.new("RGBA", (288 * scale, 56 * scale))
    canvas.paste(source, ((288 * scale - source.width)//2, (56 * scale - source.height)//2))
    rgb = canvas.convert("RGB")
    palette = Image.new("P", (1, 1))
    palette.putpalette((ROOT / "tutnt/PLAYPAL.pal").read_bytes()[:768])
    # Quantize once at the actual menu resolution: no faux high-resolution pixel grid.
    result = rgb.quantize(palette=palette, dither=Image.Dither.NONE).convert("RGBA")
    result.putalpha(canvas.getchannel("A"))
    return bleed_transparent_rgb(result)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, scale in ((OUTPUT, 1), (HIRES, 2)):
        image = render(scale)
        if args.check:
            existing = Image.open(path).convert("RGBA")
            if existing.size != image.size or existing.tobytes() != image.tobytes():
                raise SystemExit(f"{path} is stale; run tools/build_menu_logo.py")
            print(f"M_DOOM {scale}x: {image.width}x{image.height}, palette, continuous alpha and edge colors verified")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(path, optimize=True)
            print(path)

if __name__ == "__main__":
    main()
