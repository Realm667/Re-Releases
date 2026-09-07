# FireSpawner torch-style adaptation

FireSpawner (DoomEdNum 32700) now uses the shared organic fragments, four smoke
shapes, gold embers and central glow. Its three original scales 0.35/0.70/1.40
retain their 1:2:4 relationship. The floor profile uses a broad footprint and a
shorter upward shape, calibrated against the original spawners in the included
before/after screenshots. It emits at the source position, with no torch body.

Only visual births in the original DECORATE state machine are replaced. The
native SwitchableDecoration parent, radius 30, height 40, original flags, map
ID, size/sound arguments, all labels, relative jumps and durations, start/loop/
stop sound actions, and Small/Medium/LargeFlame light helpers are preserved.
A zero-tic inactive notification stops the local emitter and glow; existing
particles finish their finite lifetimes. A static normalized comparison proves
the rest of the original state block is unchanged. Other uses of the legacy
Flame/Ember classes and monster BruiserFireSpawner are untouched.

The complete current checkout builds with all 14 ACS modules and an engine
package load check. Both OpenGL and Vulkan pass 48 FireSpawner assertions each:
size ratio and defaults, ownership, no old flame actors, deactivate/reactivate,
quality 0/1/2/3, reduced effects, distance culling, sound-option transition,
source removal and save/load. The shared torch/barrel suite passes a further
60 assertions per backend plus actual orange/green/blue ember-color probes.
Total: 216 passing runtime assertions, with rendered color/motion checks.

Sound actions were preserved and the option transition was exercised, but the
automated engine harness runs without audio output; no listening test or
multiplayer session was performed. Source and package hashes are in manifest.
Run with UTNT_ENGINE and UTNT_IWAD configured:

    python tools/test_firespawners.py --mod path/to/tutnt.pk3
