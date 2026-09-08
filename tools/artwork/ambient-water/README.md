# Ambient smoke and water artwork

The water atlas was generated with the built-in Imagegen tool on 2026-09-08.
The original 1254 x 1254 PNG is stored unchanged at
`tutnt/graphics/utnt-water/water-atlas.png`. TEXTURES.ambientwater defines four
627 x 627 regions: ligament, droplet, splash crown and overhead ripple.
The material derives opacity from luminance; water uses translucent blending.
Ambient smoke reuses the four approved density silhouettes in
`tutnt/graphics/utnt-fire/smoke-atlas.png` through separate materials. The fire
material and all torch/FireSpawner behavior are unchanged. Ambient smoke's
maximum material RGB is (0.60, 0.60, 0.60), approximately #999999.

## Runtime behavior

Smoker and all three DarkSmokeSpawner sizes use independently rotated,
aspect-varied puffs in a shared slowly changing breeze. Consecutive births
choose different silhouettes. Lifetimes, opacity and lateral turbulence vary;
shader edge erosion breaks up wisps. Local quality, LOD, smoke toggle and the
existing particle budget remain effective. Emission stops with source states;
remaining puffs dissipate, and source removal cleans them up.

All nine fountain classes keep their IDs, speed (5/4/3), gravity (.125), launch
angles, one-missile-per-tic cadence and activation states. Existing missiles
carry the new jet/droplet graphics; transient local sheets extend the coherent
portion for narrow trajectories. No additional gameplay projectile is spawned.
Impacts add a short splash and rebound drops; ripple actors are client-side,
non-interactive, live 28 tics and only appear on water. Generic water terrain
splashes use the same artwork. Blood, slime, nukage and lava terrain behavior
and sounds are retained.

## Validation

`tools/test_ambientwater.py --mod tutnt.pk3` runs the nine fountain combinations,
all smoke sizes, source activation, removal, smoke/quality switches and save/load
on OpenGL and Vulkan in an isolated map. Screenshots and results are recorded
under tools/validation/ambient-water-2026-09-08.

The mockups are art direction references, not engine screenshots. Actual
rendered results use the existing map scale and scene lighting.
