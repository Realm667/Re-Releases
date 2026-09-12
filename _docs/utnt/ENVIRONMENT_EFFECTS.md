# Environmental presentation

Updated 2026-09-11 after the third visual review. Four localized environment
options remain. Local lava heat now runs in the campaign and follows the existing
heat enable/strength and reduced-effects settings.

## Current behavior

- **Rain-wet surfaces:** native planar reflections show actual walls, actors and
  sky in irregular wet patches on eligible horizontal TNT02 floors. A material
  alpha mask keeps dry areas opaque and reveals at most 16% of the reflected
  scene in wet patches, weighted by viewing angle: half the approved previous intensity. A minimal native
  transparency selects the translucent draw pass; the material supplies the mask. Artificial blue-grey sky
  sheen and the previous specular coat are removed. The existing 3,178 candidate
  floor/wall faces retain their textures, scale, relief and terrain. Walls and
  unsupported floor types only darken slightly when wet; they do not mirror.
  Native reflections are only enabled while wet, restored when disabled, and
  relinquished if map scripts replace the texture or reflectivity.
- **Underwater:** water level 3 enables general blur and increasing distance blur.
  At 256 units the sample radius is about 3.2 output pixels, increasing to 5.85
  at 1024 units. Water/slime/blood tints remain; existing liquid distortion is
  independent. Reduced effects disables the additional treatment.
- **Caustics removed:** no runtime water-light branch, placement bindings, water
  material aliases or generated water shader remain. Original liquid rendering
  and underwater atmosphere remain independent.
- **Footprints:** approved alternating snow and wet sole marks are unchanged,
  including moving-floor support, budgets and lifetimes.
- **Mechanisms:** one cloud is emitted every 2–5 tics while a floor, door or
  ceiling moves. A jittered grid visits the sector area; no complete start/stop
  burst remains. Four soft shapes retain size, aspect, orientation and drift
  variation. Individual clouds fade in over six tics, then fade over 2–3 seconds.
  Their transparency is independent of mover start/stop. Both position endpoints
  follow their supporting plane; closing gaps fade clouds out over ten tics.
  Nearby motion adds a small, silent native quake: stronger decaying impulses
  at start/stop, lighter vibration while moving, falling to zero within 512 units.
  Quakes have zero damage radius and zero thrust and respect reduced effects.
- **Scenic lighting:** remains removed, as approved.
- **Local lava heat:** generated source tables cover eligible lava floors and
  visible lower/middle/upper wall pieces in all nine lava-bearing campaign maps.
  No actors need to be placed by hand. At runtime, up to six invisible cosmetic
  anchors follow nearby camera-facing sources (three at medium, one at low
  quality), with hysteresis and soft transitions. Overlapping volumes combine
  by their strongest mask, keeping displacement at the approved maximum of
  3.5 pixels per component instead of multiplying it. The final pass adds a
  restrained amber haze and a five-tap warm-pixel bloom inside the same occluded
  mask. The haze/glow is applied once, including where several sources overlap. The original laboratory
  prototype remains available separately for comparison. Switch that prototype
  off when reviewing production heat to avoid stacking the two systems.

No production map geometry is rewritten. Start a fresh map after updating;
older saved environmental objects and tables are not a migration target.

## Rendering limits

Native planar reflections are limited here to horizontal floors without existing
reflectivity, nonstandard portals, height-transfer water or 3D-floor stacks.
Vertical walls and slopes cannot use this masking path. Native mirror rendering
must be supported/enabled by the hardware renderer. This is not screen-space
reflection or a renderer modification; reflected scene rendering has a cost.

Rain exposure uses a bounded grid, about 64 map units with a per-face cap. Roof
and rain-direction traces include solid 3D floors. Boundaries of partial overhangs
remain approximate, and newly visited large surfaces take time to settle.
Wet values interpolate smoothly; integer lattice hashing avoids noise seams.

UZDoom 5.0.1 custom postprocessing does not expose native scene depth. The camera-
aligned 8 x 4 static-geometry ray grid estimates underwater distance. It excludes
actors and cannot resolve every silhouette. Heat uses that grid over its projected
actor bounds and conservatively clips against nearby geometry. Thin occluders,
portals, stereo views and complex stacked volumes remain approximation limits. Generated control sectors are excluded; this does
not reconstruct arbitrary 3D-floor top surfaces or dynamically created geometry.
Parameters stay within a conservative 128-byte GPU budget per pass. The six
consecutive heat passes carry the maximum mask in intermediate RGBA16F alpha;
the final pass restores alpha to one. At most 192 local geometry rays run per tic.

Computed ACS movement tags and polyobjects are not guaranteed automatic mechanism
discovery. Snow marks remain visual and do not displace map geometry.

