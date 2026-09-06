# UTNT remaster implementation — 2026-09-06

Historical first-pass report. The current follow-up, map corrections, four-player coverage and updated acceptance tools are documented in [UTNT_SECOND_PASS.md](UTNT_SECOND_PASS.md). Use the second-pass structural check for the current sources; the original map-preservation check describes the first-pass baseline.

Runtime target: UZDoom 5.0.1. Tested with the local Windows build dated 2026-09-05, NVIDIA RTX 4080, OpenGL and Vulkan. ZScript language level is 5.0.0. Older GZDoom builds are no longer a supported target for these sources.

## Changes

1. Fixed the heat menu binding, swapped level 9/10 intro assignments, invalid negated map comparisons, per-player/per-portal bookkeeping, boss zero-HP/index/range guards, and voice/legacy ember parameter guards. Scout now starts with its declared 75 HP.
2. `tutnt_build.bat` compiles the common library plus all 13 embedded map scripts, builds a new deterministic ZIP, validates it in UZDoom, then atomically replaces the previous PK3. Deleted assets cannot linger. Failed compilation or engine validation preserves the existing PK3. Map `SCRIPTS` lumps are authoritative; extracted reference scripts are documentation only. The common library name is normalized to `TUTNT` for ACS imports.
3. Motion blur uses local camera movement in `RenderOverlay`; no `liveupdate` network messages remain. It normalizes movement by elapsed game time, applies bounded recovery/autostop settings, and resets after camera changes, teleport-sized movement, pause, death and load. Frozen/cutscene scripts feed a saved Behavior through ACS adapters.
4. Torch flames and animated rocket flames use client-side VisualThinkers. Decorative smoke, bullet sparks, rocket smoke, embers and teleport sparkles use native particles. Torch bodies/lights, gameplay projectiles, damage, weapon timings and editor IDs remain. Legacy externally callable actor names and ACS 444 remain as compatibility adapters. Existing authorship notices are retained.
5. Local quality 0–3, distance culling, reduced far-away emission and a client-thinker emission budget apply before creating effects. The cosmetic RNG stream is separate. Budgets are 32/64/128 emissions per tic; native particles additionally obey the engine particle limit. Quality zero produces no new flame visuals.
6. Heat sources are registered once, combined per player and checked every five tics; UI reads the camera's Behavior instead of scanning all inventories each frame. Source cleanup only runs for actual heat givers. Water distortion and zoom share one postprocess pass. Engine time uniforms replace manually updated shader clocks.
7. A saved map handler holds boss HP/group/end state. ACS retains all five original completion blocks; UI only interpolates and draws. The HUD scales to the viewport, has optional percentage text and a separate Source-shield appearance. Voice subtitles wrap locally and have a size option.
8. TNT04CN now delegates to the common checkpoint implementation while retaining its map-specific cleanup. Respawn checks destination existence. Corpses release the old `1000+p` TID. Portal state has 64 player slots and 64 independent portal slots. The campaign's existing start/checkpoint placements remain the practical player-count limit; two-player coop is tested, 64-player campaign play is not claimed.
9. `UTNTPlayerEffects : Behavior` is the deliberately limited Behavior migration for heat/cutscene state. NashGore's gameplay lifecycle remains intact; the review proposed a further conversion only if profiling justified it.
10. Player footsteps use `MakeFootsteps`, engine terrain parameters and a fallback surface sound. No per-step helper Actor is created. Terrain mappings use generic step sounds and distance timing. The menu controls the engine's footstep volume.
11. 360 referenced story/objective/voice/checkpoint strings are in LANGUAGE. A dedicated UTNT options menu includes tooltips, individual effects, boss/voice settings and a reduced-effects profile. Unused `fullhud_*` and old step-volume options are removed. Weather remains functional. The global renderer-menu override is removed.
12. Flame Actor adapters have alpha/scale interpolation. Shared, opt-in sky mist and distant thick fog are implemented for TNT03A1, TNT03A2 and TNTLE. It is off by default and is an atmosphere prototype, not volumetric weather.

## Validation and measured scope

