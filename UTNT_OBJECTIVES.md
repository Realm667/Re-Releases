# UTNT objectives

The approved iron/brass artwork, ember accent, demonic relief and existing
DBIGFONT/SmallFont typography remain in use. Separate localized headings and
descriptions cover all 21 goals in English and German.

## Behavior

- At the original ACS briefing point, a compact upper-left panel shows only
  numbered goal headings for four seconds, including its brief fades. It leaves
  the center of the view clear. The existing quiet switch sound accompanies it.
  Objectives no longer produce additional ACS console/notification messages.
- Hold **O** to read the full plaque. Press and release fade it in/out over
  0.2 seconds (seven tics), including text and shadow. Reversing mid-fade
  continues smoothly from the current opacity. The default
  applies only if O is unbound. Change it under UTNT Options, **Show objectives
  (hold)** / **Missionsziele anzeigen (halten)**, or the UTNT control section.
- Manual reading works before and after the automatic summary, including the
  TNT03A2 continuation. The full plaque is smaller than the initial version.
  Opening a menu/console, pausing, dying or loading/changing levels clears the
  held state so it cannot leave a stuck plaque.
- Neither view blocks firing/movement, pauses the world nor changes actors.
  No combat detection is used. Subtitles draw above objectives.
- The original automatic dispatch is unchanged: TNT04A retains its 1,860-tic
  cinematic delay; TNT03A2 has no second automatic briefing. Duplicate adapter
  calls and respawns do not restart the saved timeline. Old save timers are
  clamped to the new four-second duration when rendering.
- Descriptions wrap using font metrics and row heights grow with the text.
  Caps retain their proportions across 4:3 and widescreen viewports. Their
  shared edges are rounded once to whole screen pixels, preventing gaps and
  overlapping alpha at fractional scales.
  Objective completion and campaign progression are unchanged.

## Artwork transparency

The original approved RGB bitmap is preserved byte for byte. Native drawing
clips remove its baked black outside margin, following the protruding emblem
and top corners. Two separate low-opacity shadow layers are drawn behind the
opaque metal. The world is visible outside the contour; interior dark pixels
are retained. Only the existing three texture caps are used, avoiding hundreds
of intermediate texture decodes on first opening.

`tutnt/zscript/UTNT_Objectives.zc` renders both views.
`UTNT_Presentation.zc` owns the saved timer and local hold state.
`KEYCONF.objectives` defines the press/release aliases and default binding.
`TEXTURES.objectives` supplies the three caps from `graphics/hud/UTOBJART.png`.
The original artwork prompt is in `tools/objectives-artwork-prompt.txt`.

## Verification

Set `UTNT_ENGINE` and `UTNT_IWAD`, then run:

```
python tools/test_objective_controls.py
python tools/test_objectives.py --lang deu --width 1024 --height 768
python tools/test_objectives.py --lang enu --width 1920 --height 1080 --renderer 0
python tools/test_objective_mapstarts.py
python tools/test_objective_seams.py --renderer 1
python tools/test_objective_seams.py --renderer 0
```

Tests use isolated configs/saves and test addons outside the packaged game.
The controls suite exercises actual press/release aliases on TNTLE, firing
during both views, manual access before/after the summary, save/load, old timers
menu cancellation, fade endpoints/reversal and absence of duplicate ACS
messages. The layout suite checks all nine variants, both text
types, wrapping, duplicate calls and persistence; it previews all full plaques
through a test-only drawing hook. The map-start suite checks real ACS dispatch.
Each suite accepts `--mod` for a built PK3.

Evidence for this revision is in `tools/validation/objectives-compact-2026-09-07/`.
The earlier `objectives-2026-09-07` evidence records the superseded automatic
large plaque. These focused checks are not a full campaign playthrough or a
multiplayer certification. Existing player configs and saves are not modified.

Fade and message-removal evidence: `tools/validation/objectives-fade-2026-09-08/`.

Pixel-join regression (Pillow/numpy screenshot reads): `tools/validation/objectives-seams-2026-09-08/`.