## Manual checks

Use hardware rendering, quality 3 and reduced effects off:

```text
UTNT_fxquality 3
UTNT_reducedfx false
weatherfx true
gl_plane_reflection true
UTNT_wetsurfaces true
UTNT_underwateratmosphere true
UTNT_footprints true
UTNT_mechanismfx true
netevent environmentstats
```

Load the current package plus the regenerated laboratory addon:

```powershell
& "F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe" -iwad "F:/DoomDev/DOOM2.WAD" -file "F:/DoomDev/Projects/realm667.git/tutnt.pk3" "F:/DoomDev/Projects/realm667.git/tools/fixtures/environment" +playerclass Marine +map ENVTEST
```anvpos 32 384 0`, walk and look back |
| Water: wall 256 units away | `netevent envpos 512 2304 -192`, `netevent envview 90 0` |
| Water: wall 512 / 1024 units away | `netevent envpos 512 2048 -192` / `netevent envpos 512 1536 -192`, `netevent envview 90 0` |
| Water comparison | `UTNT_underwateratmosphere true` / `false`; hall is 1024 x 1536 units |
| Long platform motion / dust | `netevent envfly`, `netevent envpos 650 384 112`, `netevent envview 0 25`, `netevent envstream` |
| Very short motion | `netevent envshort`; raises the platform by only two units |
| Door dust | `netevent envpos 1280 384 0`, `netevent envview 90 0`, `netevent envdoor`; door opens and closes |
| Moving ceiling dust | `netevent envpos 1408 1088 0`, `netevent envview 90 -15`, `netevent envceiling`; reverse with `netevent envceilingup` |
| Production heat | `UTNT_localheatprototype false`, `UTNT_shaderoverlayswitch true`, `UTNT_heatstrength 1`, `netevent envpos 690 128 0`, `netevent envview 0 0`, `netevent localheatstats` |
| Floor heat prototype | `netevent envpos 690 128 0`, `netevent envview 0 0`, `netevent heatlabmode 0`, `UTNT_localheatprototype true` |
| Wall heat | Same position; `netevent heatlabmode 1` |
| Heat comparison | `UTNT_localheatprototype true` / `false`; watch moving wall edges behind the hot volume |
| Heat diagnostic coverage | `UTNT_heatlabmask true`; **return to actual shimmer with `UTNT_heatlabmask false`** |
| Hidden source | `netevent heatlabmode 2`, `netevent envpos 128 384 0`, `netevent envview 0 -15` |

For campaign rain: `map TNT02`, then `warp 2944 3568 -496`. Look across the
island floor, allow roughly 10 seconds for wetness and compare the wetness option.

## Generation and validation

```text
python -B tools/build_environment_fx.py
python -B tools/build_local_heat.py
python -B -m unittest discover -s tools -p test_local_heat.py
python -B tools/build_environment_fx.py --check
python -B -m unittest discover -s tools -p test_environment_contracts.py
python -B tools/test_environment_fx.py --case compile --mod tutnt.pk3
python -B tools/test_environment_fx.py --renderer 0 --mod tutnt.pk3
python -B tools/test_environment_fx.py --renderer 1 --mod tutnt.pk3
python -B tools/test_environment_fx.py --case prototype --renderer 1 --mod tutnt.pk3
python -B tools/test_environment_fx.py --case motion --renderer 0 --mod tutnt.pk3
python -B tools/test_environment_fx.py --case motion --renderer 1 --mod tutnt.pk3
```

The test harness explicitly renders while unfocused, so OpenGL captures actual
scenes instead of retaining the startup image. Runtime checks cover rain exposure,
shelter, native mirror state, real submersion, footprints, mechanisms and save/load.
Contract checks cover shader budgets, packed distances, dust alpha/pivots/variants
and removal of water-light bindings. Visual evidence and exact console sequences
are under `tutnt/.codex/validation/environment-motion/` and
`tutnt/.codex/work/environment-motion/`. Test packages stay under
`tutnt/.codex/builds/`. These checks are not a complete campaign or multiplayer
performance certification.

## Campaign source inventory

Generated by `tools/build_local_heat.py`; the shared build regenerates these tables
after map edits. These are source locations, not simultaneously active actors.

| Map | Floor volumes | Wall volumes |
|---|---:|---:|
| TNT02 | 438 | 240 |
| TNT03A1 | 0 | 24 |
| TNT03A2 | 421 | 0 |
| TNT03B | 4 | 16 |
| TNT04A | 12 | 18 |
| TNT04B | 653 | 1 |
| TNT04C | 418 | 0 |
| TNT04CN | 827 | 1524 |
| TNTLE | 421 | 532 |
