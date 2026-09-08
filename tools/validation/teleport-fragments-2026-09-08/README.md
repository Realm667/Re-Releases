# Teleport fragment validation, 2026-09-08

UZDoom 5.0.1 completed the final Vulkan six-color fixture and OpenGL TNT01 run
without script/VM errors. Runtime checks resolve all six atlas texture names;
the fixture also confirms spawner creation and the selected disabled quality.
Screenshots were visually inspected: all six colors render, red fragments and
short trails match the approved direction, and particles disappear after
deactivation or FX quality 0. Reactivation, low quality and Reduced FX were
captured. The actual TNT01 teleporter screenshot shows the effect in the map.
This is a focused VFX check, not a campaign, network or performance benchmark.
TNT01's first two camera targets cross teleport geometry; only the final useful
teleporter view is included. The test fixture contains no production game code.

Reproduce via tools/check_engine.py with --addon tools/teleport-tests,
--map UTNTPART --exec tools/teleport-tests/all-colors.cfg (Vulkan), or
--map TNT01 --exec tools/teleport-tests/real-map.cfg --renderer 0 (OpenGL),
--set UTNT_fxquality=3 and --timeout 50, supplying engine and IWAD paths.

The active PK3 was rebuilt concurrently by another workflow and already
contained the final effect. Every owned package entry was checked against the
tested source bytes; unrelated package content was retained. Exact hashes and
final run assertion counts are in results.json.
