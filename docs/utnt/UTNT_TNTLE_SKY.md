# TNTLE: Basalt cavern and ember night

The two main TNTLE skies now follow the approved cavern/ember-night mockups.
The cavern has an irregular closed vault, basalt arches, deep warm haze and
long lava falls. The night sky has stationary jagged mountains, two slowly
moving dark cloud layers and sparse rising embers. Existing gameplay geometry,
SkyPicker assignments and the separate grey sky in the secret area remain.

## Animation and rendering

Lava uses a stationary material mask with two downward-moving flow patterns;
rock silhouettes and ledges never scroll. Smooth warm haze has a subtle rising
density variation. Mountains use a premultiplied matte in front of the clouds.
The sky materials share a serialized map-local clock (35 Hz, interpolated on
render, 2000-second repeat); it stops with frozen game time and survives saves.
Reduced FX / effect quality 1 removes haze variation and embers while retaining
the essential waterfall and cloud animation.

Two isolated six-surface sky rooms use world-position projection. This avoids
cube-edge UV disagreement and blends into closed planar zenith projections.
The artwork represents distant scenery; it does not add geometric parallax or
physical smoke volumes. The target is UZDoom 5.0.1 hardware rendering, tested
on OpenGL and Vulkan. Static projected textures provide the non-shader artwork;
the full animation requires custom material shaders.

## Scope and map preservation

- Original map SHA-256: `01d67636244bf7305186bffe87ee20b50d80142ee79aea6ef30abeb5b8288ac0`.
- The untagged SkyViewpoint moves to (-24576,24576,0); TID 13 to (-20480,24576,0).
- TID 31 stays at (11712,-5824,64), and all three viewpoints and all pickers remain.
- Exactly 8 vertices, 8 lines, 8 sides and 2 sectors are appended. All 2,411
  things remain; only the two main cameras change position/relative height.
- Every original vertex, line, side and sector block remains byte-identical.
  ACS script 14, the retired room's periodic light show, becomes a no-op. Other
  scripts are unchanged. ACS and compressed nodes are rebuilt.
- `areaalign/TNTLE.txt` changes only its topology header; all 7,597 existing
  bindings remain. Runtime must report `AREAALIGN|TNTLE|7597|0|7597`.
- Private ULC*/ULN* materials and ULEDATA canvas avoid shared sky/lava changes.

## Reproduction and checks

Run commands from the repository root, with Python 3.11+, Pillow and NumPy:

```
python tools/build_tntle_sky.py
python tools/test_tntle_structure.py <original-tntle.wad> tutnt/maps/tntle.wad --acc <acc.exe>
python tools/build_utnt.py --engine <uzdoom.exe> --iwad <DOOM2.WAD> --acc <acc.exe>
python tools/test_tntle_sky.py --engine <uzdoom.exe> --iwad <DOOM2.WAD> --mod tutnt.pk3 --work <test-directory> --renderer 1
python tools/check_tntle_motion.py <test-directory>/logs --renderer 1
```

Repeat the runtime/motion checks with renderer 0 for OpenGL. The fixture uses
isolated settings, saves and fixed cameras and does not ship inside the game.
It checks sky-room layout, the secret camera, time freeze and save restoration,
and captures eighteen views plus equal-interval animation samples. Motion
measurement compares downward translation with stationary/upward controls and
checks a dark rock region separately. It is not a performance benchmark.

`patch_tntle_sky.py` rebuilds the map from the original WAD with `--acc` and
`--zdbsp`; optional `--area-table` updates only the old topology header. It
deliberately refuses an already patched map. Generated art, actual prompts and
approved mockups are documented in `tools/artwork/tntle-sky/`.

Validation evidence: `tools/validation/tntle-sky-2026-09-09/`. Structural checks
and runtime tests do not constitute a full campaign playthrough. Existing saves
from before the map geometry change are not migration-tested; start TNTLE fresh
to see the new sky rooms.
