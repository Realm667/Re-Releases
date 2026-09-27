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

Full-map playthroughs, Doom II visual balance, linked-portal/3D-floor fixtures,
and network multiplayer remain separate acceptance tasks. These regression
checks are not a frame-time benchmark. Existing `Unknown terrain ZDCMP1_`
warnings and MAP01 line 23532's unused argument predate these changes.
