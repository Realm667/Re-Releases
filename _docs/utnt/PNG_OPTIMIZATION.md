# Lossless PNG storage optimization

UTNT's production PNGs can be recompressed without changing their image content.
`tools/optimize_utnt_pngs.py` uses the locally installed SLADE plugins PNGCrush,
PNGOUT and DeflOpt. The executables are external dependencies, not shipped in
this repository or the game package. Their paths and SHA-256 hashes are recorded
in each local report.

## Preservation rules

- Keep resolution, decoded RGB and alpha values, including RGB underneath fully
  transparent pixels. Keep indexed palette values and indices exactly.
- Preserve the payload and order of all ancillary chunks, including Doom `grAb`
  offsets, `alPh`, color profiles, transparency, text and provenance metadata.
  The optimizer does not use blanket metadata stripping or transparent-pixel
  blackening. Chunk checksums are recalculated, repairing pre-existing bad CRCs.
- Remove an entirely opaque alpha channel only when no palette, transparency,
  alpha-mask or other color-type-dependent chunk is present, then compare all
  decoded RGBA values. Palette/grayscale conversions are otherwise disabled.
- Accept only a smaller PNG which also does not increase its ZIP-deflated size.
  Compare the original and final images independently of the external tools.
- APNG, full-depth 16-bit images and malformed/unreadable files require separate
  verification. Record failures; do not silently turn them into accepted files.

## Explicit workflow

```text
python -B tools/optimize_utnt_pngs.py --plugins "<SLADE plugins directory>" --run-name review-1
python -B tools/optimize_utnt_pngs.py --apply-report tutnt/.codex/validation/png-optimization-review-1.json
python -B tools/test_png_storage.py
python -B tools/test_png_storage_runtime.py --report tutnt/.codex/validation/png-optimization-review-1.json --package tutnt.pk3 --engine "<uzdoom.exe>"
```

The first command operates only on copies. It inventories runtime PNG inputs,
creates an original-byte recovery ZIP under `.codex/backups`, and stores smaller
candidates under `.codex/work/png-optimization`. Identical inputs are processed
once and checked for every original path. Use a new run name for each audit;
existing backups are never overwritten. The final report must be reviewed for
errors and optimizer timeouts before application.

`--apply-report` verifies every original against the backup and the reviewed
hash, rejects concurrent source edits, and checks every candidate again before
writing any PNG. Current font, material, palette-regression and asset-sharing
manifests are updated only where the old hash matches a verified original.
Historical imported-image hashes remain separate from current storage hashes.

## Generators and verification

`tools/png_storage.py` provides a shared pixel/metadata comparison. Regular
material, sky-edge, lava-lip, CRT, effect-artwork and font generators retain an
already smaller equivalent encoding; explicit ENV authoring does the same.
If actual image content changes, the generator still emits its new content.
Normal packaging reads the resulting production assets from `tutnt/`; it does
not require the local backup, candidates or optimizer executables.

The font validator decodes PNG filters rather than assuming unfiltered RGBA
scanlines. The blue-color regression compares metadata payloads and actual
palette indices independently of IDAT compression and CRC encoding.

The runtime gallery samples large images, every changed image subfolder,
opaque-alpha reductions and repaired files. It compares actual engine screenshots
before and after with nearest and linear filtering. Every changed image also
receives a full-resolution, pixel-by-pixel comparison in the optimizer.

File size reduction is a storage/download optimization; it does not imply an
equivalent reduction in graphics memory. Published PK3 measurements must separate
PNG changes from concurrent map, model-compression and other project changes.

## Applied results (16 September 2026)

| Measurement | Result |
|---|---:|
| Production PNGs audited | 13,049 |
| Unique original byte streams | 12,273 |
| Files reduced | 8,178 |
| PNG bytes before | 242,454,346 |
| PNG bytes after | 212,137,517 |
| PNG bytes saved | 30,316,829 (12.50%) |
| ZIP-deflated payload bytes saved, level 6 | 30,263,751 |
| Entirely opaque alpha channels removed | 82 |
| Files with pre-existing CRC errors repaired | 194 |

All files were reviewed; none failed or timed out. The verifier rejected 38
PNGOUT candidates that violated exact image/index preservation and retained safe
alternatives. Every accepted file passed independent full-resolution RGBA,
palette-index, ancillary-data and compressed-size comparison before application.
All 13,049 originals are recoverable from the local recovery ZIP and Git history.

Post-application checks passed for palette/color regression (514 assets), fonts
(4 fonts with 171 glyphs each), asset consolidation, release effects (125 assets),
brightmap bindings (1,506), CRT artwork (48 screens), tester artwork (14 outputs)
and organic material cache (256 materials, 3,107 bindings). PNG storage and font
unit tests passed (22 tests). Generator manifests track current storage hashes;
original imported-source hashes remain intact.

Local evidence: `.codex/validation/png-optimization-reviewed.json`,
`.codex/validation/png-optimization-cache.json`, and
`.codex/backups/png-optimization-all.zip` below `tutnt/`.

The isolated test PK3 passed the UZDoom loading check. A 288-resource gallery
passed four engine runs (before/after, nearest/linear filtering), with zero
changed screenshot pixels in both comparisons. This is a sampled engine check
in addition to the exhaustive full-resolution image-data comparison.

The shared `tutnt.pk3` could not be replaced because another process held it open.
A subsequent normal build correctly refused publication after concurrent source
changes. Verification therefore used `.codex/builds/tutnt-png-optimized.pk3`;
the optimized editable assets are already present in `tutnt/`. This isolated
package uses DEFLATE for all assets, so its total size is not compared with the
shared package's mixed model compression. The next normal integration build
will include the optimized PNGs.

Runtime evidence: `.codex/validation/png-optimization-runtime.json` and
`.codex/logs/png-gallery-*`; package evidence:
`.codex/validation/png-optimization-package.json` and
`.codex/validation/png-optimization-package-sources.json`.

The complete package/source comparison confirmed all 13,049 PNGs match the
reviewed hashes and packaged bytes. No map or other included production asset
differed; the only byte difference was the existing `MAPINFO.txt` precache
packaging transform. Documented source-only ACS/voxel files and expanded TEXTURES
modules are omitted from the package. No new package-only asset transformation
was introduced by this optimization.

The work-layout audit reports 15 pre-existing editor state/autosave/backup files
under `tutnt/maps`. They belong to ongoing map editing and were left untouched;
all artifacts created by this task use the prescribed central directories.
