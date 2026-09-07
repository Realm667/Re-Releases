# UTNT objective plaque

Map briefings now use the approved dark iron/brass plaque with an ember accent,
demonic relief, numbered rows and ivory text. DBIGFONT and SmallFont keep the
existing UTNT typography. Artwork contains no baked-in text. Separate localized
headings and descriptions cover all 21 objectives in English and German; the
console history uses the same revised descriptions.

## Behavior

- Existing episode title and ACS timings remain authoritative. TNT04A retains
  its 1,860-tic cinematic delay; TNT03A2 remains a continuation without a second
  briefing. Title and intermission maps remain excluded by the original script.
- The plaque fades in over 14 tics, holds for 8 seconds (two goals) or 10 seconds
  (three goals), and fades out over 18 tics. One quiet existing switch sound
  accompanies arrival. Reduced effects disable the brief highlight animation.
- Descriptions wrap using actual font metrics; row height grows with the text.
  Top and bottom artwork caps keep their proportions. The panel respects 4:3,
  widescreen and ultrawide viewports. Subtitles draw above the plaque.
- Timing belongs to the saved level handler. Duplicate adapter calls and
  respawning do not restart the briefing; saving/loading preserves its timeline.
- Objective completion triggers and campaign progression are unchanged.

## Files and verification

`tutnt/zscript/UTNT_Objectives.zc` renders the plaque;
`UTNT_Presentation.zc` owns its saved timer and draws it;
`source/tutnt.acs` invokes the adapter at the original briefing point.
`TEXTURES.objectives` defines three caps from `graphics/hud/UTOBJART.png`.

Set UTNT_ENGINE and UTNT_IWAD to run:

```
python tools/test_objectives.py --lang deu --width 1024 --height 768
python tools/test_objectives.py --lang enu --width 1920 --height 1080 --renderer 0
python tools/test_objective_mapstarts.py
```

Tests use isolated configs and saves, disable background pausing in those test
configs, and load a test-only addon outside the packaged game. They check actual
localized fonts, all nine briefing variants, timer persistence, duplicate calls,
expiration, reduced effects, and real ACS map-start dispatch. `--mod` accepts a
built PK3 for the same checks. Runtime evidence is stored under
`tools/validation/objectives-2026-09-07/`.

The text-free panel was created with the built-in Imagegen tool from the approved
mockup. Its final prompt is preserved in `tools/objectives-artwork-prompt.txt`.
No API/CLI image generation was used. Existing UTNT fonts supply all text.

The automated checks do not constitute a full campaign playthrough or a new
multiplayer certification. No existing save files or player configs were changed.

## Acceptance, 2026-09-07

All 14 ACS modules compile; only the shared TUTNT bytecode changes. Three
UI/lifecycle cases passed with 331 assertions across English/German and
OpenGL/Vulkan. The other nine campaign map starts passed with 26 assertions,
including the intentionally skipped continuation and delayed TNT04A briefing.
The final live PK3 was engine-validated and passed the German Full HD suite.

Final tested live PK3 SHA-256: `15f9edbe50651137f3f0d0e3f0f8f2322ed58ff166fbae46ba53d2a223f1e660`.
