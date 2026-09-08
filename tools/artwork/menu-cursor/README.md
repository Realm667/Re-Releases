# Brown menu cursor

`tutnt/graphics/doomcurs.png` replaces UZDoom's red Doom cursor through the
existing `doomcurs` resource name. Doom's inherited `GameInfo.CursorPic`
already selects it. Explicit user selections of other cursor styles remain
available. No engine files or player configuration are modified.

The RGBA PNG is 32 x 32 pixels, including transparent padding. Its PNG `grAb`
offset (1, 1) places the click hotspot at the upper-left arrow tip. UZDoom's
Windows `I_SetCursor` rejects images larger than 32 x 32 and reads these offsets
as the native cursor hotspot.

Artwork: generated using the built-in Imagegen tool, then cropped and reduced
with Pillow/Lanczos for runtime export. `source.png` preserves the generated
RGBA original. Run `python tools/artwork/menu-cursor/export.py` to rebuild.

Prompt: Create one production-ready game menu mouse cursor on a truly
transparent background. A single compact classic arrow pointing upper-left,
with a straight nearly vertical left edge, a triangular arrow head and short
diagonal lower-right stem. Dark walnut brown and weathered bronze bevels,
warm tan thin highlight along upper/left edge, near-black brown crisp outer
outline. Restrained rugged 1990s Doom gothic-industrial UI style, primarily
brown, no red and no bright yellow/gold. Strong simple silhouette that reads
at 32x32 pixels, minimal broad surface facets, no tiny ornaments. Entire arrow
isolated, no text, no scene, no surrounding frames, no extra icons, no
checkerboard baked into image. Square canvas, arrow occupies most of canvas
with small transparent margin. Tip must be precisely defined for clicking.
This will be downscaled into a small native OS cursor.

Validation: inspected the 32-pixel export on dark brown and light tan
backgrounds; checked RGBA transparency, dimensions and hotspot against the
local UZDoom cursor implementation. The regular build validates ZIP integrity,
compiles ACS in an isolated snapshot and checks engine resource loading.
An interactive mouse-click test was not performed.
