# Light rays

The eight original LightRay actor classes are enhanced in place. Existing editor
numbers, script class names, activation states, colors, alpha, signed scales and
wall-sprite orientation remain authoritative. Maps need no edits. The current
map inventory contains 206 placements in TNT01 and 276 in TNT02.

## Rendering

Ordinary VOLT A downlights use a twelve-plane radial OBJ model (24 triangles). Its
256-unit envelope and attachment offset match the original sprite. The original
alpha mask remains authoritative for visible width, length and source placement;
the shared material adds gentle density movement without lengthening the shaft.
Squared view-facing weights normalize the twelve layers as the camera moves around
the lamp; a projection correction preserves the apparent profile width. A
per-fragment camera-distance fade hides nearby sheets gradually. A narrow axial
fade suppresses the radial star when looking directly along the shaft.
The original sprite remains the fallback when model rendering is disabled.

Wall sprites and the irregular VOLT B mask keep their authored planes; TNT01
uses negative Y scale and TNT02 uses rolled sheets. They receive the shared
slow density variation and camera fade without changing their placement. The
orange TNT02 grille rays retain their separated streaks. A grazing-angle fade
softens sheet edges. Dust and light placement follow the engine's signed scale,
yaw, roll pivot and pixel-aspect transformation, including rolled grille sheets.
The gentle material animation does not alter actor alpha.

Nearby rays trace their axis and four surrounding samples against blocking walls,
floors, ceilings and solid 3D floors. The nearest sampled obstruction bounds the
material, with a six-unit soft ending. A client canvas passes at most 32 geometry
records to the shader; attachment positions identify the original sheets and
model slices without adding state to map actors. Records fade in and out.
This is bounded simulated scattering, not ray-marched or shadowed volumetric fog.
It does not sample the screen depth buffer or cast moving actor shadows. The
sampled bound is conservative, rather than an exact per-pixel obstacle silhouette;
untracked distant rays retain native depth testing and their original footprint.

## Local detail and lighting

Client-side emitters add sparse, fading dust inside nearby shafts. Dust inherits
the authored tint and opacity, follows signed scales/yaw/roll, and rejects floor,
ceiling, solid 3D-floor and water volumes. Adjacent open sectors remain valid.
An explicit owner assignment avoids ZScript's case-insensitive parameter/member
shadowing, which previously destroyed every grain before its first visible tick.
The dedicated dust material feathers each grain independently of fire shaders;
its peak opacity remains 0.25 times the source alpha, with lifetime and camera fades.
Grains additionally sample a bilinear density table generated from the actual
VOLT A/B alpha masks, including the gaps between grille streaks. Downlight samples
use radial distance; geometry bounds and detail fades further reduce brightness.
Dust therefore disappears gradually as it drifts out of the illuminated volume.
Particles measure 1.8–3.2 map units and live 90–140 ticks, emitted every 12 ticks
at normal quality or 8 at high quality within the shared ambient budget.

Regular downlights and directed VOLT B wall sheets add restrained, attenuated
spotlights. The central geometry trace finds the first receiving surface up to
768 units along the ray. Light range follows this distance rather than visible
sprite length, so high ceiling lamps can illuminate the floor. Lamp position,
direction and tint follow the same transformed ray as the dust. Short grille rays
contribute less at distant receivers; faint decoration and already bright rooms
receive no extra lamp. Nearby authored dynamic lights and overlapping receivers
reduce additional brightness. Existing sector lighting remains unchanged.

The existing effect quality, reduced-effects and LOD settings govern optional
dust and lamps. At most 32 emitters and 12 light anchors exist locally, with
640-unit emitter and 448-unit dust ranges. Distance and quality transitions fade
the details smoothly. A source's proximity, size, opacity and view direction
determine its budget priority. Replacement requires a substantial priority gain;
lamp cooldowns prevent repeated exchanges and waiting lamps start at zero opacity.
Low/reduced effects retain the shaft material and bounded geometry cache while
fading out dust and lamps. Cosmetic random numbers use a separate stream.
Map actors never store client objects; registry ownership and finite lifetimes
cover deactivation, destruction, save loading and map changes.

## Maintenance and validation

- `tools/build_light_ray_model.py --check` checks the reproducible model.
- `tools/build_light_ray_masks.py --check` checks the generated dust density tables.
- `tools/build_definition_tables.py --check` checks the definition modules.
- `tools/test_light_rays.py` exercises both populated maps, all eight classes,
  authored property preservation, activation, save/load, local budgets, reduced
  effects, smooth quality changes and near/side/inside views. It checks the TNT02
  screenshot grille's direction and reach, a real floor intersection, and an
  isolated rendered geometry-bound comparison. It checks visible dust and uses
  isolated image comparisons for dust, material movement and floor illumination.
  An unmodified sprite alias and fixed camera
  compare the visible width and length against the model, allowing at most 8%
  variation in brightness-weighted dimensions. Pass `--renderer 0` for OpenGL or `1` for
  Vulkan. Results belong in `tutnt/.codex/validation/light-rays/`.

Implementation: `tutnt/zscript/UTNT_Props.zc`,
`tutnt/zscript/UTNT_LightRays.zc`, `tutnt/shaders/light-rays.fp`, and the
`GLDEFS.light-rays`, `MODELDEF.light-rays`, `TEXTURES.light-rays` modules.

Validation targets UZDoom 5.0.1 on Vulkan and OpenGL, including active and
inactive saves in TNT01 and TNT02. Width and length comparisons measure visible
profiles against the original sprites, not merely unchanged actor dimensions.
Local results for the 14 September 2026 refinement are kept in
`tutnt/.codex/validation/light-rays-refinement/`. Both populated maps passed on
Vulkan and OpenGL, including 49 TNT01 and 47 TNT02 runtime assertions per renderer.
The original-size comparisons differed by approximately 2.5% in width and 0.5%
in length. Rendered geometry clipping preserved the upper shaft while removing
the deliberately bounded lower portion. The dust detector measures a localized
low-contrast contribution, allowing the requested transparency and density fade.
