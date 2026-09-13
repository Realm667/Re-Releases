# Stained-glass chapter artwork

Updated: 13 September 2026.

The sixteen A/B chapter images for chapters 02, 03, 04, 05, 06, 07, 09 and 10
use the user-approved I_06A variant 4: dark, weathered stained glass, oxidized
lead lines, mineral patina, muted colors and restrained warm light.
Every image reinterprets its matching user-supplied scene from
`C:/Temp/interms/`. I_06A is the exact approved PNG, without a second rendering.
Chapter 08 has no corresponding image pair in the supplied or existing set.

## Runtime contract

- Replacements: `tutnt/hires/graphics/interms/I_02A.png` through `I_10B.png`,
  restricted to the sixteen named A/B resources.
- Each output is a 460 x 778 PNG, preserving the existing replacement dimensions.
- All pixels are opaque. Straight rectangular corners intentionally replace the
  previous rounded, feathered alpha silhouette.
- The original low-resolution images remain unchanged at 230 x 389. The hires
  namespace keeps their logical size; no chapter layout or script changes are needed.
- The remaining title, frame, credit and ending resources are unchanged.

These sixteen images supersede the original gothic-illustration style and
source-derived alpha rules described in the historical
[2x artwork report](../../tools/artwork/interms-hires/README.md).
That report still documents the original 34-image pass and the other resources.

## Production and provenance

The built-in Imagegen tool generated each scene separately with the approved
I_06A master as its style reference. Generated portraits were mechanically
downsampled with high-quality bicubic filtering; no procedural style filter was used.
I_06A was copied directly from the approved 460 x 778 export.

[Prompts](../../tools/artwork/interms-stained-glass/prompts.json) record the common
style, per-image scene instructions and approved example prompt.
[Manifest](../../tools/artwork/interms-stained-glass/manifest.json) records the
source and installed PNG SHA-256 hashes.

Local source references live under `tutnt/.codex/references/interms-stained-glass/`.
Production masters, export helpers, rejected drafts and review sheets live under
`tutnt/.codex/work/interms-stained-glass-series/`; the exact approved example
remains in `tutnt/.codex/work/interms-stained-glass-i06a/`.
Previous replacement PNGs are retained under
`tutnt/.codex/backups/interms-stained-glass-20260913/`.
These local artifacts are excluded from Git and game packages.

## Validation

All sixteen PNGs were visually reviewed individually and as a series.
Automated decoding confirmed 460 x 778 dimensions and fully opaque alpha.
The installed I_06A matches the approved export byte for byte; hashes of all
original low-resolution chapter PNGs remain unchanged.
Local evidence: `tutnt/.codex/validation/interms-stained-glass/assets.json`.


UZDoom's actual resource-render checks passed for both the live source directory
and the integrated PK3: sixteen resources resolved and sixteen logical-size
assertions passed in each run (230 x 389), with completion markers and exit 0.
The rendered contact sheet was reviewed. No full campaign playthrough was performed.
The integrated build b125352663ea passed its engine check; its sixteen chapter
PNGs exactly match the installed artwork hashes.
Runtime logs: tutnt/.codex/logs/interms-stained-glass-render.log and
tutnt/.codex/logs/interms-stained-glass-packed.log.
