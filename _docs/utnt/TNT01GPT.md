# TNT01GPT — The Ashen Liturgy

TNT01GPT is an independent UTNT bonus map built from the TNT01 analysis and the
Ashen Liturgy concept. Start it through its episode entry or with `map TNT01GPT`.
It requires the UTNT resource package and a ZDoom-compatible engine supporting
UDMF, ACS and solid 3D floors; validation targets UZDoom 5.0.1.
The original TNT01 and its campaign route are not replaced.

## Layout and progression

The eight areas form a courtyard-centered loop. The rocky Ash Gate provides an
early super shotgun. The courtyard leads west to the Chain Library, where a
sunken reading floor, stairs and an overhead gallery lead to the blue skull.
Picking it up opens the library shortcut and wakes enemies behind bookcases.

The blue gate leads east to the Machine Monastery and its rocket launcher.
The raised console shuts down the green reactor, changes its light and height,
opens reinforcement closets, and releases the upper bridge and drainage loop.
The upper bridge crosses the north corridor as a solid 3D floor; the crypt
beyond contains the plasma rifle and red skull. Taking the skull opens the
crypt's return gate to the library. The courtyard's north gate requires both
the red skull and reactor shutdown. It can be opened from its far side to
avoid trapping a player who drops into the north corridor.

The Seal Court uses a recessed octagonal floor, two sets of stairs, four cover
pillars and an outer movement loop. Crossing its entrance starts the encounter;
its entrance closes after a warning and reinforcements follow. The exit opens
only when both authored guardian groups have been defeated. The map then ends
through the normal Doom statistics and ending sequence.

| Area | Primary elevations | Role |
|---|---|---|
| Ash Gate | -64 to 0 | Weapon introduction and terraced opposition |
| Courtyard | 0 | Orientation, two locks, reinforced return visit |
| Chain Library | -64, 0, +128 | Blue skull and overhead combat |
| Reliquary Crypt | +128 | Red skull, plasma and final supplies |
| Machine Monastery | 0, +32, +96, +160 | Reactor switch and upper return route |
| Drainage | -48, -32, 0 | Optional supply and return loop |
| Seal Court | -48, 0 | Two Hectebi on UV and staged companions |
| Exit | +64 | Completion |

The established Quake stone, wood, library, metal and machinery textures are
reused. Warm library and crypt lights contrast with the green reactor and red
sky. Blue and red lamps identify progression gates. Supplies and three secrets
are placed separately from mandatory progression objects.

## Play parameters

There are 120 preplaced monsters on UV/Nightmare, 103 on HMP and 87 on the two
easiest skills. The easier roster retains one Hectebus in the final encounter.
The map has three secrets and eight cooperative starts. Keys and switches use
shared map-local ACS state; repeated activation is guarded and the state is
serialized with saves. Respawning players recover acquired keys and can rejoin
an active arena. Deathmatch is not an authored mode.

## Sources and rebuilding

- `tutnt/maps/tnt01gpt.wad`: playable UDMF map with compiled ACS and ZDBSP nodes.
- `tools/build_tnt01gpt.py`: authored geometry, placement and WAD generator.
- `tools/map-sources/tnt01gpt.acs`: map-local progression and encounters.
- `tutnt/mapinfo/MAPINFO.tnt01gpt`: bonus episode and map registration.
- `tutnt/language/LANGUAGE.tnt01gpt`: English text; translations live in the
  regular German, Spanish and French catalogs.

The generator requires Python, Shapely 2.1.2, ACC and ZDBSP. Supply compiler paths
with `--acc` and `--zdbsp` when their defaults are not applicable. Run
`python -B tools/build_tnt01gpt.py` to regenerate the WAD; `--check` verifies byte-for-byte reproducibility. The sky-edge generator appends bonus maps after the shipped campaign, preserving
existing campaign material IDs and tables. The normal package build
uses the checked-in WAD and does not require Shapely or rebuild this geometry.
Manual editor changes to the WAD must be reconciled with the generator before
regenerating. Work output remains under `tutnt/.codex/work/tnt01gpt/`.

## Validation

`python -B tools/test_tnt01gpt.py` runs a native-engine regression against the
current package plus the authored map. It walks the critical connections using
normal player movement, activates authored switch lines, checks key pickup
scripts, and exercises the arena completion logic. Teleports delimit individual
route segments; monsters are non-solid for this deterministic geometry test.
This is not an autonomous combat playthrough or a multiplayer network test.

Local logs, screenshots and validation records are kept under the corresponding
`tutnt/.codex/` folders. Validation on 13 September 2026 passed the complete critical route and actual
level exit, all three skill rosters, and 29 state/skill assertions including a
real save, fresh map reset and load restoring both state and opened gates.
Re-run that check with `python -B tools/test_tnt01gpt.py --state`. The common
package passed its full ACS and engine build checks; four-language validation,
14 localization tests and native font coverage also passed. Original TNT01's
source WAD hash remains unchanged. Difficulty pacing remains subject to human
playtesting; no multiplayer network session was simulated.