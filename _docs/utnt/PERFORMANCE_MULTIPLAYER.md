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


## TNT04A bridge audit — 7 October 2026

The reported bridge battle was reproduced with the current TNT04A map. Its two
combat factions contain 61 and 205 tagged enemies. The camera is placed at
(-1408, 6300, 160), looking across the battle, and sweeps a fixed yaw arc between
level tics 140 and 490. An isolated fixture calls the existing intro-completion
script to start the encounter; residual intro text remains identical in both
versions. This is a short, seeded battle benchmark, not a tester savegame replay
or a long-session leak test.

### Confirmed bottleneck and implemented changes

The older DECORATE trails were client-side but did not obey the effect quality,
reduced-effects or distance settings. One profiler sample contained 541 Imp smoke
actors, 583 Cacodemon trail actors, 413 miniature Cacodemon trails, 432 TT1 smoke
actors, 249 plasma trails and 129 Mancubus trails. The sprite workload, including
unmodified flying blood, dominated the sampled rendering workload.

`UTNTBudgetedTrail` now admits only a bounded number of live trail actors per
client: 768 / 384 / 192 at quality 3 / 2 / 1, and none at quality 0. Reduced effects
use the quality-1 limit. New trails outside the existing effect distance are
omitted; beyond 768 map units they may only enter while the total pool is below
half the cap, preserving capacity for nearby combat. Accepted particles retain
their existing animation and natural lifetime. Lowering quality limits new
admissions; it does not abruptly delete existing smoke. Destroying or expiring
an accepted actor releases its reservation, and save/load reconstructs the local
pool. The scope includes TT1 descendants, Imp/Bruiser/Pyrocannon smoke, Cacodemon,
Mancubus/Hectebus and plasma trails. Dense or distant combat can consequently have
less secondary smoke; the actual missiles, damage, impacts and monster AI are
unchanged.

Skyline and terrain-edge checks retain their immediate initial update and
eight-tic cadence, but use a wall-derived phase instead of all running on one
tic. TNT04A has 272 such actors. The benchmark measures both changes together;
it does not isolate a separate speedup for the scheduling change.

### Repeated measurements

UZDoom 5.0.3 (23 September build), Ryzen 9 7950X, RTX 4080, OpenGL, 960x540,
uncapped rendering, VSync off, clean test configuration with normal default
quality settings. Three runs per immutable package, alternating AB / BA / AB;
no simultaneous engine benchmarks. Each row averages the three per-run
statistics. FPS below is the reciprocal of the averaged median frame interval,
not an independently averaged FPS counter.

| Metric | Before | After | Change |
| --- | ---: | ---: | ---: |
| Median frame interval | 51.60 ms | 38.05 ms | 26.3% less |
| FPS corresponding to median | 19.4 | 26.3 | 35.6% more |
| 95th-percentile frame interval | 68.94 ms | 51.83 ms | 24.8% less |
| 99th-percentile frame interval | 81.67 ms | 66.75 ms | 18.3% less |
| Local actor count at tic 490 | 5,457 | 3,300 | 39.5% fewer |
| Shared actor count at tic 490 | 625 | 625 | unchanged in all six runs |
| Kills at tic 490 | 85 | 85 | unchanged in all six runs |

Before medians: 51.01 / 55.38 / 48.43 ms; after: 37.04 / 38.39 / 38.72 ms.
All six runs completed without engine errors. These are measurements of this
view and machine, not a guarantee for other maps, resolutions or beta testers.
Vulkan startup stalled before reaching the map on this machine, so this audit
has no Vulkan performance result and did not alter the user's graphics settings
or pipeline cache.

Reproduce with `tools/profile_bridge.py --mod <after.pk3> --compare <before.pk3>
--repeats 3 --renderer 0`. The runner stores package hashes, frame samples in logs,
per-run statistics, actor counts, profiler output and screenshots under `.codex/`.
Results: `tutnt/.codex/validation/oct-bridge-final.json`.
Before SHA-256: `88f88cabf2a745a5b30a09d931eb30288a62d34f19e6e78a32325c35e573974a`.
After SHA-256: `896380ee804098a53138112145c649cab68a0e991cbd67f82c936d12d1d21fc7`.

The native `tools/test_legacy_trail_budget.py` fixture passed 61 assertions:
all quality limits, reduced effects, near/far admission, distance rejection,
13 actual trail families, local network ownership, intact shared damaging
projectiles, reservation reuse, natural expiry and save/load recovery. Existing
cosmetic lifecycle tests also passed six assertions each in TNT04A and TNT02,
including restoration of skyline, lava, CRT and heat pools.

### Remaining candidates and tester evidence

- Flying blood and gore remain a substantial part of the client actor workload.
  The persistent-gore cap does not bound every transient blood trail. Measure a
  long, blood-heavy battle before changing its appearance or cleanup policy.
- Distance blur can perform 456 depth traces per changing view plus multiple
  screen passes. Disabling it, heat or glow individually did not establish a
  dominant cost in exploratory bridge runs; they are not disabled by this fix.
- Wet-floor and CRT reflections still warrant measurements in the previously
  reported TNT02 exterior and TNT03A1 monitor room. Their existing capture limits
  and weather exclusions do not prove that every reflective view is affordable.
- Relief shaders are a possible GPU cost at higher resolutions; the bridge test
  does not justify reducing their authored quality globally.

