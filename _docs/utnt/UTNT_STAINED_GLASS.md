# Stained-glass chapter artwork

Updated: 14 September 2026.

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

## TNT04A intro portraits

I_INTROA and I_INTROB are two dedicated opaque 460 x 778 portraits, replacing
widescreen background resources in the reader's right column. A adapts the user's
TNT04CN screenshot: a floating basalt fortress beneath a fiery storm opening,
with an amber beam, suspended rocks and organic volcanic foothills. Lava rivulets
and ember haze blend the uneven ground into the surrounding sky. B is the unchanged
former first portrait of the towering Source ritual chamber and amber seal.
Both use I_06A as the stained-glass style reference. The original TNTE4 backgrounds
are preserved. The shared reader fits the illustrations proportionally and draws
the same bronze edges as the text plaque, with the shared 2:1 column split.

The built-in Imagegen tool authored both illustrations. Production export applies
uniform bicubic downsampling and a small central crop to match 460:778 exactly;
the sigil and architecture are never stretched. Local masters are retained under
tutnt/.codex/work/intro-stained-glass/ (chamber) and
tutnt/.codex/work/intro-stained-glass-exterior/ (fortress) and
tutnt/.codex/work/intro-organic-rock/ (organic rock and atmospheric lava revision). The user screenshot
is retained under tutnt/.codex/references/intro-stained-glass/TNT04CN.png.
[Intro prompts](../../tools/artwork/intro-stained-glass/prompts.json) and
[manifest](../../tools/artwork/intro-stained-glass/manifest.json) record provenance.

TNT04A portrait update, 14 September 2026: two UZDoom runtime cases passed
76 assertions at 1280 x 720 (English) and 640 x 480 with 150% UI scale (German).
Both portraits and the intermediate dissolve were visually reviewed. Resource
dimensions, shared columns, reader save/load and host skip cleanup passed.
Local evidence: tutnt/.codex/validation/intro-stained-glass/runtime.json and
assets.json; screenshots: tutnt/.codex/logs/intro-glass-*.png.

The exterior-first revision passed 38 UZDoom assertions with the German reader
at 1280 x 720; both displayed positions were visually reviewed. SHA-256 confirms
that position B is byte-identical to the former A. Evidence:
tutnt/.codex/validation/intro-stained-glass-exterior/ and
tutnt/.codex/logs/intro-glass-exterior-a.png / intro-glass-exterior-b.png.

The organic-rock refinement passed the seven intro resource/layout assertions.
The first portrait was visually reviewed in the German 1280 x 720 reader;
both images remain opaque 460 x 778, and B retains its previous hash.
Evidence: tutnt/.codex/validation/intro-organic-rock/ and
tutnt/.codex/logs/intro-organic-rock.png.
