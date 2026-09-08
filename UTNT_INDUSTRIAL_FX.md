# Industrial particle effects

Implements the five approved concepts: directed metal impact sparks and dust;
three-pulse electrical discharges; a green teleport impulse with outward and
returning fragments; flash/fire/ember/smoke explosion phases; and a short hot
rocket core with a continuous, widening smoke wake.

## Runtime

`zscript/UTNT_IndustrialFX.zc` owns cosmetic client-side VisualThinkers. Existing
map actor names, editor numbers, electrical activation/deactivation and gameplay
actions remain in place. The adapters cover NewPuff, all 21 directional/color
spark spawners, TeleportEffects, 13 New/MonExplosion variants, and UTNTRocket.
Explosion scales are 0.5 / 0.7 / 1 / 1.4 / 2, with concentrated/simple variants.

Existing approved teleport fragment, fire and smoke atlases are reused. The new
TEXTURES.industrial aliases and industrial-smoke.fp material give combat smoke
a separate density profile. No new generated bitmap assets are introduced.

The existing fxquality, reducedfx and distance controls apply. The local limits
are 768 live visual particles, 64 electrical pulse controllers, 24 geometry
traces per tic, plus the shared ambient/combat emission budgets. Sparks expire
on geometry contact or when the trace budget is exhausted. Rockets sample
distance instead of drawing a helix; jumps over 96 units reset the wake.

## Validation

UZDoom 5.0.1: 92 runtime assertions each on OpenGL and Vulkan, including all
families, activation, expiry, texture/scale validity, counter consistency,
quality off/low/high, reduced effects and simultaneous bursts. See
`tools/validation/industrial-fx-2026-09-08/results.json`, logs and screenshots.

A before/after fixture produced identical target health after hitscan batches,
an actual UTNTRocket collision/explosion and follow-up hitscan damage. Player
health/position after the teleport visual also agreed. This is a deterministic
gameplay comparison, not a full weapon-animation or multiplayer playthrough.
The rocket Death block and all weapon attack/damage calls were also compared
and are unchanged. Sound calls were preserved by source review; automated
engine tests run without sound. Save/load and network sessions were not tested.
There is no measured FPS claim.

## Reproduce

Use the existing tools/check_engine.py with --mod pointing at the built PK3,
--addon tools/industrial-fx-tests, --map UTNTIFX, --renderer 0 or 1,
--exec tools/industrial-fx-tests/visuals.cfg, --timeout 100,
--set UTNT_fxquality=3 and --set vid_maxfps=120. Set --engine and --iwad.
For the damage comparison, run tools/industrial-fx-damage-tests with the same
seed (the runner defaults to 667). Call the check_engine.run_case Python API
with mapname="UTNTIFX" and duration=160 against
before/after packages, then compare the UTNT_DAMAGE lines in the logs.
