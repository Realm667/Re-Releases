# TNT03A2 cavern presentation

Updated: 15 September 2026.

The lava cavern receives explicit distance fog, separate floor/ceiling lighting,
four asymmetric hanging rock formations, a flowing lava curtain with rock cheeks
and an outlet lip, three local lights, and three restrained smoke/dust sources.
This is a cosmetic layer: no source WAD, collision, platform route, sector tag,
map action, enemy placement or ACS script is edited.

## Source and placement

`tools/build_cavern.py` generates the OBJ scenery, MODELDEF module, actor classes
and sector/placement manifests. The regular package builder regenerates these
assets and `--check` rejects stale output. The generator checks the actual map
before placing the hanging formations above lava beneath the high ceiling.

The curtain follows the east cliff of the first chamber, near (5470, -4040),
from the existing ledge at roughly -248 down to the lava at -1500. Its bowed
surface, irregular rock cheeks and shallow lip conceal the edges against the
original cliff. It uses the shared lava-fall shader. Rock uses the original
IKWALL44 artwork. The four ceiling formations are distributed across the first,
second and lower chambers and remain outside the platform route.

The 538 sector bindings select the authored brown cavern region within
x=3700..8000, y=-6800..-3180 and its separate skybox sector. Each binding includes
a boundary line, its side and endpoint coordinates; runtime rejects a binding
if that boundary no longer identifies the same sector.
Material names are not identity checks because the existing area-material
handler replaces them with aliases before this handler runs.

## Lighting and lifecycle

`UTNTCavern` changes the original 0x62411d fade to a subdued warm 0x363029 and sets
explicit fog density 22. Authored static light values 150/134 receive a -6
adjustment, with +32 floor and -16 ceiling offsets. The seven moving platform
control sectors receive a +36 ceiling light offset for their top faces only.
Other authored light levels
are preserved. Settings are applied once, then serialized by the engine; map
scripts remain free to change lighting. Save/load and hub return do not
accumulate offsets. Outdoor day/night and snowfall sectors are not selected.
Fog density is installed before the fade update, which rebuilds UZDoom's cached
3D-floor light lists. A single post-setup refresh handles attached floor lists.

The client controller creates eight noninteracting scenery actors and three
lights. It rebuilds local objects after loading, clearing old instances from
both thinker pools. Smoke and dust use local deterministic phases, bounded
lifetimes, distance checks and the shared effect-quality setting. No gameplay
random stream is consumed. Effect quality zero stops new clouds; existing
clouds fade out. Cosmetic models remain visible as part of the room design.

## Validation

Run `python -B tools/build_cavern.py --check` and
`python -B tools/build_definition_tables.py --check` before packaging.
`tools/test_cavern.py` captures six views and checks model/light counts,
noncollision, bounded clouds and sector lighting before and after save/load.
Use `--renderer 0` for OpenGL and `--renderer 1` for Vulkan. `--live-overlay`
tests current cavern resources over an existing complete cavern package during
iteration; final acceptance uses the rebuilt package without this option.

Local screenshots and logs: `tutnt/.codex/logs/cavern-tnt03a2/`.
Machine-readable results: `tutnt/.codex/validation/cavern-tnt03a2/`.
`--hub` adds effect-quality shutdown and travel through TNT03A1 back to TNT03A2.
It requires 22 lifecycle assertions; the ordinary save/load run requires 14.
The shared integration package must be built from the full current workspace;
the isolated cavern package must never be copied over it.

Acceptance on 15 September 2026: UZDoom 5.0.1 passed all 22 lifecycle assertions
on OpenGL and all 22 on Vulkan, using complete packages without a live overlay.
The OpenGL test package and the newly built root `tutnt.pk3` have identical
SHA-256 hashes; Vulkan tested the root package directly. Six views per renderer
were captured and representative views were visually inspected. Source-map
geometry matches the task's starting snapshot, and
all generated cavern files also match generation against the committed map.
These checks cover single-player save/load, effect shutdown and hub return;
network multiplayer was not exercised for this change.
