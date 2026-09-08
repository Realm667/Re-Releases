# Liquid material redesign

Water, slime, blood, void and star surfaces now use world-space layered materials. The original blue/brown/gray water variants, olive slime, crimson blood, bronze void and white/amber stars informed the redesign. Lava is independent and unchanged.

## Bindings

| Family | Material names | Treatment |
| --- | --- | --- |
| Water | QWATER1, QWATER2, QWATER3, QWATER3A, QFWAT | Broad branching currents, fine ripples, submerged flow |
| Slime | QSLIME1, QSLIME2, IKSLIME1, IKSLIME2, SLIME05B | Partial granular skin, smooth sludge channels, slower motion |
| Blood | QWATERT6 | Merging crimson currents and dark pools, restrained wet highlights |
| Void | QTELEPT (flat), QTELEPOR (wall) | Three spatial layers of bronze flecks |
| Stars | STARSKY1, STARSKY2 | Three point-field depths, variable density, white/amber variants, subtle twinkle |

The two IKSLIME names were referenced by ANIMDEFS but had no source assets or current map uses. TEXTURES.liquids supplies native-palette aliases to QSLIME1/2. Terrain definitions, damage, sounds, map geometry and gameplay are unchanged. In particular, visual water variants retain their existing slime/lava terrain assignments.

## Surface and depth

Physical liquids use 1024 x 1024 scalar height artwork plus derived tangent normals. Top, middle and deep currents have independent directions/speeds. World-space placement, mirrored sampling, two rotated/scaled samples and broad irregular warping/blending reduce obvious 64-unit repetitions and keep neighboring sectors continuous despite different texture transforms.

Normals come from the same composite height field as the visible surface, with additional fine detail from the authored normal texture. UZDoom's Normal/Specular material path supplies the actual dynamic-light response. Height slabs are 10 map units for water, 14 for slime and 9 for blood. A seven-step height traversal with interpolated crossing replaces the old two-step offset; submerged layers have separate depth offsets and normal-driven refraction.

The earlier translation-only treatment was too subtle from player height. Surface currents now travel at approximately 46 / 17 / 32 map units per second (water / slime / blood), with independent crossing currents below. Travelling waves deform the height field, and sparse slime domes inflate and subside. Underlying layers contribute substantially to the visible color. Unresolved waves fade with screen footprint to prevent distant shimmer.

A broad, stylized environment highlight and height-based occlusion make the moving relief visible even without dynamic lights. This is an approximation, not a reflection of actual scene geometry. It remains attenuated by sector lighting; liquids do not glow in darkness. Actual dynamic lights additionally use the same evolving normal field.

Normal mapping changes lighting; parallax changes apparent sample position. Neither moves vertices, silhouettes, collisions or the actual sector floor. Relief is visible from an oblique view in ordinary sector lighting and under dynamic lights. Physical liquids are not fullbright. Cosmic points use selective emission and spatial layers rather than rock-like bump normals.

The height PNG channels store original / 2-pixel / 12-pixel prefilters. The shader explicitly samples level zero and blends these by screen footprint: this works with OpenGL nearest filtering, which does not always allocate higher hardware mip levels. A camera-relative horizon closure is reconstructed onto its flat plane before world-space sampling.

GLDEFS.liquids replaces ANIMDEFS warp/warp2 for these names to avoid double warping. Original assets remain available as static software-renderer fallback; the new material animation requires hardware rendering. Physical-liquid colors sample the current original textures, including their palette. Cosmic colors are fixed, source-inspired bronze, white and amber.

## Sources and regeneration

`tools/artwork/liquids/` contains the approved concept, three ImageGen scalar artwork sources, their exact generation prompts and a generated asset manifest. These are design references and build inputs; only runtime materials/shaders ship in the PK3. No painted source image is used as a normal map: normals are derived mathematically from the scalar heights.

Requires Python, NumPy and Pillow:

```text
python tools/build_liquid_assets.py
python tools/test_liquids.py --out logs/liquid-motion --engine PATH_TO_UZDOOM --iwad PATH_TO_DOOM2 --renderer both
python tools/test_liquids.py --out logs/liquid-relief --engine PATH_TO_UZDOOM --iwad PATH_TO_DOOM2 --renderer both --relief
python tools/test_liquids.py --out logs/liquid-player --engine PATH_TO_UZDOOM --iwad PATH_TO_DOOM2 --renderer both --physical --eye-level
python tools/build_utnt.py --engine PATH_TO_UZDOOM --iwad PATH_TO_DOOM2 --acc PATH_TO_ACC
```

Edit `tools/liquid-surface.glsl` or `tools/liquid-cosmic.glsl`, then regenerate. Generated fragment shaders should not be edited independently. The test fixture stays outside the game package. It exercises every name, split-sector transforms, floors/walls, animation, distant detail, save/load and both renderers. Frozen normal-on/off tests isolate engine dynamic-light response while retaining the same stylized environment contribution. Player-height tests run without a fixture lamp, require visible motion across at least 15% of the evaluated image, and export short animated WebP captures for visual review. Pixel changes alone are not a guarantee of convincing liquid motion. Tested with UZDoom 5.0.1.
