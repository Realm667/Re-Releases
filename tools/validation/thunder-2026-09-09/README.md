# TNT02 thunder validation

Both UZDoom 5.0.1 backends, 1920 × 1080, 15 assertions each. Includes all 551 exterior sectors, cold/desaturated palette, three sky viewpoints, sky/world-light state, save/load, indoor and solid-overhang roof checks, and automatic return to baseline after the real pulse sequence. Image checks confirm moving clouds, localized sky and world light gain, and no image change in the sampled indoor area during lightning.

An immutable previously built package plus the new thunder resources was used to isolate concurrent unfinished portal/UI work. `snapshot.json` records the base and test package hashes and every owned runtime asset. Fixtures are excluded from the game package. Read `thunder-results.json` for measured values. Software rendering, full campaign playthrough and a multiplayer session were not covered by these runs.

Repeat with `python tools/test_thunder_runtime.py --engine <uzdoom.exe> --iwad <doom2.wad> --mod <tutnt.pk3>`. Use `tools/test_thunder_structure.py --before <baseline.wad> --after <updated.wad>` for preservation checks.
