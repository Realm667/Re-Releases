# Light rays

The eight original LightRay actor classes are enhanced in place. Existing editor
numbers, script class names, activation states, colors, alpha, signed scales and
wall-sprite orientation remain authoritative. Maps need no edits. The current
map inventory contains 206 placements in TNT01 and 276 in TNT02.

## Rendering

Ordinary VOLT A downlights use a six-plane radial OBJ model (12 triangles). Its
256-unit envelope and attachment offset match the original sprite. The original
alpha mask remains authoritative for visible width, length and source placement;
the shared material adds gentle density movement without lengthening the shaft.
Squared view-facing weights normalize the six layers as the camera moves around
the lamp; a projection correction preserves the apparent profile width. A
per-fragment camera-distance fade hides nearby sheets gradually.
The original sprite remains the fallback when model rendering is disabled.

Wall sprites and the irregular VOLT B mask keep their authored planes; TNT01
uses negative Y scale and TNT02 uses rolled sheets. They receive the shared
slow density variation and camera fade without changing their placement. This
is lightweight simulated scattering, not ray-marched or shadowed volumetric fog.
Geometry intersections use normal depth testing, not a depth-buffer soft-particle
intersection pass. The gentle material animation does not alter actor alpha.

## Local detail and lighting

Client-side emitters add sparse, fading dust inside nearby shafts. Dust inherits
the authored tint and opacity, follows signed scales/yaw/roll, and rejects floor,
ceiling, solid 3D-floor and water volumes. Adjacent open sectors remain valid.
An explicit owner assignment avoids ZScript's case-insensitive parameter/member
shadowing, which previously destroyed every grain before its first visible tick.
The dedicated dust material feathers each grain independently of fire shaders;
its peak opacity is 0.25 times the source alpha, with lifetime and camera fades.
Particles measure 1.8–3.2 map units and live 90–140 ticks, emitted every 12 ticks
at normal quality or 8 at high quality within the shared ambient budget.

Regular downlights add a restrained, attenuated downward spotlight. A geometry
trace finds the first receiving floor, including solid 3D floors, up to 768 units
below the lamp. Light range follows this distance rather than visible sprite
length, so high ceiling lamps can actually illuminate the floor. Faint
decorative rays and wall sprites do not infer a new light direction. Existing
sector lighting remains unchanged.

The existing effect quality, reduced-effects and LOD settings govern optional
dust and lamps. At most 32 emitters and 12 light anchors exist locally, with
640-unit emitter and 448-unit dust ranges. Low/reduced effects retain the shaft
material and omit these details. Cosmetic random numbers use a separate stream.
Map actors never store client objects; registry ownership and finite lifetimes
cover deactivation, destruction, save loading and map changes.

## Maintenance and validation

- `tools/build_light_ray_model.py --check` checks the reproducible model.
- `tools/build_definition_tables.py --check` checks the definition modules.
- `tools/test_light_rays.py` exercises both populated maps, all eight classes,
  authored property preservation, activation, save/load, local budgets, reduced
  effects and near/side/inside views. It checks surviving, visible dust and uses
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
The 13 September 2026 visibility correction passed both maps and renderers,
including dust survival, cleanup, rendered movement and receiver lighting.
The Vulkan original-size comparison differed by 1.6% in width and 0.2% in length.
