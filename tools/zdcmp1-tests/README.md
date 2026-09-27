# ZDCMP1 effect regression checks

Target engine: UZDoom 5.0.1 or newer. The tests use an isolated generated room,
the existing `check_engine.run_case` helper, separate configuration files, and
temporary savegames under `logs/`. They do not change a normal game configuration.

```sh
python3 tools/test_zdcmp1_effects.py --engine /path/to/uzdoom --iwad /path/to/doom2.wad --renderer 0
python3 tools/test_zdcmp1_effects.py --engine /path/to/uzdoom --iwad /path/to/doom2.wad --renderer 1
```

Renderer 0 selects OpenGL; renderer 1 selects Vulkan. Freedoom 2 is sufficient
for code assertions. Use the intended Doom II IWAD for visual acceptance.
Success requires 34 passing assertions, a completion marker, and no detected
script/VM errors. A process exit code alone is not a passing regression test.

Validated on 2026-09-27 with the official UZDoom 5.0.1 macOS ARM64 release
and Freedoom 2 0.13.0: all 34 assertions passed on both OpenGL and Vulkan.
MAP01 startup and save/load passed on both backends. The packaged PK3 also
passed the Vulkan MAP01 check, and the Max/default effects menu was inspected
in a rendered screenshot. ACS was rebuilt with ACC 1.60.

Coverage includes the default Max profile; silent fire lights and cleanup;
multiple departing and invalid ladder occupants; weather floor filtering;
gore limits, profile changes, zero and negative limits; smoke distance and
effect switches, including emitters created while disabled; heat activator
cleanup; save/load; invalid motion-blur sample values; local blur state; and
absence of motion-blur network events.

## Quality and compatibility

`ZDCMP1_fxquality` defaults to 2 (Max). Max preserves the original six weather
spawn attempts per effect and player per tick, full smoke emission, the user's
full `nashgore_maxgore` budget, and the configured motion-blur sample count.
Balanced uses four weather attempts, half-rate smoke, half the gore budget,
and at most four blur samples. Low uses two attempts, one-third-rate smoke,
one-quarter of the gore budget, and at most two blur samples. Profile changes
do not overwrite the user's individual effect switches or gore settings.

Motion blur remains enabled by default. Heartbeat and injury overlay default
to enabled, and underwater distortion retains its original default strength.
Both simple and advanced options menus link to the same effects submenu.

Gore cleanup is deferred until the next handler tick and includes all actors
in the dedicated gore stat list, including wall blood. Temporary within-tick
bursts can exceed the configured budget. Smoke uses its existing 1200-unit
range and checks range at staggered intervals of at most eight ticks.
Weather prefiltering falls back to the original actor checks in sectors with
3D floors, height transfers, or floor portals, and in linked portal maps.

Recompile `zdcmp1/source/zdcmp1.acs` with ACC when changing the comfort options;
the tracked `zdcmp1/acs/zdcmp1.o` must match its source. Keep this test directory
outside the shipped mod. The existing Windows build already excludes PSD art.

## Extended release checks

The following tools accept `--engine`, `--iwad`, `--mod` and `--renderer`, or
the same `UTNT_ENGINE` / `UTNT_IWAD` environment variables as the original test.

```sh
python3 -B -m unittest discover -s tools -p test_zdcmp1_integrity.py -v
python3 -B tools/build_zdcmp1.py --acc /path/to/acc
python3 -B tools/test_zdcmp1_effects.py --mod zdcmp1.pk3
python3 -B tools/test_zdcmp1_edges.py --mod zdcmp1.pk3
python3 -B tools/test_zdcmp1_coop.py --mod zdcmp1.pk3 --renderer 0
python3 -B tools/test_zdcmp1_map.py --mod zdcmp1.pk3
python3 -B tools/test_zdcmp1_remaster.py --mod zdcmp1.pk3
python3 -B tools/test_zdcmp1_logbook.py --mod zdcmp1.pk3 --visual-matrix
python3 -B tools/test_zdcmp1_weapons.py --mod zdcmp1.pk3 --compare /path/to/baseline.pk3
python3 -B tools/audit_zdcmp1.py
```

