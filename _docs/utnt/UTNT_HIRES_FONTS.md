# Double-resolution interface fonts

13 September 2026. `BIGFONT` and `SMALLFONT` use newly drawn glyph artwork at
twice the original pixel width and height. The large letters retain their gray
Quake-style metal forms; the small letters have clearer bronze faces, cleaner
edges and more legible counters. `BIGUPPER` shares the large artwork and `UCRBIG`
retains its brighter treatment. Each variant includes 171 Unicode glyphs.

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

- `tools/font-sources/hires/*-atlas.png`: authored ASCII atlases, generated with
  the built-in Imagegen tool from the original font reference sheets. Each atlas
  has eight columns and eight rows; cells contain ASCII 33–95, with the final cell
  empty. A uniform magenta key is removed during import.
- `tools/import_hires_fonts.py`: optional Pillow import step; extracts coverage,
  removes key-color spill, resamples each glyph into its original bounds at 2x,
  and writes the portable RGBA palette/glyph JSON sources beside the atlases.
- `tools/build_localized_fonts.py`: standard-library-only build from those JSON
  sources. It composes accents, ligatures, localized punctuation and lowercase
  aliases, preserving exact doubled source metrics. Accent strokes use opaque
  face colors rather than translucent edge pixels.
- `tutnt/fonts/`: generated runtime PNGs and definitions;
  `tools/font-glyphs.json`: pixel dimensions, scale, offsets and content hashes.

Run `python -B tools/import_hires_fonts.py` only when changing an atlas, then
`python -B tools/build_localized_fonts.py`. Commit sources, generated assets and
the manifest together. Normal builds and CI need no Pillow dependency.

## Generation prompts

Both source requests specified the exact 8×8 ASCII order, original glyph
proportions, no hexadecimal labels or extra symbols, cleaner contours, accurate
punctuation and functional small-size game-font readability. BIGFONT requested
faithful angular, weathered gunmetal Quake serifs with restrained texture;
SMALLFONT requested compact bronze-gold lettering with simple strong strokes,
clear counters and restrained bevels, intended for 14-pixel cap height.

The first exports contained a baked checkerboard instead of alpha. A targeted
Imagegen edit replaced only that background and all negative spaces with uniform
RGB 255,0,255, preserving the lettering and cell positions. These corrected
atlases are the versioned source; runtime PNGs contain real alpha and no key color.

## Validation

UZDoom 5.0.1 passed 11,268 assertions across the four language/layout cases and
four credits cases with the rebuilt integration package. All 688 packaged font
assets match their generated sources; all font variants have real alpha and no
magenta key pixels. Ten font unit tests and the reproducibility, coverage and
definition-layout checks passed.

`tools/build_localized_fonts.py --check`, `tools/check_font_coverage.py` and
`tools/test_font_coverage.py` check reproducibility, all localized characters,
original display metrics and solid accent colors. The localization runtime test
checks glyph dimensions and offsets after scaling, font selection, layouts and
credits in English, German, Spanish and French. Its grouped-credit fixture now
uses the group's frame bounds rather than indexing a three-row card layout;
creator and thanks cards are checked against their actual dynamic heights.

Local screenshots and runtime results are under
`tutnt/.codex/validation/fonts-2x-final/` and `fonts-2x-credits/`; the comparison is under
`tutnt/.codex/work/fonts-2x/`.
