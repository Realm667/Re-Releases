# Industrial effects — revised after in-game review

## Current behavior (2026-09-09)

- Impact and electrical sparks align their long axis with their projected
  velocity. Random spin is disabled for streaks. The projection accounts for
  view yaw/pitch, map pixel stretch and perspective at the edges of the screen.
  Roll angles cross +/-180 on the shortest arc, avoiding an interpolated full
  revolution. Streaks use view-aligned billboards and centered sprite rotation.
- All 21 electrical spawners again create their original SparkFlare_W/R/O/Y/G/B/P
  at the source. Activation, original sound and the three spark pulses remain.
- TeleportEffects again renders its original X010 animation, TportSphere and
  TeleParticle emission, together with the new returning fragments. New sprite
  dimensions are 2.5 times the previous industrial version; launch velocities
  are doubled to spread the addition around the original core.
- UTNTRocket again runs the original flame and smoke trail states. Its visual
  explosion uses UTNTRocketExplosion, an exact copy of the original
  NewExplosionMedium body under a dedicated name. Its damage calls, missile
  properties and death timing remain unchanged. Other explosion families keep
  their existing implementation.

The existing teleport, fire, smoke and original flare assets are reused.
The industrial smoke material and unused trail classes remain available for
other effects and previously serialized objects. No bitmap assets were added.
Local industrial particles retain the existing quality, distance and emission
budgets (768 live particles, 64 pulse controllers, 24 geometry traces per tic).
Restored classic flare/teleport/explosion actors use their original lifetimes.

## Verification

The revision fixture checks native particle state, angle wrap, every flare color,
the simultaneous classic/new teleport layers, original rocket flame animation,
absence of the new rocket trail controller, original explosion sprites on an
actual rocket collision, and particle expiry. OpenGL and Vulkan logs and native
screenshots are in tools/validation/industrial-revision-2026-09-09.

The alignment screenshots place independent green world-space motion markers
behind eight gold streaks. Pixel analysis measures the two axes rather than
repeating the angle implementation. A second image includes movement toward and
away from the viewer to exercise perspective. The checker requires less than
6 degrees deviation at 960x540. See the recorded measurements for actual errors.

Run tools/test_industrial_revision.py with --engine and --iwad, optionally
--mod <PK3> and --renderer 0 or 1. This uses tools/industrial-revision-tests.
Run its check_alignment.py with an alignment screenshot path for the image check.
The historical initial-implementation tests and evidence dated 2026-09-08
describe the earlier design; their rocket expectations predate this restoration.

Engine angle interpolation reference:
https://github.com/UZDoom/UZDoom/blob/trunk/src/playsim/p_effect.cpp
Renderer reference:
https://github.com/UZDoom/UZDoom/blob/trunk/src/rendering/hwrenderer/scene/hw_sprites.cpp
