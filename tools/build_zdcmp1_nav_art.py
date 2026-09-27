"""Build the small pixel-art badges and HUD direction sprites for ZDCMP1."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1] / "zdcmp1/Graphics/hud"


def badge(path: Path, selected: bool) -> None:
    image = Image.new("RGBA", (18, 18))
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, 17, 17), fill="#d9aa48" if selected else "#7c8584")
    draw.ellipse((1, 1, 16, 16), fill="#321e19" if selected else "#182023")
    draw.ellipse((2, 2, 15, 15), fill="#91252b")
    draw.arc((2, 2, 15, 15), 205, 330, fill="#b44246", width=1)
    image.save(path, optimize=True)


def pointer(path: Path) -> None:
    image = Image.new("RGBA", (20, 20))
    draw = ImageDraw.Draw(image)
    polygon = [(10, 1), (16, 8), (12, 8), (12, 17), (8, 17), (8, 8), (4, 8)]
    draw.polygon(polygon, fill="#ffce67")
    draw.line(polygon + [polygon[0]], fill="#3d2b16", width=1)
    image.save(path, optimize=True)


def main() -> None:
    badge(ROOT / "zdcmapbg.png", False)
    badge(ROOT / "zdcmapgo.png", True)
    pointer(ROOT / "zdnav0.png")


if __name__ == "__main__":
    main()
