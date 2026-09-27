# ZDCMP1 validation, 2026-09-27

## Scope

Baseline: `1b3c03b62e4f1598e8a2f1b50daf782d49cbc5c0` (the first Max-default
optimization release). Production changes in this follow-up are deliberately
limited to two warning fixes:

- Define the existing solid-terrain placeholder explicitly. Default footstep
  fallback and non-liquid behavior remain unchanged.
- Remove the unused `arg1` from MAP01 linedef 23532's `Thing_Activate` action.
  Its actual argument, activation flags and geometry are unchanged. The other
  WAD lumps, including compiled ACS, source ACS and nodes, are byte-identical.

Max remains the default. No enemies, pickups, progression scripts, textures,
sounds, shader strengths or effect densities have been reduced or rebalanced.

## Local functional evidence

Official UZDoom 5.0.1, Apple M3, macOS 26.7, Freedoom 2 0.13.0:

- Original effect suite: 34 assertions passed on each of OpenGL and Vulkan.
- Real 3D-floor, height-transfer, floor-portal and linked-portal fixtures:
  34 assertions passed on each backend, including save/load and camera changes.
- MAP01: startup and save/load passed on all five skills on both backends;
  30 assertions per backend, no remaining known terrain/line warnings.
- Two actual local peers on each backend: nine assertions per peer passed, with matching
  final state, death/respawn, gore inventory, camera changes and opposite local
  motion-blur settings.
- Earlier native macOS Vulkan coop attempts timed out while the endurance run
  was also active. The isolated rerun passed with identical final peer states:
  `time=350 respawns=1 health0=100 health1=100 quality=2`. The timeout cause is
  not established; concurrent-load reliability remains unverified.
- Six engine-independent integrity tests passed. ACC 1.60 reproduced both
  tracked ACS libraries byte-for-byte. Deterministic package tests passed.

The complete [Linux CI run for 465301e](https://github.com/Realm667/Re-Releases/actions/runs/36319793108)
passed on both software OpenGL and Vulkan, including the two-peer cooperative
suite and the short save/load stress test. The first CI attempts
identified an AppImage resource-path issue and insufficient settling time in
the existing quality-switch test. Engine resources are now placed next to the
resolved executable; strict gore assertions wait 35 instead of five ticks and
log requested/applied state. No assertion was removed or relaxed.

The intended Doom II IWAD was not available in the checked game/work locations.
Freedoom verifies code paths, not the intended Doom II artwork or combat feel.

## Thirty-minute endurance run

The Max-quality mixed scene ran for **1842.6 seconds** with ten real save/load
cycles. All **21 assertions** passed. The effect implementation is unchanged
from the baseline during this follow-up.

Observed checkpoint maxima:

| Object | Maximum | After final cleanup |
| --- | ---: | ---: |
| Fire lights | 8 | 0 |
| Smoke particles | 368 | 0 |
| Gore actors | 1088 | 0 |
| Weather particles | 678 | 0 |

The gore limit is 1024. A newly spawned 64-object burst can be observed before
the next handler tick trims it; this is the documented deferred-cleanup behavior.

Resident memory was sampled every 30 seconds. After the first three minutes,
first-half median RSS was **102.35 MiB**, second-half median **151.63 MiB**,
and the peak **183.80 MiB**. RSS fluctuated rather than growing monotonically;
the higher second-half median must not be presented as proof of constant memory.
Other functional engine tests ran during parts of this soak. macOS residency,
compression and allocator caches confound comparisons. Object counts remained
bounded and final tracked-object cleanup succeeded; this is not a comprehensive
CPU/GPU memory-leak certification.

Raw evidence: `logs/zdc-soak-30min-mixed-1-0-after/result.json` and `engine.log`.
The `logs` compatibility path points to ignored `tutnt/.codex/logs`.

## Performance protocol

The benchmark compares the immutable baseline PK3 with the new PK3 after the
soak finishes, with no other engine tests running locally. It uses seed 667,
Max, a 1024 gore budget, five seconds of workload warmup and ten seconds of
frame samples. Two repetitions alternate baseline/current and current/baseline.

Vulkan covers weather, smoke, fire, gore and the mixed scene. OpenGL covers the
mixed scene. Weather means the mod's lava particles, not a new rain effect.
The effective macOS framebuffer is 1152x745; both sides use the same size.
Presentation/compositor pacing is included. These short synthetic scenes do
not predict full-campaign FPS, and no speedup is promised from warning fixes.
Native thinker profiling on this ARM64 build reported `0.000000 ms` for all
classes. Those tables provide object counts, not a usable CPU-cost ranking;
zero must not be interpreted as free execution. No additional production
optimization was justified from those timing tables.

All 24 runs passed, with identical checkpoint object counts between baseline
and current builds and zero tracked objects after cleanup. Results are recorded
under `logs/zdc-benchmark-*-results.json`.

The following milliseconds are arithmetic means of the two per-run medians or
95th percentiles, not percentiles pooled across runs. Lower is better.

| Backend / scene | Baseline median | Current median | Baseline p95 | Current p95 |
| --- | ---: | ---: | ---: | ---: |
| Vulkan / weather | 8.166 | 8.222 | 12.837 | 12.666 |
| Vulkan / smoke | 8.205 | 8.145 | 10.957 | 11.073 |
| Vulkan / fire | 7.901 | 7.942 | 12.580 | 12.586 |
| Vulkan / gore | 7.768 | 8.084 | 12.596 | 12.040 |
| Vulkan / mixed | 8.134 | 8.127 | 10.320 | 10.106 |
| OpenGL / mixed | 10.679 | 10.648 | 12.898 | 12.726 |

The small, mixed changes and two repetitions do not establish a performance
gain or a regression. The tested production changes remove warnings, not
effect work. These results also do not measure the earlier optimization's
benefit over the original mod: the baseline already contains that optimization.

Validated current package SHA-256:
`658d47c73889c823be388dcb9549a374dd20b5156e0dd995bbb7860855e00fdd`.

## Gameplay inventory and remaining acceptance

MAP01 contains 5481 placed things, 25844 vertices, 31350 linedefs and 5131
sectors. Runtime monster counts are 384 on skills 1/2, 528 on skill 3, and 667
on skills 4/5. All skills have ten secrets. These counts were unchanged by
save/load. The static audit records keys, locks, player starts, weapon/ammo/
health placements and progression scripts without claiming route reachability.

No full, unaided Doom II playthrough has been completed. Route readability,
backtracking, ammunition sufficiency, boss pacing, final exit progression and
campaign-wide cooperative desynchronization remain unverified. Teleporting to
an exit or starting every skill would not satisfy that acceptance criterion.
No speculative gameplay edits were made to disguise this gap.

## Reproduction

See [test instructions](../../tools/zdcmp1-tests/README.md). The GitHub workflow
checks a built PK3 with pinned UZDoom/Freedoom/ACC dependencies and preserves
its own logs. Software-rendered CI is functional evidence, not hardware
performance evidence.
