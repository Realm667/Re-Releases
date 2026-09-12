# UTNT intermission artwork at 2x resolution

34 replacement PNGs live in `tutnt/hires/graphics/interms/`. The source files in
`tutnt/graphics/interms/` are retained unchanged and supply the original logical
dimensions. Names are identical so the sourceport hires namespace resolves them.

The approved I_02A example defines the visual style: detailed dark gothic game
illustration, charcoal and umber stone, restrained red/orange light, and source
composition retained. The remaining illustrated assets were newly rendered with
the built-in Imagegen tool using their respective originals and the approved
example as references. `prompts.json` records the production instructions.

## Export and related assets

- Both dimensions are exactly twice the source dimensions, with no aspect change.
- All outputs are RGBA PNGs. For 33 files, every output alpha value exactly matches
  the corresponding source pixel replicated 2x in each axis, including feathering.
- M_CREDIT is newly typeset from the original 146 rows (150 text blocks because of
  the four two-column tester rows). It is 800x8400, with original line positions,
  indents, line extents and empty scrolling space retained. Antialiased glyphs use
  new transparent alpha, Impact outlines fitted to the original text bounds,
  rust-red heading gradients, warm pale-gray text and subtle surface grain.
  The transcript is recorded in `credits.txt`; the vertical bar separates columns.
- S_BORDER is the common newly illustrated frame for the wide images. Its original
  transparent central opening and feathered inner edges are retained.
- INTERP2 and TNTE4_2 use the same new artwork as INTERPIC and TNTE4_1, respectively,
  with source-derived darkening masks at the original text-panel positions.
- S_BORDET is the corresponding source-modulated frame variant.
- S_BLACK remains a uniform black technical fade image at twice the resolution.

The approved example is retained as-is. No original low-resolution source artwork
was overwritten. Generated intermediates are not part of the game package.

## Validation (2026-09-08)

`validation.csv` records all dimensions and alpha counts. All 34 PNGs were decoded
and checked; SHA-256 comparisons confirmed all original source files unchanged.
The complete assembled set was visually reviewed in `review-portraits.png` and
`review-other.png` (the latter shows only the opening of the tall credits).

An isolated render-overlay fixture in UZDoom 5.0.1 loaded the actual UTNT project,
resolved all 34 names, and drew every replacement. All 34 resource assertions
passed, the completion marker was reached, and the process exited successfully.
TexMan.GetSize reported the original logical sizes, e.g. 230x389 for I_02A and
858x480 for TITLEPIC. The rendered contact sheet confirmed the replacement artwork.
This was a targeted resource/render test, not a full campaign playthrough or a
check of every original timed transition.
