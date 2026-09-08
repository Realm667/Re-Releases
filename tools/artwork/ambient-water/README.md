# Ambient smoke and water artwork

## Current revision: animated splashes and motion trails (2026-09-09)

`tutnt/graphics/utnt-water/water-atlas-v3.png` is the unmodified 1254 x 1254
RGBA output of the built-in Imagegen tool. The prompt is in `prompt-v3.json`.
TEXTURES.ambientwater selects nine 418 x 418 cells: six sequential crown shapes,
one droplet, one tapered motion trace and an overhead ring. Crown offsets align
each row to the waterline. The previous two atlases remain as historical assets.

Water is translucent and responds to map lighting. The material uses the source
alpha and a restrained slate-gray palette. Fine highlights remain readable in
dark rooms without additive blending or fullbright sprites.

Body impacts now have one crown, 34â€“42 units wide before modest expansion,
instead of a 90â€“110 unit crown plus three large outward crowns. It advances
through six frames over 22 tics. Eight small rebound drops leave short trails;
a subtle flat ring expands and fades over 28 tics. Footsteps and light impacts
retain a separate smaller envelope. The NODELAY terrain-trigger fix is retained.

Splash droplets use UTNTWaterTrail for motion traces.
Every other particle tic can record a local stationary trace of the current
trajectory, with a maximum length of 18 units and a six-tic fade. Trail length
depends on speed, so the apex is naturally shorter. Camera-relative orientation
and projected length prevent sideways stretching when viewed along the motion.
The material feathers the tail and sides. Traces are clipped against the source
waterline on ascent, and no trace is born below it. The short lifetime prevents
old traces following particles through a turn or impact. No new gameplay
projectile is introduced; traces are client-side VisualThinkers and use the
existing cosmetic impact budget.

## Removed unused fountain family (2026-09-09)

All nine Liquid_Fountain_B1A through B3C actors (editor IDs 20024-20032),
their nine Drop_B* missiles and UTNTFountainDropBase have been removed after
auditing all 13 campaign maps and their script sources/compiled lumps, in both
the source tree and active package. There were no placements or external callers.
The standalone tools/fountain-prototype add-on and runner were also removed.
The obsolete DROPA0 sprite and unused UWATC0 texture alias are removed.
UWATA0, UWATB0, UWATD0, UWSC*, their atlas and water shaders remain shared by
terrain splashes, rebound droplets, trails and rings. The engine's independent
WhiteParticleFountain (five in TNT04C) and GreenParticleFountain (ten in TNTLE)
are unaffected. Old validation captures describe the historical implementation.

## Ambient smoke

Smoker and all three DarkSmokeSpawner sizes retain four independently rotated,
aspect-varied silhouettes and their shared slowly changing breeze. The shader
uses a weighted nine-sample density filter and a broad density/edge falloff to
soften the formerly hard charcoal contour. Colors remain centered around
#333333 (material range approximately #1c1c1fâ€“#3d3d40). Existing puff counts,
lifetimes, quality/LOD controls, smoke toggle and source cleanup are preserved.
Torch and FireSpawner smoke materials are not changed.

## Validation and scope

`tools/test_ambientwater.py --mod tutnt.pk3 --renderer 0` (OpenGL) and renderer 1
(Vulkan) exercise three smoke sizes and Smoker, activation,
removal, smoke/quality controls and save/load. A real falling player verifies
terrain activation, the compact crown, all six animation phases, rebound drops
and their motion traces. Trail scale, lifetime, maximum length and waterline
bounds are checked, along with cleanup after sources stop. The removal passes
55 assertions per renderer (110 total); logs and the map audit summary are in
`tools/validation/fountain-removal-2026-09-09`. Earlier artwork captures remain
in `tools/validation/ambient-water-trails-2026-09-09`.

The approved mockups are art direction, not engine screenshots. The installed
effects retain each map's lighting and the existing smoke motion.
Smoker and DarkSmokeSpawner have no campaign placements in
the audited maps. They can be summoned for inspection; no map placements are
added. Water terrain splashes work on existing UTNT_Water surfaces. Blood,
slime, nukage and lava effects are unaffected.
