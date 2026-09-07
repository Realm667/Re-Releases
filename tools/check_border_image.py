"""Detect missing horizontal bands in a 1920x1080 screenblocks=3 capture."""
from PIL import Image


def longest_black_band(path):
    with Image.open(path) as source:
        if source.size != (1920, 1080):
            raise ValueError('Border band check requires a 1920x1080 capture')
        # This strip stays outside both the viewport and status bar at size 3.
        strip = source.convert('RGB').crop((8, 0, 128, 1080))
        run = longest = 0
        for y in range(strip.height):
            black = sum(max(strip.getpixel((x, y))) <= 2 for x in range(strip.width))
            run = run + 1 if black >= 118 else 0
            longest = max(longest, run)
        return longest
