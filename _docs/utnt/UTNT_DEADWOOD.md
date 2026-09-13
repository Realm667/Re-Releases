# Deadwood decorations

The approved weathered, charred and frozen families replace the appearance of
existing BigTree, TorchTree, IceyTree and IceyStub objects. Each family contains
three trees and three stumps (18 original designs). Native Doom patches follow
the active PLAYPAL and match the original sprite pixel density. Original actors, map positions,
angles, authored scale, collision dimensions, projectile pass heights, TIDs and
script references remain intact. No campaign WAD is rewritten.

## Mapping

| Existing decoration | New appearance |
| --- | --- |
| BigTree (54) | Three full-size tree silhouettes |
| TorchTree (43) | Three compact broken/hollow stump silhouettes |
| IceyTree (20002) | Three frozen trees, including outside the winter maps |
| IceyStub (20001) | Three frozen stumps at the original smaller visual scale |

Ordinary Doom decorations use weathered wood in TNT01 and TNT02, frozen wood in
TNT03A1/TNT03A2, and charred wood in TNT03B, TNT04A/B/C/CN, TNTLE and ENDMAP01.
Explicit IceyTree/IceyStub placements always remain frozen: TNT02 includes seven.
Other maps default to weathered wood.

The current source inventory contains 508 placements:

| Map | BigTree | TorchTree | IceyTree | IceyStub |
| --- | ---: | ---: | ---: | ---: |
| TNT01 | 33 | 20 | 0 | 0 |
| TNT02 | 22 | 29 | 2 | 5 |
| TNT03A1 | 0 | 0 | 12 | 24 |
| TNT03A2 | 2 | 1 | 5 | 6 |
| TNT03B | 4 | 5 | 0 | 0 |
| TNT04A | 4 | 5 | 0 | 0 |
| TNT04B | 39 | 34 | 0 | 0 |
| TNT04C | 19 | 29 | 0 | 0 |
| TNT04CN | 50 | 55 | 0 | 0 |
| TNTLE | 45 | 35 | 0 | 0 |
| ENDMAP01 | 14 | 9 | 0 | 0 |

## Runtime and compatibility

[UTNT_Deadwood.zc](../../tutnt/zscript/UTNT_Deadwood.zc) assigns a sprite and
frame to the original actor after spawning completes. A position/angle hash
selects one of three silhouettes without consuming gameplay randomness. Only
the four exact classes and their original idle sprites are eligible; unrelated
subclasses and script-selected alternate sprites are untouched.

Choices serialize with each actor. Existing converted sprites are not assigned
again after save/load, even if a script moved them. The load hook also queues surviving original sprites for conversion. Newly spawned originals
are queued for the next tick. There is no recurring full-map scan and no extra
decoration actor or thinker per placement.

BigTree and IceyTree visual heights remain 124 and 127 units respectively;
TorchTree stump art is 40 units tall and IceyStub art 33 units tall, before any
map-authored scaling. The original simplified collision cylinders are retained,
including the taller TorchTree cylinder, to preserve traversal and projectile
behavior. Root anchors follow each trunk rather than the center of its widest
branches. The existing TNT04C sky-room light override still recognizes the
original actor classes and follows their transferred floor lighting.

The charred stump's tiny ember fissure is painted into its surface, without a
new dynamic light, fullbright tree, particle system or gameplay effect.

## Artwork and rebuilding

Approved concepts: local `tutnt/.codex/work/tree-stump-mockups/`.
The original-faithful atlas extraction and explicit key-background correction
used built-in Imagegen. [Prompts](../../tools/artwork/deadwood/prompts.json),
[keyed artwork and layout](../../tools/artwork/deadwood/atlas-layout.json) are
versioned under `tools/artwork/deadwood/`.

[build_deadwood_sprites.py](../../tools/build_deadwood_sprites.py) converts the
explicit chroma key to real alpha, separates the six atlas subjects without
cutting neighboring branches, and emits 18 native Doom patches plus 24 TEXTURES views.
The extra six views retain the original Icey actor visual scales; they are not
additional artwork. The compiler reduces trees to the original 124/127-pixel grid and stumps to
40 pixels, without dithering or a high-resolution override. It uses the original
TRE1/TRE2 and ICT1/ICS1 palette ramps with restrained olive moss and grey
extensions, and matches their matte brightness.
[Palette profiles](../../tools/artwork/deadwood/palette-profiles.json) record
these ramps and exposure adjustments. The authoring palette is stored as
quantization.pal; runtime patches contain indices, so later active PLAYPAL changes
apply automatically. The global PLAYPAL itself is not modified.
Every generated patch is decoded again to verify exact indices, transparent gaps
and offsets. The compiler performs format conversion, palette matching and
anchoring, not creative image generation. Generated sprite geometry is recorded in
[generated.json](../../tools/artwork/deadwood/generated.json).

```text
python -B tools/build_deadwood_sprites.py
python -B tools/build_deadwood_sprites.py --check
python -B tools/build_definition_tables.py --check
python -B tools/build_utnt.py --engine F:/DoomDev/uzdoom.exe
```

## Validation

[test_deadwood.py](../../tools/test_deadwood.py) checks current campaign maps,
original actor classes/collision/scale/TIDs, all three frames, explicit frozen
props, idempotence, and the TNT04C sky-room light override. `--restore` adds
save/load and dynamic-spawn checks, including an unrelated BigTree subclass.
The separate DWLAB fixture displays all 18 designs for visual inspection.
Test maps and handlers do not ship in the game.

```text
python -B tools/test_deadwood.py --maps TNT01 TNT02 TNT03A1 TNT04C --restore
python -B tools/test_deadwood.py
python -B tools/test_deadwood.py --maps DWLAB --renderer 0
```

Validated on 13 September 2026: all 508 source placements across the 11 affected
maps, with 87 successful runtime assertions across the final/native runs. Save/load
and dynamic-spawn checks passed on TNT01, TNT02, TNT03A1 and TNT04C; all 18
designs were inspected in the engine gallery. The 13 current source WADs retained
their before-task SHA-256 hashes and were byte-identical in the integration package.
One final Vulkan start on TNT02 timed out before the test commands; its OpenGL
rerun passed. TNT01 passed on the final package under Vulkan; remaining final
save/load cases passed under OpenGL. This is not a full campaign playthrough.

Local evidence belongs under `tutnt/.codex/validation/deadwood/`; working
baselines and source-map SHA-256 checks are in
`tutnt/.codex/work/deadwood-integration/`. The integration uses the live map
files, not historical snapshots or editor backup files.
