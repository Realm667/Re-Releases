# TITLEMAP intro

Updated: 13 September 2026.

The original border and four-image sequence is retained. All four illustrations,
including TITLEPIC, render behind the dark and illuminated border layers. The
existing transparent M_DOOM Reforged logo fades into the final composition,
followed by the project, author and engine credits. LANGUAGE keys provide the
English, German, Spanish and French versions using the original SmallFont.

## Sequence and layers

- 0 seconds: black background.
- 2 seconds: dark border begins its three-second fade.
- 10, 16, 22 and 28 seconds: TITLE_1, TITLE_2, TITLE_3 and TITLEPIC begin their
  original four-second fades, with overlapping illustration transitions.
- 34 seconds: title logo fades in over two seconds.
- 36 seconds: the three credit lines fade in over two seconds.
- 38 seconds: the fully opaque composition becomes persistent HUD messages,
  preventing the old six-/twelve-minute timeouts from removing its layers.

HUD message IDs draw back to front: black 90; illustrations 80, 70, 60, 50;
dark/light borders 30/20; credits 10/11/12; logo 1. Art uses the original
640 x 480 virtual canvas, while the logo and text share a 480 x 360 canvas.
The menu remains accessible during the sequence.

The authoritative ACS source and compiled BEHAVIOR are embedded in
`tutnt/maps/titlemap.wad`. The existing music and artwork assets are reused.

## Validation

Full build `541ac1068a5c` passed localization, glyph coverage, ACS compilation
and engine loading. All 14 localization unit tests passed. UZDoom completed
the sequence in English, German, Spanish and French, covering 4:3, 16:9 and
ultrawide windows; final cards and menu access were visually reviewed. A direct
full-package run without an overlay also passed. Only SCRIPTS and BEHAVIOR
changed in TITLEMAP; all geometry lumps are identical. The shared `tutnt.pk3`
is byte-identical to the checked package, with no removed resources.

The existing menu dimming remains in use; its own title is drawn over the
background title card. Menu-specific hiding and adaptive ultrawide artwork
coverage are possible future presentation refinements.

The work-layout checker reports eight pre-existing TNT01/TNT02 editor backup
files, unrelated to this change. No files from this task violate the layout.

Local evidence is stored under
`tutnt/.codex/validation/titlemap-intro/`, with the build log under
`tutnt/.codex/logs/titlemap-intro-build.log`.
