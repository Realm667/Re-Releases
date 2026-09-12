# UTNT cooperative compatibility

Updated: 12 September 2026.

## Eight-player starts

TNT04A and TNTLE now include player starts 5–8 (thing types 4001–4004) in
existing walkable start areas. Each inherits the original player-one start's
angle, skill and class flags. Existing starts, geometry, map scripts and other
WAD lumps are unchanged.

All regular campaign entries have eight authored starts, including INTERMAP
and ENDMAP01. Cursed Peak uses entry positions 0 and 1 in TNT03A1 and position 1
in TNT03A2. TNT03A2's position-zero solo editor start and TITLEMAP are not
cooperative campaign entry points.

The shared ACS portal arrays already support 64 players; ZScript player state
uses MAXPLAYERS. Existing checkpoints have eight authored destinations and the
respawn helper checks both occupied destinations and nearby fallback positions.
No player-cap increase, gameplay rebalance or replacement respawn system was
needed for this change.

## Repeatable checks

Use the same built PK3 for all peers. Both runners default to `tutnt.pk3`;
`--mod` selects a separate test package. Set `UTNT_ENGINE` and `UTNT_IWAD` to the
UZDoom executable and Doom II IWAD. For example:

```text
python -B tools/test_eight_player.py --static-only
python -B tools/test_eight_player.py
python -B tools/test_four_player.py --players 8
python -B tools/test_four_player.py --players 4
```

The campaign test launches eight real local network peers, checks all 13 entry
cases across 12 maps, verifies slot-specific positions, collision clearance,
unique pawn TIDs and peer synchronization, and skips the TNT04A intro through
its existing chapter controller. The route revisits TNT03A1 through its other
hub entrance. Expected positions come from the authored WADs; missing,
duplicated or disabled starts fail the static audit.

The arena test checks simultaneous death and checkpoint respawns for every
participant, retained keys/weapons/ammo, safe fallback around occupied spots,
independent client settings and synchronized continuation after one peer quits.
The historical four-player test now accepts `--players 8`; its obsolete fire
visual class reference was updated so it compiles with the current mod.

Runtime fixtures remain under `tools/fixtures/eight-player` and
`tools/runtime-tests`. Generated expectations live under
`tutnt/.codex/work/eight-player`; logs and validation results remain in the
central `.codex` directories.

## Validation scope

The eight-peer campaign entry sweep passed all 13 cases on every peer (913
assertions per peer) using UZDoom 5.0.1. The eight-peer arena regression passed
with 148–149 assertions on each remaining peer and 140 on the departing peer.
The four-peer baseline also passed (82–83 / 78 assertions). The test package
also passed ACS,
localization/font and engine compilation checks during the standard build.

These are automated local compatibility regressions, not an eight-person
campaign playthrough or an Internet latency/load test. Combat balance and a
full cooperative playthrough remain outside this change.