- All 14 ACS modules compile with ACC 1.60; stale-bytecode verification passes.
- 26 campaign/title/intermission/ending map starts: 13 maps × OpenGL/Vulkan. Each case reaches an explicit completion marker after running the map. This is a startup/runtime smoke test, not a complete campaign playthrough.
- Six regression-arena cases: Marine, Scout and Commando × both backends. Includes actual GLSL execution, Behavior attachment, heat, cosmetic actors, boss updates and localized subtitles.
- Save/load restores boss state and player Behavior. A final focused regression covers the last cosmetic lifetime/cleanup adjustments.
- Two local network peers with different effect quality, movement and motion-blur settings pass portal activation/cleanup, shared checkpoint, real death, rebirth, checkpoint placement, and engine consistency checks. The test runner deliberately terminates only its two child processes after all assertions; that teardown exit code is not a game crash.
- Every non-`SCRIPTS`/`BEHAVIOR` map lump is byte-identical to the starting repository. All five boss completion blocks are source-equivalent after resolving the localized text. Every referenced localization key exists.
- Packaging checks verify deterministic output, removal of deleted inputs, and preservation of the previous archive after injected engine-validation failure.
- Controlled 40-torch scene, tic 300: baseline 1,047 Actors including 960 flames; remaster 87 Actors plus 960 client visuals. The sampled profiler tic measured about 0.189 ms for the old flame actors and 0.035 ms for the new flame visuals. These are individual CPU samples, not averaged frame times or a general FPS claim. Original and new profile logs/screenshots are retained locally.

The original `Unknown flat DOPE2` warning and TNT02's unconnected-edge warning also occur in the baseline. No map geometry was silently rebuilt to hide them. Full campaign completion, all secrets, arbitrary mod combinations, 8/64-player sessions, every 3D-floor/water footstep case and subjective audio/visual approval are not certified by these automated tests. Saves created before this structural migration are not a supported compatibility target; new saves were tested.

## Build and tests

Requires Python 3.11+, ACC 1.60, UZDoom 5.0.1 and a legally supplied Doom II IWAD. Local paths are configured in the ignored `tools/utnt-env.cmd`; no engine or IWAD binaries are committed. Other machines can set `UTNT_PYTHON`, `UTNT_ACC`, `UTNT_ENGINE`, and `UTNT_IWAD` themselves. `--skip-engine-check` is available for non-runtime build environments and explicitly does not certify engine compatibility.

From the repository root in a configured command prompt:

```bat
tutnt_build.bat
call tools\utnt-env.cmd
"%UTNT_PYTHON%" tools\build_utnt.py --check-only
"%UTNT_PYTHON%" tools\test_matrix.py
"%UTNT_PYTHON%" tools\test_coop.py
```

The small regression ACS module must be rebuilt with ACC after changing the imported common-library layout; `tools/compile_test_acs.py` performs this step. Test add-ons stay outside the game package. Logs, screenshots, test saves and per-case INIs are local artifacts. `tools/test_structure.py --baseline PATH_TO_ORIGINAL_TUTNT` checks the preserved map and boss contracts.

For the controlled profile, load `tools/profile-tests`, start UTNTPERF, wait for warm-up, then run `profilethinkers -t 12` and `profilecsthinkers -t 12`. `tools/profile.cfg` automates this with a screenshot; `--mod` in `tools/check_engine.py` selects a baseline source directory.

## Debugging and references

`tutnt_debug.bat` starts UZDoom's DAP server on port 19021 with an isolated debug INI. The repository's `.vscode/launch.json` attaches to it and maps the `tutnt` source directory. This configuration follows the official [UZDoom VSCode extension schema](https://github.com/UZDoom/UZDoom-VSCode/blob/master/package.json); the extension itself is not installed or required for builds/tests.

The current wiki export and UZDoom source snapshot remain under `_references`; their manifests document version, date and verification. No 2022 wiki snapshot is reintroduced.

Recorded evidence and source hashes: `tools/validation/2026-09-06/`. Test logs describe their exact coverage; earlier failed development trials are not presented as successful results.
