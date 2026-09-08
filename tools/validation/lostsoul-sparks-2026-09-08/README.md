# Lost Soul sparks

Lost Souls continuously shed the same orange UTNTFireDetail embers used by
torches and FireSpawner. Sparks originate around the flame crown, retain 12%
of flight velocity, rise, shrink and expire after 28–46 tics. Default emission
is once per four tics; quality, reduced effects, distance and the ambient
budget can reduce or disable it. Death stops new emissions. Existing AI states,
timings and attacks are unchanged. Terror's separate sprites are excluded.

The shared ember initialization was extracted without changing torch/fire
parameters. No new textures, gameplay actors or map edits are required.

Validation: UZDoom 5.0.1 full package build and all 14 ACS modules checked.
OpenGL and Vulkan each passed nine runtime checks: idle, chase, skull charge,
save/load, FX disabled, reduced FX, distance culling, re-enabling and death.
Checks inspect actual live particles, material, lifetime and Terror exclusion.
Idle and charge screenshots were visually inspected. The test player uses
CF_NOTARGET for a stable idle phase; chase/attack are entered explicitly.
This is a focused effect regression, not a full campaign or multiplayer test.

Run: `python tools/test_lostsouls.py --mod tutnt.pk3` with UTNT_ENGINE and
UTNT_IWAD configured. The package includes the current local project snapshot;
the commit is restricted to the Lost Soul change and these tests/evidence.
