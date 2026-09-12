# Layered animated lava

The small repeating lava pattern is broken up by world-space variation and
independently moving layers. Existing `QLAVA`, `QLAVA2`, `QLAVASB`, `LAVA` and
`LAVAHR` materials receive the effect without editing the maps or replacing
their source images.

## Surface

Cooled rafts add a fourth layer above the existing liquid stack:

| Layer | World-space velocity (X, Y), units/second | Apparent depth |
| --- | --- | --- |
| Floating cooled rafts | (-4, +2.4) | 6-10 units above liquid |
| Original crust and large cracks | (-7, +4) | Surface |
| Channels | (-13, +8) | 2.5 units |
| Incandescent bed | (-22, +13) | 5 units |

The original crust layer moves about 4.4 times as fast as in the first implementation. Faster
currents remain visible through the openings in that crust. A bounded,
view-dependent parallax offset separates the lower layers, with a warm inner
edge at the openings. This is material depth, not displaced geometry: collision,
floor height and silhouettes remain those of the map.

The source texture supplies the broad crack pattern and palette. Additional
fine grain and soft, filled variations in the flowing melt are calculated per
fragment, rather than upscaled from 64x64 texels. Frequencies finer than a screen pixel fade with
distance. The fine heat field varies continuously across filled areas; it does
not highlight noise isolines, which would form an artificial orange net.
Original map-scale variation remains roughly 185 units for the large
cracks and 310 units for the broad variation field.

### Reference-based cooled crust and visible relief

The new `materials/lava/crust-height.png` is a 1254x1254 generated grayscale
asset based on the supplied reference's broken angular plates, curled folds,
chipped rims and layered basalt. It is an independently generated arrangement;
the reference photo itself is not shipped. The same asset supplies plate shape,
height-linked color variation, ray intersections and bump normals.

Two broad world-space fields at 410 and 157 units control crust groups. Whole
areas remain liquid between denser patches. Coverage is independent of the
texture's fine grain, preventing tiny pits from fragmenting solid plate tops.
The field travels with the plates at (-4, +2.4) units/second. Distorted atlas
coordinates, per-cell orientation changes and faded boundary pieces reduce
repetition and prevent straight cuts at nonmatching image edges.

Parallax occlusion mapping traces down from 18 units above the liquid to the
first visible height-field intersection, with up to 32 steps and five binary
refinements. Solid caps sit roughly 6-10 units above the bed; folds add smaller
height variation. This replaces the earlier fixed two-unit decal offset. The
ray slope is bounded at grazing views. Explicit bilinear filtering from mip
level zero works even when nearest texture filtering disables engine mipmaps.

Bump normals are finite differences of that same height field at the visible
intersection. Dynamic lights therefore follow the displayed folds and rims.
Height-linked charcoal variation keeps the folded material legible under
uniform sector lighting too. Molten gaps retain emission; solid caps do not.

Bump mapping computes normals from heights; a normal map stores the normals
directly. Both primarily change lighting. Parallax occlusion additionally moves
and occludes apparent surface details with the viewpoint, but does not create
mesh geometry, collision, new horizon silhouettes or changes to lava damage.
Falls retain the preceding layered shader.

## Falls

The front liquid ribbons descend at 64 units/second (previously 38), fine streaks
at 87, and the rear current at 110. Front opacity partially hides the faster rear
layer. A shallow, bounded parallax offset and distinct current shapes give the
curtain depth while retaining its original wall silhouette.

Three-dimensional world-space fields avoid restarting patterns at texture
boundaries. `LAVA` and `LAVAHR` have the same physical flow scale regardless of
their different texture scaling and offsets.

## Color and integration

Hot openings have their own material brightness, so dim sector lighting does not
extinguish the incandescent layer. Cold crust still responds to scene lighting.
Brightness remains orange and bounded; fog and the user's Bloom setting still
apply. Source colors, including the existing PLAYPAL, determine the palette.

`gldefs/GLDEFS.lava` binds `shaders/lava-surface.fp` and `shaders/lava-fall.fp`. The three
superseded surface Warp declarations are removed from `ANIMDEFS`; other Warp
definitions remain active. Map scrollers still execute, but these materials use
world-space motion rather than scrolling UV coordinates. No new actors,
particles, damage logic, network state or gameplay state are introduced.

OpenGL/Vulkan hardware material rendering is required. Software rendering keeps
the original images without the new animation. Animation uses the local render
clock, so phase is not serialized or synchronized between players.

## Reproduce validation

Requires UZDoom 5.0.1, DOOM2, Python, Pillow and NumPy. Set `UTNT_ENGINE` and
`UTNT_IWAD`, or pass `--engine` and `--iwad`. Files are generated under
`logs/lava-test`, or the supplied `--out` directory.

```text
python tools/test_lava.py --mod tutnt-lava-reference-relief.pk3 --renderer both --label package
python tools/test_lava.py --mod tutnt-lava-reference-relief.pk3 --renderer both --map TNTLE --label scene --bloom
python tools/test_lava.py --mod tutnt-lava-reference-relief.pk3 --renderer both --label lit --time 3.75
python tools/test_lava.py --mod tutnt-lava-reference-relief.pk3 --renderer both --label dark --time 3.75 --dark
python tools/check_lava_light.py --renderer both
python tools/test_lava_relief.py --project . --out logs/lava-relief --engine ENGINE --iwad IWAD --mod tutnt-lava-reference-relief.pk3 --renderer both
```

The runtime fixture checks moving surface pixels, an unchanged non-lava control
wall, downward fall motion, continuity between differently mapped `LAVA` and
`LAVAHR`, the additional surface variants, and material visibility after
save/load. The frozen-time fixtures compare exactly the same material phase at
sector lights 160 and 32. The checker requires the hot areas to retain their
brightness while the ordinary wall becomes dark. `--time` writes test-only
shader copies in the fixture; it does not change production shaders.

Final results and representative unmodified engine captures are in
`tools/validation/lava-reference-relief-2026-09-08/`. The earlier surface refinement
is retained under `tools/validation/lava-refined-2026-09-08/`. The preceding layered version is
retained under `tools/validation/lava-layered-2026-09-08/`. Earlier first-version evidence is
retained under `tools/validation/lava-2026-09-08/`. All 14 ACS modules were
checked for the preceding layered version without rewriting bytecode. This
extension changes the surface shader, adds a directional-light comparison, and
updates documentation; its package also passes the engine startup parser.

These are targeted rendering checks, including TNTLE with Bloom, not a full
campaign playthrough or a performance guarantee for other GPUs. The local PK3
contains the working-tree content present at build time; unrelated project
changes are not part of the lava source change.

The relief test freezes the shader clock and camera, then compares the real
height-derived normals with a test-only flat-normal override. Identical material
colors must match without dynamic lights, and moving a grazing light from left
to right must produce measurable shading changes from the bump normals. This
checks the actual engine lighting path rather than just a colored normal preview.

The reference-relief validation also compares frozen, identical views with and
without the ray intersection (`--mode flatdepth --pitch 45`) and renders a
coverage-only view (`--mode mask --pitch 90 --camera-height 850`) to verify both
open regions and crust groups. These overrides exist only in the test fixture.

Asset generation mode, final asset path and the complete prompt are recorded in
`tools/validation/lava-reference-relief-2026-09-08/asset-source.md`.
