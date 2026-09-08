# Portal activation and proximity suction — 2026-09-09

UZDoom 5.0.1; OpenGL and Vulkan. Both decoration sizes are explicitly dormant
at spawn in PORTEST. Native SwitchableDecoration.Activate only changes the
state label; it does not clear bDormant. The previous lifecycle fixture used
initially active decorations and therefore missed this regression.

The portal base now maintains Dormant and PortalActive during activation and
deactivation, and respects dormant starts. Visible hot cores, wider launch
positions and tighter destinations make the accelerating inward particles
legible in actual campaign views. Particle budgets/lifetimes are unchanged.

| Runtime check | Passing assertions |
| --- | ---: |
| Dormant 128/192, emission, proximity, settings, save/load — OpenGL | 202 |
| Same — Vulkan | 202 |
| Solid occluder blocks suction — OpenGL / Vulkan | 4 / 4 |
| Original ACS 176 via ExecuteSpecial, TNT03B / TNT04A / TNT04B | 50 / 50 / 44 |
| Automatic sources, FX quality and save/load in TNT04CN | 14 |
| Final packaged TNT03B particle and shader run | 40 |

SuctionAmount is the value actually submitted by the render handler. At tested
128/96/64/24-unit front distances it is 0 / 0.1563 / 0.5 / 0.9077. The view
tests also verify off-screen/back/side positions, source deactivation, quality
0, reduced effects and the overlay switch. Active and inactive saves are
restored; automatic sources are checked separately after load.

LineTracer's default all-flags wall mask incorrectly treats ordinary two-sided
trigger lines as walls. A zero flag mask preserves geometric wall/sector
occlusion while passing those invisible boundaries. Both the blocked test map
and the three campaign maps exercise this distinction. The initial 30-second
OpenGL occlusion startup timed out; the final retry passed, and the committed
runner allows 75 seconds for that case.

All final logs reached their completion marker with no assertion, script, VM
or shader compilation failures. Total 610 logged passing assertions, including
repeated checks of individual live particles. The screenshots come from the
final full package, with a held local camera facing the actual TNT03B portal.
They are evidence of the running renderer, not generated mockups.

The full build compiled the common library and all 14 map scripts, then passed
the engine load check. Build c7ea59c099c4, package SHA-256:
76a9bab304c7a60181408fd5d771a6b841c9749dbb11614fc3ac5af9070d2c17.
Its four portal runtime files matched the tested sources byte-for-byte.
The build includes the current full worktree; only portal-owned changes are
part of this commit. Runtime file hashes are recorded alongside the results.

Reproduce with tools/test_portal_suction.py --mod tutnt.pk3 --campaign,
supplying --engine and --iwad when they are not configured in the environment.
No full campaign playthrough, migration test of saves made by older releases,
new cooperative session or general FPS benchmark is claimed by this check.
