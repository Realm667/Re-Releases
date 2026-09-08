"""Export the generated brown cursor at UZDoom's Windows cursor size limit."""
from pathlib import Path
import struct
from PIL import Image
from PIL.PngImagePlugin import PngInfo

ART = Path(__file__).resolve().parent
ROOT = ART.parents[2]
image = Image.open(ART / "source.png").convert("RGBA")
bounds = image.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
if bounds is None:
    raise ValueError("Cursor artwork is empty")
image = image.crop(bounds)
image.thumbnail((30, 30), Image.Resampling.LANCZOS)
cursor = Image.new("RGBA", (32, 32))
cursor.alpha_composite(image, (1, 1))
metadata = PngInfo()
metadata.add(b"grAb", struct.pack(">ii", 1, 1))
cursor.save(ROOT / "tutnt/graphics/doomcurs.png", pnginfo=metadata)
