# Double-resolution interface fonts

13 September 2026. `BIGFONT` and `SMALLFONT` use newly drawn glyph artwork at
twice the original pixel width and height. BIGFONT uses the selected **Classic**
design: Roman wedge serifs, aged pewter faces and restrained silver highlights.
SMALLFONT uses the selected **Retro** design: compact golden-bronze letters with
deliberate stepped contours and open counters. `BIGUPPER` shares the large artwork
and `UCRBIG` retains its brighter treatment. Each variant includes 171 Unicode glyphs.
Existing engine color translations still tint menu and HUD text.
Both fonts retain their original base palettes. Import maps the new artwork's
luminance distribution to RGB colors actually used by `DBIGFONT.fon2` and the
original `STCFN` patches: neutral dark gray for BIGFONT, dark brown-bronze for
SMALLFONT. The brighter concept-sheet colors do not become the runtime colors.
Alpha coverage is preserved; `UCRBIG` keeps its established 1.8x brightening.

## Engine integration

UZDoom 5.0.1 supports `Scale 2` in the Unicode font directory's `font.inf`.
Its font loader applies that texture scale before calculating character advance;
display dimensions and PNG offsets are divided by two. `FontHeight`, `SpaceWidth`
and `Kerning` remain in their original logical units. SmallFont therefore retains
its 11-unit line height and BigFont its 20-unit line height. Every glyph's original
advance, height and offset is checked against the unmodified source artwork.
Existing menus, HUDs, wrapping and localization use the same font names and metrics.

This is redrawn artwork, not duplicated source pixels. Readability still depends
on the actual on-screen text size; very small UI scaling cannot show every detail.
The original font sources remain available for reproducibility and comparison.

## Sources and regeneration

- `tools/font-sources/hires/*-atlas.png`: authored atlases assembled from the
  selected Classic and Retro Imagegen specimens and matching punctuation sheets.
  Each atlas has eight columns and eight rows; cells contain ASCII 33–95, with
  a dedicated sharp-S in the final cell. A magenta key is removed during import.
- `tools/import_hires_fonts.py`: optional Pillow import step; extracts coverage,
  removes key-color spill, resamples each glyph into its original bounds at 2x,
  applies the original font's shared color ramp,
  and writes the portable RGBA palette/glyph JSON sources beside the atlases.
- `tools/build_localized_fonts.py`: standard-library-only build from those JSON
  sources. It composes accents, ligatures, localized punctuation and lowercase
  aliases, preserving exact doubled source metrics. Authored sharp-S overrides
  replace the generated fallback for both ß and ẞ. Accent strokes use opaque
  face colors rather than translucent edge pixels.
- `tutnt/fonts/`: generated runtime PNGs and definitions;
  `tools/font-glyphs.json`: pixel dimensions, scale, offsets and content hashes.

Run `python -B tools/import_hires_fonts.py` only when changing an atlas (optionally
with `--font bigfont` or `--font smallfont` to import just one), then
`python -B tools/build_localized_fonts.py`. Commit sources, generated assets and
the manifest together. Normal builds and CI need no Pillow dependency.

## Generation prompts

The user selected Classic from six BIGFONT proposals and Retro from six SMALLFONT
proposals. Their alphabet and digit rows supply the actual glyph shapes; matching
punctuation was generated separately with explicit character order. Targeted
Imagegen edits replaced specimen backgrounds with magenta while preserving the
chosen lettering. Import removes the key and fits each glyph to the original
2x bounds. Runtime PNGs contain real alpha. The large specimen previews show
the art direction; detail at actual game size is limited by the glyph resolution.

## Validation

UZDoom 5.0.1 passed 11,268 assertions across the four language/layout cases and
four credits cases with the rebuilt integration package. All 688 packaged font
assets match their generated sources; all font variants have real alpha and no
magenta key pixels. Eleven font unit tests and the reproducibility, coverage and
definition-layout checks passed.

`tools/build_localized_fonts.py --check`, `tools/check_font_coverage.py` and
`tools/test_font_coverage.py` check reproducibility, all localized characters,
original display metrics and solid accent colors. The localization runtime test
checks glyph dimensions and offsets after scaling, font selection, layouts and
credits in English, German, Spanish and French. Its grouped-credit fixture now
uses the group's frame bounds rather than indexing a three-row card layout;
creator and thanks cards are checked against their actual dynamic heights.

Classic/Retro screenshots and runtime results are under
`tutnt/.codex/validation/fonts-classic-retro/`. The selected specimens, extraction
work, final preview and exact built-in Imagegen prompts are under
`tutnt/.codex/work/bigfont-classic/`; the six SMALLFONT proposals are under
`tutnt/.codex/work/smallfont-six-variants/`. These local working files are excluded
from Git and game packages; the finished atlases and glyph sources are versioned.
