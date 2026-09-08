# TNT01: Blood-red storm

TNT01 now uses a dark crimson cloud sky with distant ridges and red valley haze,
based on the approved courtyard mockup. Two cloud samples drift in opposite
directions at different speeds; the mountain panorama remains stationary.

## Integration

- `MAPINFO.txt` assigns `USTSKY` only to TNT01.
- Thing 606 changes from the untagged SkyViewpoint (9080) to an inert MapSpot
  (9001). This disables the old off-map sky camera. All other map bytes, geometry,
  nodes, actors, SCRIPTS and BEHAVIOR remain intact. The unused sky sector and its
  original ceiling-scroll script remain in place.
- `GLDEFS.storm` defines six cube faces and their material shaders. The original
  shared `TNT_CL2` and `BERGE2` textures are unchanged.
- Mountains and haze are painted panoramic layers, not 3D geometry or volumetric
  fog. Clouds use animated texture sampling, not simulated volume clouds.

## Rendering

Cloud layers rotate at 0.00220 and -0.00092 panorama turns per second (about
7.6 and 18.1 minutes per revolution). The second layer contributes 18 percent.
The movement is slow but visible over several seconds. There is no map-wide
flashing light effect.

Spherical sampling makes all cube faces agree. Near the zenith the shader blends
to a planar overhead projection, preventing the pinched pole of a cylindrical
sky. Wrapped edge blending conceals the authored image join. Explicit bilinear
sampling supports the game's nearest-neighbour texture setting.

The mountain image uses a blue chroma key because the image generator's first
transparency request produced a painted checkerboard. The selected source has a
blue background. The shader keys individual samples before interpolation and
suppresses blue spill, keeping ridges stationary and avoiding blue outlines.
The two selected source images are 1774 by 887 pixels; each generated cube face
is 768 by 768 pixels. Original source pixels are preserved in the package.

## Rebuild and checks

`python tools/build_storm_sky.py` regenerates the static fallback cube faces,
GLDEFS and the six material shaders from the two source images and
`tools/storm-material.glsl`. Requires Python, NumPy and Pillow.

`python tools/test_storm_structure.py --baseline-ref 9c39d881c3eb3ec6184673e56f615c8328f39f97`
checks that the sole WAD change is the untagged camera's type.

`python tools/test_storm_runtime.py --engine <uzdoom.exe> --iwad <doom2.wad>`
tests the built PK3 in OpenGL and Vulkan at 1920 by 1080. It captures nine views
per renderer (courtyard, outdoor directions, another courtyard, arena, zenith
and ridge edges), tests save/load and checks six runtime assertions. Two images
five seconds apart verify moving clouds against a stationary, unlit mountain
region. Wall differences are reported separately because existing map lights
continue animating on masonry. Fixtures in `tools/storm-tests` are excluded
from the game package.

Validation evidence is stored under `tools/validation/storm-2026-09-08`.
Art provenance and the approved mockup are under `tools/artwork/storm`.
Start TNT01 fresh to use the new sky assignment and retired sky actor; saves
created with the old map retain their serialized sky camera.

## Cloud motion update - 2026-09-08

TNT01 now animates both cloud projections at exactly four times the original rates.
TNT03B has a slowly rotating polar cloud wall with a calm, softly blended eye.
The low panorama and mountains remain stationary; no map file is part of this update.
Both maps passed OpenGL and Vulkan runtime checks, including save/load.
The annular image comparison measured about 2.1 degrees of TNT03B cloud rotation
over five seconds. Rebuild checks covered all 26 generated sky resources.
Evidence: `tools/validation/sky-motion-2026-09-08`. Repeat with
`python tools/test_sky_motion.py --engine <uzdoom.exe> --iwad <doom2.wad>`.
