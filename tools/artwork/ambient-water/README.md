# Ambient smoke and water artwork

The revised water atlas was generated with the built-in Imagegen tool on 2026-09-09.
The original 1254 x 1254 PNG is stored unchanged at
`tutnt/graphics/utnt-water/water-atlas-v2.png`. TEXTURES.ambientwater defines four
627 x 627 regions: ligament, droplet, splash crown and overhead ripple.
The material derives opacity from luminance; water uses translucent blending.
Ambient smoke reuses the four approved density silhouettes in
`tutnt/graphics/utnt-fire/smoke-atlas.png` through separate materials. The fire
material and all torch/FireSpawner behavior are unchanged. Ambient smoke's
material shades now range from charcoal (0.11, 0.11, 0.12) to (0.24, 0.24, 0.25),
centered around #333333. Increased opacity and denser texture coverage retain
the existing emission count, motion and four silhouettes.

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

## Revision 2026-09-09

Water now uses a hand-painted, visibly coarser slate-blue atlas. Its original
color is retained by the shader, replacing the earlier silver luminance ramp.
Compact drops and shorter coherent segments prevent long white string shapes.
The crown is anchored at its base so most of it appears above the water plane.

The terrain splash's first action now uses NODELAY: the single-frame Spawn
state previously skipped its action. Large body impacts spawn a broad crown,
an outward skirt, higher droplets and wider rings. A separate smallclass keeps
light impacts and footsteps small. Landings are tested with an actual falling
player and assertions for terrain activation, large crowns and rebound drops.

Campaign coverage: Smoker, DarkSmokeSpawner and Liquid_Fountain_* are defined
but not placed in the campaign maps. Water terrain impacts apply on existing
UTNT_Water surfaces. Ambient emitters and fountains are tested in the fixture
or with summon; this change does not add map placements.
