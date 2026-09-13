# Sparse grass tufts

Updated: 13 September 2026.

Eight independent grass sprites add low vegetation to QGRASS, GRASS2 and SM_GRAS floors,
including their XA08TEX/XB08TEX and XA31TEX/XB31TEX expanded-material aliases.
The artwork follows the approved TNTLE mockup, with greater density and the
subsequently requested low-resolution appearance and ground-matched colors.
Original RGBA images and their alpha channels remain intact in `tutnt/patches/grass/`.
Imagegen prompts and provenance are recorded in `tools/artwork/grass/prompts.json`.

## Appearance

The hardware shader samples each silhouette at 32 pixels in height with hard
pixel edges and six brightness steps. QGRASS/GRASS2 use dark, desaturated olive
and earth tones derived from the original floors; SM_GRAS receives a separate
greener palette. Both palettes reuse the same eight silhouettes. Source images
remain at their original size as editable artwork; visible detail is limited in
the shader, independently of the player's texture filtering setting.

Each grass cell independently varies the sprite (eight silhouettes), horizontal
mirror, width, height and position. Tufts are about 17–25 map units high. A jittered
48-unit grid accepts 82% of cells before geometry checks: roughly one tuft per
2,810 square map units of open eligible floor. The grid is a sampling aid; its
points are displaced independently on both axes and cells can remain empty.

Sprites remain vertical, receive the existing sector lighting and use translucent
rendering. Their lower 16% fades smoothly through the existing image alpha; roots
sit 0.65 units below the actual floor plane. An alpha threshold suppresses
very faint source edge speckles. No opaque ground decal or artificial soil mound
is added. The palette, pixelation and soft roots require the hardware renderer; source
color and alpha remain the fallback for software rendering.

## Placement and lifecycle

A private map/cell hash makes placement repeatable across save/load, revisits and
quality toggles without consuming gameplay RNG. Runtime placement uses actual
floor textures, floor planes, sector polygon containment and 22-unit clearance
from sector boundaries. It handles holes and disconnected sector regions, rejects
steep slopes and insufficient ceiling clearance, and follows moving floor height.
Changed floor materials hide/remove the grass and eligible surfaces can repopulate.

Floor portals, deep-water control sectors and sectors containing 3D floors are
excluded conservatively; this version does not scatter on stacked 3D-floor tops.
Decorative actors are client-local, nonblocking, nonshootable, absent from the
blockmap and automap, and do not change maps, collision or gameplay counts.

The existing effect quality and LOD options govern vegetation. Maximum ranges are
448/704/896 units at low/medium/high quality, capped by the user's LOD setting.
Quality zero clears grass; reduced effects use low quality. The outer 144 units
fade out smoothly. New instances fade in over 12 tics. Placement inspects at most
96 cells per tic and keeps no more than 1,200 actors around the local camera.

## Sources and checks

- `tutnt/zscript/UTNT_Grass.zc`: actor, bounded local scatter controller and lifecycle handler.
- `tutnt/shaders/grass.fp`: soft root and alpha-edge treatment.
- `tools/build_grass_sprites.py`: validates RGBA assets and normalizes sprite bounds/scale via TEXTURES; it never changes image pixels.
- `tools/test_grass.py` and `tools/fixtures/grass/`: engine checks for eight variants, bounded unique actors, floor/material safety, save/load and quality changes, plus before/after captures.

The standard `tools/build_utnt.py` refreshes grass sprite definitions before the
package snapshot; `tools/build_grass_sprites.py --check` checks them independently.

Reference: [ZDoom sprite format](https://zdoom.org/w/index.php?title=Sprite).

Validation: UZDoom 5.0.1 passed 60 runtime assertions across TNT01 (OpenGL),
TNT02 (Vulkan) and TNTLE (Vulkan). All eight variants, unique nonblocking actors,
grass-only floor attachment, changed materials, moving floors, quality zero and
repeatable save/load/quality restoration passed. The grass-only staged source
also passed independent engine compilation and the TNTLE runtime suite.
Screenshots were reviewed for pixel scale, floor colors and soft root transitions.
