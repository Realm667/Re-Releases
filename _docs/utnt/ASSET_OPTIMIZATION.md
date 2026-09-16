# UTNT asset storage audit

Completed 16 September 2026. The audit covered every current UTNT game-source
file, embedded map lumps and ACS, engine definitions, ZScript/DECORATE, shaders,
and the repository tools/manifests that read or regenerate assets. Other mods,
Git history, local references and historical backups are outside this cleanup.

## Result

| Measurement | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Game-source files (build input inventory) | 31,270 | 30,555 | 715 |
| Game-source bytes | 628,238,816 | 611,187,686 | 17,051,130 (2.71%) |
| Engine-checked PK3 bytes | 372,959,148 | 366,546,135 | 6,413,013 (1.72%) |

These are snapshots of the shared checkout, including ongoing local integration.
An unrelated secondary-fire source grew by 174 bytes during the audit. Image and
model reductions below were independently checked against the original bytes.
The source inventory excludes local `.codex` artifacts; retaining Git history
and recovery packages means this is not a claim that the entire disk footprint
has shrunk by the same amount.

## Changes

- **369 duplicate legacy patches:** composite definitions now reference the
  byte-identical image under `textures/` by full path. Public composite names,
  dimensions, layer positions, transforms and palette behavior are preserved.
  Both authored and generated environmental composites were updated. Patches
  used as direct inputs by active tools/generators remain available.
- **Seven duplicate hires images:** native `Remap` directives share the Source
  illustration between INTERPIC and TNTE4_1 and share six monitor replacements.
  Existing names, display dimensions and offsets remain valid. The remaps live
  in `textures/definitions/TEXTURES.shared-assets` and use the existing TEXTURES
  entrypoint. No image is re-encoded or downsampled.
- **Two unused water atlases:** removed `water-atlas.png` and `water-atlas-v2.png`.
  All nine ambient-water patches use `water-atlas-v3.png`; tools and map scripts
  have no references to the earlier atlases.
- **338 duplicate generated models:** 202 terrain/sky-edge meshes and 136 lava
  meshes share a deterministic canonical file. Every actor retains its own
  class, skin, placement, render settings and frame binding. Generators and
  output inventories maintain this sharing on rebuild.
- **Lossless OBJ decimal compaction:** removes trailing decimal zero padding
  without rounding. All numeric values, including signed zero, remain exactly
  equal. Face indices, comments, smoothing and order stay unchanged.

Image cleanup removes 8,706,144 bytes. Models remove 8,348,109 bytes:
6,773,129 terrain/sky-edge bytes, 1,516,784 lava bytes and 58,196 cavern bytes.
Small additional reference/definition text accounts for the net source result.

## Why some apparent duplicates remain

The remaining 2,970,516 byte-duplicate bytes are candidates, not automatic
removal instructions. Most are patches still used by material/artwork tools,
public textures, sprite frames, independently addressed font glyphs,
material-generator output and music/sound copies in different namespaces.
Animation ranges, inherited sprite frames, IWAD replacements and generated
resource names cannot be proven unused by a missing literal text match.

In particular, `sprites/sfx/#remove/FLM*` is **active**: Flame actor subclasses
select the prefix and inherit the remaining animation through `####` states.
The credits and pickup UI also construct resource names dynamically. These
resources were retained. Maps contain no unindexed trailing WAD payload to
remove. No source maps, ACS, gameplay definitions, shader behavior, audio
quality or authored artwork were changed by this task.

## Validation

- Complete regular build: generators, localization/font validation, all ACS
  compilation, ZIP integrity and UZDoom load check passed.
- All **12,093 model actor bindings** compared with the pre-change package.
  Every model's numeric tokens were independently compared as binary64 values;
  indices and non-numeric lines were unchanged. Placement registries are equal.
- **458 affected composite/hires textures** rendered before and after under
  identical Vulkan settings: **zero changed pixels**, identical resource sizes,
  and 458 successful texture-lookup assertions on each run.
- All **369 removed patch copies** passed the original palette-conversion
  fixture's content hash, dimensions, offsets, column structure and packaged
  byte checks using their identical canonical images.
- 31 unit regressions passed (model storage, lava geometry, sky-edge geometry,
  definition layout); definition generation check passed.
- TNT03B terrain rendering and save/load: 11 assertions passed. TNTLE lava
  rendering and save/load: 238 assertions passed.

The full historical palette fixture already refers to six assets absent from
the original baseline (M_SKULL1/2, DROPA0 and QRUNT61/62/63); that pre-existing
fixture issue was not suppressed. The scoped original 369 asset records all
pass. The work-layout checker reports 15 pre-existing editor `.dbs`, backup and
autosave files under `tutnt/maps`; none was created, moved or removed here.
Their timestamps and paths are recorded in the local audit evidence.

## Source tree and package comparison

The engine-checked common `tutnt.pk3` already contains every validated change:
11,758 changed runtime resources match the tested candidate and all 716 removed
resources remain absent. Final verification did not rerun asset generators or
overwrite manual edits. Other tasks continue to update unrelated weapon/voxel
sources; the common package is not claimed to match every later live edit. All
compact/shared production models and images are present under `tutnt/`.
`.codex` is not needed at runtime or shipped.

There are **pre-existing packaging exceptions**, unchanged by this audit:
TEXTURES source modules are expanded into the root table; native model precache
lists are appended to MAPINFO; the cavern skyroom specification transforms
TNT03A2 only inside the package; authoring-source folders are omitted, and build metadata plus
its language label are added. Consequently a plain ZIP of the source directory
is not yet equivalent to the regular production build. Resolving the existing
cavern map transformation belongs to the source-tree integration work, not this
storage cleanup. The exact comparison is recorded locally in
`.codex/validation/size-audit-package-source.json`.

### Subsequent cavern source integration (16 September 2026)

The cavern exception above was subsequently resolved: TNT03A2 now contains the
final rooms, scenery Things and authored lighting in its source WAD, and the
packager no longer patches it. Direct source-ZIP lifecycle tests passed. The
TEXTURES expansion, precache and build-label distinctions remain; see
[production sources](PRODUCTION_SOURCES.md) and [cavern authoring](UTNT_CAVERN.md).

## Repeat checks

```text
python -B tools/audit_utnt_assets.py --check
python -B tools/audit_utnt_assets.py --report tutnt/.codex/validation/asset-inventory.json
python -B tools/test_model_assets.py
python -B tools/test_asset_consolidation.py --before <baseline.pk3> --after <candidate.pk3> --engine <uzdoom.exe>
python -B tools/build_definition_tables.py --check
```

`tools/asset-consolidation.json` records original names, canonical paths and
content hashes. The palette checker follows these aliases while retaining the
original expected hashes and offsets. If a shared image is intentionally
changed later, review all consumers and update this manifest or split the asset.

Local recovery/evidence: `tutnt/.codex/backups/size-audit-assets.zip`,
`tutnt/.codex/work/size-audit/`, and the `size-audit-*` reports under
`.codex/validation` and `.codex/logs`. The two disposable comparison PK3s
(739,505,283 bytes in total) were removed after verification; their complete
resource/hash manifests and rendered comparisons remain. Original production
assets are also recoverable from Git history. The common `tutnt.pk3` is retained.