For the next tester report, retain the exact build, savegame, map/position,
viewing direction, renderer, resolution, GPU/CPU and time until the drop. Compare
`stat rendertimes` and `stat renderstats` from that same view, with one setting
changed at a time. `profilethinkers -t 20` and `profilecsthinkers -t 20` record the
shared and local thinker workloads; let another tic run after these commands.
A before/after savegame or short movement route is preferable to unrelated FPS
screenshots. The new bridge runner provides a repeatable first reference case.

### Packaging and workspace scope

All five changed runtime resources live in editable `tutnt/` sources; the new
fixtures are tests only. Packaging uses the existing snapshot packager without
regenerating authored scenery or maps. Legacy package transformations remain:
TEXTURES module flattening, generated precache declarations and build metadata.
These pre-existing exceptions mean a literal source ZIP is not claimed equivalent
to the integration package. The packaged runtime changes are checked byte for
byte against their production sources.

The layout checker reports 15 pre-existing UDB `.dbs`, autosave and backup files
under `tutnt/maps/`. This audit did not create, move or delete those editor files;
its own temporary files stay under `.codex/`.


## Adjustable particle detail distance — 7 October 2026

The performance submenu now includes **Effect detail distance**. Each client can
adjust full / half / minimum particle-density distances, enable or disable the
gradual reduction, change the existing outer effect distance, and restore the
recommended distances. The menu and tooltips are available in English, German,
Spanish and French. Existing visual presets keep these three custom thresholds;
their existing quality and sight-distance choices still apply.

| Local user setting | Default | Menu range |
| --- | ---: | ---: |
| `UTNT_fxgraduated` | true | on/off |
| `UTNT_fxfull` | 768 | 128–8192, step 64 |
| `UTNT_fxhalf` | 1536 | 192–12288, step 64 |
| `UTNT_fxminimal` | 2048 | 256–16384, step 64 |
| Existing `UTNT_lod` | 2048 | existing distance choices |

These values are map units measured from the local viewing camera. Emission
probability is 1 up to the full-detail distance, smoothly approaches 0.5 at the
half-detail distance and 0.25 at the minimum-detail distance, then stays at 0.25.
The outer effect distance takes precedence: emission probability also smoothly
falls to zero over its final 128 units (or one eighth for shorter ranges). Thus,
at the default outer limit of 2048 there are no new optional particles, even
though the unconstrained minimum-density anchor is also 2048. Raising the outer
limit exposes the quarter-density plateau. The enable switch bypasses the new
smooth reduction but retains quality, budgets and the outer range limit.

Thresholds are cached once per tic. Runtime validation clamps console inputs and
keeps the half and minimum thresholds at least 64 units beyond their predecessor;
crossed sliders cannot produce division by zero or inverted density. The menu
tooltip explains the ordering and outer limit. Restoring recommendations resets
these distances, enables reduction and restores the outer range to 2048 without
changing overall quality or unrelated graphics options.

The admission decision runs at particle birth using a dedicated cosmetic random
stream. Existing particles keep their natural lifetime when a threshold changes
or the camera moves. No probabilistic test runs in a particle's visibility/lifetime
check. There are no additional per-particle line-of-sight traces.

Coverage: legacy projectile smoke/trails, legacy MCBlood particles and flying
blood trails, modern NashGore blood particles 1/2, ambient smoke and embers,
fire's optional smoke/embers, Lost Soul embers, pressure-steam births, rocket
smoke/flame trails, impact/electrical sparks and optional industrial explosion
smoke/teleport fragments. Existing quality-specific core fire/steam policies
remain in force. The invisible Cacodemon trail controller is not sampled twice;
its two visible children make individual decisions. Discarded sparks do not
consume the shared emission allowance. Large industrial secondary particles use
their world-space size to retain detail longer, within the unchanged outer limit.

Actual missiles, damage areas, monster AI, boss attacks, primary impact flashes,
explosion flame cores and rocket nozzle cores are not subject to this new
probability. Persistent corpse/gib policy, weather, mirror captures and material
shaders are outside this particle pass. Local density choices do not change
shared combat simulation.

Regression entrypoint: `tools/test_distance_fx.py --mod <package> --renderer 0`.
The fixture checks density anchors, monotonicity, continuity, outer fading, size
handling, actual near/far actor admission and client ownership for six families,
retention of existing smoke and impact cores, immediate shorter/longer/crossed
settings, opt-out, the menu reset and save/load recovery. Menu screenshots are
captured in all four languages. `tools/test_legacy_trail_budget.py` additionally
checks quality budgets, natural expiry and shared damaging projectiles with
cosmetic quality disabled. Local evidence lives in `.codex/validation/distance-fx.json`
and `distance-menu-*.png`. No additional FPS percentage is promised solely from
the density reduction; rendering cost depends on how much combat is distant.

Validation: 43 native distance assertions and all four menu captures passed on
UZDoom 5.0.3/OpenGL. The existing legacy-trail suite passed all 61 assertions;
14 localization unit tests, definition-table consistency and the four-font
689-file check passed. Menu labels and tooltips were visually reviewed at
960x540 in all four languages.

A supplementary TNT04A bridge AB/BA check (two runs per version, same OpenGL
setup as above) compared the previous capped-trail implementation with this
distance pass. Mean per-run medians were 44.14 / 41.14 ms and p95 values
61.89 / 59.24 ms; local actors averaged 3262 / 2788. All four runs
retained 625 shared actors and 85 kills. The small timing difference is not
strong evidence of an additional general FPS gain; the actor reduction is clear.
Results: `.codex/validation/distance-fx-bridge.json`.
