# Deadwood decorations

The selected Style C weathered, K4 charred and F2 frozen sprite families replace the appearance of
existing BigTree, TorchTree, Stalagtite, IceyTree and IceyStub objects. Each family contains
three trees and three stumps (18 original designs). Native low-resolution Doom
patches use the active PLAYPAL through 24 sprite views, including the original
frozen size variants.
Original actors, map positions,
angles, authored scale, collision dimensions, projectile pass heights, TIDs and
script references remain intact. No campaign WAD is rewritten.

## Mapping

| Existing decoration | New appearance |
| --- | --- |
| BigTree (54) | Three full-size tree silhouettes |
| TorchTree (43) | Three compact broken/hollow stump silhouettes |
| Stalagtite (47) | Three compact stump silhouettes; includes the reported TNT02 stump |
| IceyTree (20002) | Three frozen trees, including outside the winter maps |
| IceyStub (20001) | Three frozen stumps at the original smaller visual scale |

Ordinary Doom decorations use weathered wood in TNT01, frozen wood in
TNT03A1 and explicitly icy props in TNT03A2, and charred wood in TNT02, TNT03B, TNT04A/B/C/CN, TNTLE and ENDMAP01.
Explicit IceyTree/IceyStub placements always remain frozen: TNT02 includes seven.
Other maps default to weathered wood.

The current source inventory contains 851 placements, including 343 type-47 stumps:

| Map | BigTree | TorchTree | IceyTree | IceyStub | Stalagtite |
| --- | ---: | ---: | ---: | ---: | ---: |
| TNT01 | 33 | 20 | 0 | 0 | 62 |
| TNT02 | 22 | 29 | 2 | 5 | 41 |
| TNT03A1 | 0 | 0 | 12 | 24 | 0 |
| TNT03A2 | 2 | 1 | 5 | 6 | 3 |
| TNT03B | 4 | 5 | 0 | 0 | 0 |
| TNT04A | 4 | 5 | 0 | 0 | 0 |
| TNT04B | 39 | 34 | 0 | 0 | 44 |
| TNT04C | 19 | 29 | 0 | 0 | 40 |
| TNT04CN | 50 | 55 | 0 | 0 | 88 |
| TNTLE | 45 | 35 | 0 | 0 | 47 |
| ENDMAP01 | 14 | 9 | 0 | 0 | 18 |

## Runtime and compatibility

[UTNT_Deadwood.zc](../../tutnt/zscript/UTNT_Deadwood.zc) assigns a sprite and
frame to the original actor after spawning completes. A position/angle hash
selects one of three silhouettes without consuming gameplay randomness. Only
the five exact classes and their original idle sprites are eligible; unrelated
subclasses and script-selected alternate sprites are untouched.

Choices serialize with each actor. Existing converted sprites are not assigned
again after save/load, even if a script moved them. TNT02 saves with the former
weathered sprites migrate to charred wood while retaining their variant frame. A transient flag triggers a single actor scan on the first tick after map entry
or save restoration; EventHandler.WorldLoaded is skipped for restored handlers.
This also converts surviving original sprites in old saves. Newly spawned originals
are queued for the next tick. There is no recurring full-map scan and no extra
decoration actor or thinker per placement.

BigTree and IceyTree visual heights remain 124 and 127 units respectively;
TorchTree and Stalagtite stump art is 40 units tall and IceyStub art 33 units tall, before any
map-authored scaling. The original simplified collision cylinders are retained,
including the taller TorchTree cylinder, to preserve traversal and projectile
behavior. Root anchors follow each trunk rather than the center of its widest
branches. The existing TNT04C sky-room light override still recognizes the
original actor classes and follows their transferred floor lighting.

Charred K4 uses dark carbonized bark with small exposed wood breaks. Frozen F2
uses neutral gray wood, thick snow masses and icicles. Neither family adds
emissive lighting or particles.

## Artwork and rebuilding

The user selected Style C for weathered wood and then K4/F2 for charred/frozen
wood on 14 September 2026. All families share the same six broken, weathered
silhouettes. The new winter family has gray bark, substantially more snow and
ice; its pixels use only neutral grayscale indices.

The three selected ImageGen atlases and their exact [prompts](../../tools/artwork/deadwood/prompts.json)
are versioned under `tools/artwork/deadwood/`. The approved low-resolution
selection previews were transferred directly into [indexed native source PNGs](../../tools/artwork/deadwood/native/),
without changing their pixel indices or transparent masks.
[Layout metadata](../../tools/artwork/deadwood/atlas-layout.json) records source
atlas bounds, selection identifiers, pixel hashes and explicit trunk anchors.
The crooked middle tree is anchored at its lower trunk, not at the midpoint
of its overhanging branches.

[build_deadwood_sprites.py](../../tools/build_deadwood_sprites.py) losslessly
compiles those 18 indexed grids into Doom patches and 24 TEXTURES views.
The extra six views retain the original Icey actor visual scales.
No build-time resampling, extra exposure reduction, dithering or high-resolution
override is applied; this preserves the appearance approved in the selection
boards. PNG index 255 is transparent, while opaque black remains visible.
The compiler validates source palettes, heights, transparency and allowed
[palette indices](../../tools/artwork/deadwood/palette-profiles.json), and decodes
every output patch to verify exact indices, masks and offsets.