The build verifies both tracked ACS libraries and MAP01 ACS byte-for-byte with ACC 1.60 and
creates a deterministic PK3. Editor backups, source artwork, test tools and
local working data are excluded. A stale ACS file fails the build; the build
does not silently change tracked binaries.

The edge suite has 34 assertions across real 3D floors, transferred heights,
ordinary floor portals, linked portal groups, missing/alternate cameras and
save/load. Particle acceptance is checked after actor initialization, not
immediately after `Spawn`.

The cooperative suite starts two actual local peers with separate configuration
files and opposing motion-blur settings. Sixteen assertions per peer cover entry,
Max server quality, death, respawn, gore inventory, camera switching and local
blur state, journal ownership/respawn, private notifications, sender-owned read
acknowledgments and non-host finale-skip rejection.
It compares final state between peers and only terminates its own
processes. It is a lifecycle test, not a campaign-wide desynchronization proof.

The map suite starts MAP01 on all five skills, checks Max defaults and a living
player, and verifies save/load and absence of the known terrain/line warnings.
It records monster/item/secret counts and screenshots. This is not a full-map
playthrough or a measurement of combat balance.

The remaster suite checks actual MAP01 script-delivered hints, camera previews
across save/load, HUD restoration, finale save/load, disabled/enabled skipping,
normal exit cleanup and menu opening. Add `--full-finale` for a roughly five-minute
natural credits run as well. The weapons suite uses real sustained primary and
alternate fire, compares ammo and object peaks at both comfort extremes and
requires projectile/effect cleanup. Its optional `--compare` also checks six
deterministic movement/camera samples against a previous package.

The field-terminal suite requires 32 assertions for notification ordering,
deduplication, expiry, menu pause, keyboard/controller/mouse navigation,
unread-state save/load, five-row scrolling, both localizations at large text,
HUD-corner avoidance, and disabled-state history preservation. Its optional
`--visual-matrix` adds nine assertions and real 1280x720, 960x720 and 1680x720
screenshots. The engine must actually reach each requested resolution; fitting
a frame into an unchanged resolution is not a passing viewport test. Window
size changes and macOS HiDPI changes affect only the isolated test configuration.

GitHub Actions runs the release checks on relevant pushes and pull requests.
It uses checksum-pinned UZDoom 5.0.1 and Freedoom 2 0.13.0, pinned ACC 1.60
source, and software OpenGL/Vulkan. CI timing must not be used as GPU performance
evidence. Logs are retained for seven days.

## Performance and soak runs

```sh
python3 -B tools/test_zdcmp1_stress.py --scene mixed --seconds 15 --repeats 2 --compare /path/to/baseline.pk3
python3 -B tools/test_zdcmp1_stress.py --scene mixed --soak --seconds 1800 --repeats 1 --label zdc-soak-30min
```

Run benchmarks without other engine processes. Available fixed-seed scenes are
`weather`, `smoke`, `fire`, `gore` and `mixed`. Weather uses this mod's lava
particles, not an invented rain implementation. Profiles stay on Max, with a
1024 gore budget. Frame intervals are measured after a five-second warmup and
reported as median, p95, p99 and maximum. Engine thinker profiling runs only
after the frame sample window. Baseline comparisons alternate AB/BA order.
Frame intervals include presentation/compositor pacing; they are not pure GPU
times. Requested benchmark resolution is 1280x720 without HiDPI, and the engine's
reported resolution is included in results.

The real-time soak performs ten save/load cycles, checks effect counts before
and after each load, then destroys emitters, clears gore, disables weather and
waits for particles to expire. Success requires all 21 assertions, completion
markers and at least the requested wall-clock duration. A 64-item within-tick
gore burst is allowed because trimming occurs on the next handler tick. The
final cleanup must leave no tracked lights, smoke, gore or weather particles.

Resident memory is sampled every 30 seconds on macOS/Linux. First/second-half
medians after warmup help identify sustained growth, but RSS includes allocator
caches and excludes much GPU memory. Stable RSS alone is not proof of no leaks.
Results and raw logs are written under `logs/`, the compatibility path to
`tutnt/.codex/logs`. Full Doom II playthroughs and visual balance remain separate
acceptance tasks; Freedoom does not substitute for the intended artwork/IWAD.
