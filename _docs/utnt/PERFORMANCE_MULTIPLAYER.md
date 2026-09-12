# UTNT performance and multiplayer

Target: UZDoom 5.0.1 and compatible later versions. Implementation dated 2026-09-12. Runtime checks use UZDoom 5.0.1; later binaries require the same regression suite.

## Simulation ownership

The actual local actor flag is `CLIENTSIDE`. UZDoom accepts but ignores the legacy `CLIENTSIDEONLY` spelling. Named `Random` streams are still gameplay streams; cosmetic branches now use `CRandom`, `CFRandom` and local selection variants.

The conversion covers 361 legacy cosmetic classes, modern fire/steam/portal effects, both gore implementations, lava menisci, CRT probes, heat anchors, snow footprints and skyline models. Local actors are non-solid, non-shootable and excluded from the actor blockmap; debris keeps world-surface movement and animation. They do not receive network entity identities. Each peer can select different quality, distance and reduced-effects workloads.

Damage, AI, collision and attack scheduling remain shared, including damaging projectile descendants PBCluster and MiniFirePuff. Map-facing steam/fire/portal markers retain their shared TIDs and activation state for ACS. Cosmetic arguments use local randomness only when passed exclusively to a local effect. Native blood creation still has a short shared entry path.

Native replacements must retain the original client/shared domain. Blood, ice fragments, crushed gibs and teleport fog use shared bridges, then transfer color, render style, pointers and velocity to local visuals. Original DECORATE blood art remains the fallback when BLUDTYPE is absent. A local debris adapter preserves the native distributions for the existing Health=1 gib definitions. Native damage rolls remain shared.

## Consolidation

| Area | Change |
| --- | --- |
| Settings and emitters | One client runtime caches settings once per tic and maps source identity to fire, steam, rocket, portal and gore emitters. It owns both particle budgets and compacts dead entries once per second. |
| Gore | Replace inventory polling with local watchers. Modern and legacy persistent gore share a bounded cleanup pass; remove only registered gore types and clamp negative limits to zero. |
| Weather and heat | Reuse XY buckets to narrow candidates while retaining exact range, height, texture and visibility checks. Cache weather sprite sizes and view trigonometry. Pad heat candidate refresh for camera movement. |
| Environment canvas | Upload on wetness/reflection revisions, option/world changes or a one-second safeguard. Preserve byte quantization and row-run drawing. |
| Depth estimates | Reuse tracer and packed samples; resolve the containing sector once per batch. Camera, FOV and projected sample rectangle invalidate the cache. |
| Lava | Share plane/texture revisions per sector and update models only when relevant geometry or textures change. |
| Heat shader | Run only active passes. First/last role bits retain mask accumulation and final glow; pixels outside heat skip noise/glow work. |
| Relief shader | Reuse height texture size and mip selection during ray marching, refinement and shadows. Preserve bilinear filtering, signed UV wrapping, sample counts and material settings. |
| Skyline canvas | Upload glow data at most once per game tic, with world invalidation. |

Local particles still cost CPU/GPU time. Moving them out of shared simulation does not reduce shared gameplay inputs or guarantee a specific network bandwidth saving.

## Save/load

UZDoom skips non-static EventHandler.WorldLoaded on savegame restore. Persistent handlers therefore hold a transient client-runtime reference and reconstruct caches when it changes. Lava, CRT and skyline reconstruction removes stale render-only instances before installing the local pool. Saved wetness, weather clocks, foot state and mechanism grouping retain their persistent owners. Obsolete NashGore inventory class names remain loadable with their old polling disabled.

## Regression entrypoints

- `tools/test_four_player.py --players 8 --mod <package>`: eight real peers, different effect settings and local spawn counts, simultaneous respawn and disconnect; verifies actual local flags, network identity exclusion, shared gameplay classes, compatible replacements, registry reuse and spatial boundaries.
- `tools/test_source_coop.py`: both Source endings with opposing FX settings.
- `tools/test_steam_coop.py`: common activation with local steam options.
- `tools/test_cosmetic_lifecycle.py`: original-map pool counts and heat references after save/load.
- `tools/test_lava_lips.py`: moving floors, texture changes and save/load.
- `tools/test_environment_fx.py` / `tools/test_environment_contracts.py`: saved surface, foot and mechanism state.
- `tools/test_relief_uv.py`: signed/repeated UV oracle and floor views on Vulkan/OpenGL.
- `tools/check_engine.py`: engine completion, parsing, replacement-domain and thinker-list errors.

Artifacts stay under `tutnt/.codex/`. The immutable before package is `builds/performance-multiplayer-before.pk3`, SHA-256 `c95210918a02cd242bfd6c0ac4aaa562de2d5658b51b3848812f5cee173d47bf`. Comparison builds retain its resources and isolate this task's code from concurrent material/map work. The shared integration package is built separately from the complete working tree.

## Measurements

Run `tools/profile_combat.py --mod <after> --compare <before> --renderers 1 --gore 1024 --repeats 2 --prefix performance-multiplayer`. Alternating AB/BA sequences in TNT02, TNTLE and TNT04CN report frame intervals, upper percentiles and shared actor counts at identical quality settings. This is a scripted weapon/effect workload, not an identical gameplay replay: removing cosmetic gameplay-RNG consumption changes later random sequences. It does not establish a guaranteed FPS gain for every view, machine or multiplayer session.

Measured on Ryzen 9 7950X / RTX 4080, Vulkan, uncapped rendering, quality 3, gore limit 1024, two runs per version/map. Values average the two run statistics; lower frame time is better.

| Map | Mean frame ms before / after | Reduction | p95 ms before / after | Shared actors before / after |
| --- | --- | --- | --- | --- |
| TNT02 | 4.026 / 2.954 | 26.6% | 5.762 / 4.375 | 3789 / 2754 |
| TNTLE | 7.628 / 4.285 | 43.8% | 12.567 / 7.789 | 5114 / 2060 |
| TNT04CN | 12.391 / 11.048 | 10.8% | 14.249 / 13.225 | 2785 / 1073 |

All twelve measurement runs completed without engine errors. TNT02 produced no kills, so that row primarily measures the environment/effects path. TNTLE reported 344 versus 343 kills; it is not a bit-identical combat replay. Shared actor counts exclude client actors and should not be read as total visible objects. Results: `tutnt/.codex/validation/performance-multiplayer-profile-results.json`.

The extended eight-peer fixture passed 157 assertions on six peers, 158 on one, and 149 on the disconnecting peer. Both Source endings passed 57 assertions per peer; steam passed 14/12. Save/load restored TNT02's 9 lava lips, 158 CRT probes and 185 baseline skyline models; the isolated moving-lava fixture passed 12 assertions. These counts belong to the isolated comparison resources and can differ in the current integration maps.


Integration validation also passed all eight peers, both Source endings, the steam toggle test, four save/load runs (TNT02/TNTLE on Vulkan/OpenGL, six assertions each), and the moving-lava fixture (12 assertions). Current integration pools restore 9/158/256 lava/CRT/sky actors in TNT02 and 118/21/560 in TNTLE.

The integration environment fixture passed 20 assertions. The signed/repeated UV oracle passed all 243,200 sampled pixels on each of Vulkan and OpenGL; three floor views were captured per backend.

All three 1280x720 Vulkan floor views were pixel-identical between the before and optimized relief shader (zero differing pixels per view).