The authoring palette in `quantization.pal` is the original Doom palette supplied
with the user's sprite references. It documents the index meanings; the runtime
patches contain only indices and use Remaster UTNT's active PLAYPAL. The global
PLAYPAL remains unchanged. [Generated geometry](../../tools/artwork/deadwood/generated.json)
records all runtime sizes and anchors.

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

Validated on 13 September 2026: the type-47 correction passed 85 assertions
across all eleven affected campaign maps (851 placements) using the final
runtime/patch overlay. TNT01 and TNT02 additionally passed save/load and
dynamic-spawn checks; TNT02 migrated a save seeded with legacy dry sprites and
original SMIT stumps. Test saves use unique filenames and verify the loaded map
identity to prevent accidental reuse of an older save. The corrected stump was
inspected at the reported location in the engine. The current source WADs match
the tested base package byte for byte and retain their before-task SHA-256 hashes.
The rebuilt integration package additionally passed the seven targeted TNT02
assertions without an overlay. All 13 current WADs and all 19 deadwood runtime
resources (handler plus 18 native patches) match their live sources byte for byte.
These correction tests used OpenGL and are not a full campaign playthrough.

Local evidence belongs under `tutnt/.codex/validation/deadwood/`; working
baselines and source-map SHA-256 checks are in
`tutnt/.codex/work/deadwood-integration/`. The integration uses the live map
files, not historical snapshots or editor backup files.

## Type-47 correction (13 September 2026)

The reported stump at TNT02 (2560, 32), Thing 14, uses Doom's Stalagtite
(type 47, SMITA0), which the first implementation omitted. All 41 TNT02
placements and the same exact class in other campaign maps now participate in
the existing cosmetic mapping. Their radius, height, projectile pass height,
position and class are retained. No map edit is needed.

The regression fixture inventories the five source classes independently of
the production mapper, so an omitted class fails rather than disappearing from
the test. It checks the reported coordinates, type-47 coverage, TNT02's charred
theme, unrelated subclasses, and restoration of saves seeded with old dry
sprites and original SMIT stumps. Local evidence and before/after screenshots
are under `tutnt/.codex/validation/deadwood-stub-fix/`.

## Sprite restoration (14 September 2026)

After evaluating the voxel conversion in the campaign, the user selected the
existing sprite artwork again. All 24 deadwood VOXELDEF bindings and KVX files
are removed, together with the dedicated voxel authoring grids and build tools.
The standard package build no longer generates deadwood models. The discarded
voxel experiment remains available in Git history through commit d36406314.

The existing 18 low-resolution indexed patches and 24 TEXTURES views are now
the active representation. Their palette indices, root anchors and visual sizes
are retained. The mapper, theme selection, collision and save migration continue
unchanged; converted actors in existing saves render as sprites automatically.
Other pickups and decorations retain their voxel models.

The rebuilt shared package passed the engine check and all 74 runtime assertions
in TNT01, TNT02, TNT03A1 and TNT04C, including save/load and legacy migration.
An engine gallery confirms all 18 sprite designs. Package verification finds
all 24 sprite views, no deadwood voxel bindings or model files, and byte-identical
remaining voxel models, native patches, maps, mapper and PLAYPAL. The sprite,
voxel and definition generators pass their stale-output checks. These are
targeted OpenGL checks, not a full campaign playthrough.

Local evidence: `tutnt/.codex/validation/deadwood-sprite-restore.json`; build logs
and ingame screenshots: `tutnt/.codex/logs/deadwood-sprite-restore/`.

## Selected Style C families (14 September 2026)

Integrated the user's final choices: C weathered, K4 deeply charred and F2 gray
winter wood with thicker snow and ice. All 18 native sprite masks and palette
indices match the approved selection previews exactly; only horizontal root
anchors were corrected. The 24 existing sprite identifiers and original
world heights remain compatible with the existing mapper and saved actors.

The rebuilt shared tutnt.pk3 passed its engine check and 56 runtime assertions
across TNT01, TNT02 and TNT03A1, including save/load, legacy-save migration,
dynamic spawns, original collision and actor scale. The DWLAB engine gallery
was visually checked for all three families. This is targeted OpenGL validation,
not a complete campaign playthrough.

Package verification confirms the 18 approved pixel grids, all 24 sprite views,
source-identical maps and mapper, unchanged active PLAYPAL and no deadwood voxel
bindings or KVX files. Both sprite and definition stale-output checks pass.
Local evidence: `tutnt/.codex/validation/deadwood-style-c-package.json` and
`tutnt/.codex/validation/deadwood-style-c-runtime.json`.
Ingame screenshots and engine logs: `tutnt/.codex/logs/deadwood-style-c/`.

The six ordinary trees/stumps in TNT03A2's dusty cave use dry wood; old winter substitutions are repaired on load. Explicit exterior IceyTree/IceyStub placements remain snowy.
