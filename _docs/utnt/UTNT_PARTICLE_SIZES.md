# Legacy particle sizes

Updated: 12 September 2026.

## Restored effects

The actor-to-particle migration used `FSpawnParticleParams.size` as though it
were a sprite dimension. In the hardware renderer a textured particle has
approximately `size * 5 / 7 / sqrt(pixelstretch)` units of height. That differs
from a sprite texture multiplied by its actor scale. The replacement lava
ember had a height of about 1.30 units at the default aspect ratio, versus the
original 3.84-6.40 units.

`UTNTLegacySizedVisual` now renders the affected finite-lived visuals using
sprite scales and existing local emission gates, cosmetic random streams and
ambient/combat budgets. Gameplay actors, map IDs, state timing, activation
triggers and map geometry are unchanged.

| Effect | Original dimensions restored | Implementation |
| --- | --- | --- |
| All twelve EmberSpawner variants | EMBRA0 at scales 0.06, 0.08 and 0.10: 3.84, 5.12 and 6.40 units | Read the three LavaEmber defaults, selected equally, matching EmberShot's weighted choices. |
| Rocket smoke trail | 23.66 x 20.93 units, from X038A0 at RockTrailSmoke scale 0.13 | Fit the intended X143J0K0 smoke image to the original envelope. |
| Rocket center smoke | 17.00 x 15.20 units, from X037A0 at RocketSmokeCenter scale 0.20 | Use the original actor's sprite scale directly. |

The trail also referenced a nonexistent texture name, `X143J0`; the actual
combined sprite lump is `X143J0K0`. The corrected lookup restores the intended
smoke image instead of the generic particle fallback.

Existing movement, opacity curves and lifetimes remain: 50 tics for lava
embers, 32 for trail smoke and 33 for center smoke. The trail particle's small
expanding envelope is replaced by its original fixed dimensions. The rocket
flame animation is retained. All new visuals expire naturally after emission
stops; they do not enter gameplay actor lists or saved simulation state.

## Other spawners checked

- Torch/barrel/floor fire and Lost Soul embers already use VisualThinker sprite
  scales, avoiding this particle-size conversion.
- Ambient smoke, pressure steam, water fountains/splashes and industrial
  sparks use explicit sprite dimensions in their newer implementations.
- Red teleport pads use ritual motes with explicit sprite dimensions. The
  other five TeleportSparkle colors use the separately reviewed chip/streak
  design, with deliberately varied particle sizes and a held bright core.
  Their initial migration size was replaced by subsequent artwork and size
  revisions; no blanket multiplier is applied to that design.
- The old generic impact smoke/spark adapters have no active state callers;
  current impact and electrical generators use industrial visuals.
- Effects which were not converted still use their actor scales.

This audit covers converted UTNT cosmetic emitter paths, not every effect in
other mods or a complete playthrough of every scripted map activation.

## Validation

`python -B tools/test_particle_sizes.py --engine <uzdoom.exe> --iwad <DOOM2.WAD>`
checks all twelve real ember spawner classes and a rocket's original state
loop, held stationary and collision-free within the test chamber. It checks
all three observed ember sizes, both rocket smoke layers, finite lifetimes,
source deactivation/reactivation, quality levels 0-3, reduced quality,
distance culling/recovery and expiry after source removal. It renders matched
legacy actor/new visual size probes in OpenGL and Vulkan, using the same
texture, scale, depth and alpha. Actor/visual texture filtering can affect
the apparent bright-core boundary.

Local evidence: `tutnt/.codex/validation/particle-size-results.json` and
`tutnt/.codex/logs/particle-size-*`. The initial TNT02 diagnosis is recorded
under `tutnt/.codex/work/ember-audit/README.md`.

Both hardware backends passed 26 runtime assertions each. The rebuilt shared
package passed its engine load and TNT02 check: nine live lava embers were
observed in the sampled area, including the original 6.40-unit size.
