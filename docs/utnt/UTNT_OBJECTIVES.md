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
  No combat detection is used. Layout reserves space for the boss plaque and subtitles.
- The original automatic dispatch is unchanged: TNT04A retains its 1,860-tic
  cinematic delay; TNT03A2 has no second automatic briefing. Duplicate adapter
  calls and respawns do not restart the saved timeline. Old save timers are
  clamped to the new four-second duration when rendering.
- Descriptions wrap using font metrics and row heights grow with the text.
  Caps retain their proportions across 4:3 and widescreen viewports. Their
  shared edges are rounded once to whole screen pixels, preventing gaps and
  overlapping alpha at fractional scales.
  At small resolutions or with long subtitles a compact text layout preserves native pixel legibility.
  Campaign progression and authored exit destinations are preserved.

## Artwork transparency

The original approved RGB bitmap is preserved byte for byte. Native drawing
clips remove its baked black outside margin, following the protruding emblem
and top corners. Two separate low-opacity shadow layers are drawn behind the
opaque metal. The world is visible outside the contour; interior dark pixels
are retained. The full plaque uses its existing three texture caps, avoiding hundreds
of intermediate texture decodes on first opening.

`tutnt/zscript/UTNT_Objectives.zc` renders the overview, full plaque and completion.
`UTNT_Presentation.zc` owns saved timers, progress mirrors and local hold state.
`keyconf/KEYCONF.objectives` defines the press/release aliases and default binding.
`textures/definitions/TEXTURES.objectives` supplies the full-plaque caps and four completion slices from
`graphics/hud/UTOBJART.png`; no bitmap was changed for completion rendering.
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

## Completion and progress

All 21 goals now use the approved compact upper-left completion plaque: numbered
badge, brass check seal, localized small heading and ivory goal title. The final
goal changes the heading to ALL OBJECTIVES COMPLETED / ALLE ZIELE ABGESCHLOSSEN.
The Mastermind goal additionally explains that the pillars have been lowered.
The old completion Print/PrintBold and loud confirmation are replaced by this
plaque and a quiet metal switch sound. Other gameplay hints remain intact.

Each notification fades in for seven tics (0.2 s), holds for 105 tics (3 s), then
fades out for seven tics (0.2 s). A single restrained seal glint is disabled by
Reduced FX. Shared rounded frame edges avoid one-pixel gaps. Holding O takes
visual priority; its completed rows retain readable descriptions, gain the same
seal and COMPLETED label, and the footer counts completed goals.

ACS global arrays 60/61 store campaign progress and a FIFO of pending completion
notifications. Each goal is recorded once; every queued entry captures its own
progress snapshot. Consecutive completions therefore cannot overwrite one
another or prematurely claim that all goals are complete. The queue crosses
map transitions, including exits through INTERMAP. Save/load restores progress
and the active notification timeline. TNT03A1 and TNT03A2 share episode 3; a hub
return refreshes the local mirror instead of replaying old notifications.
Existing saves can record subsequent completions but cannot reconstruct goals
completed before this tracking was installed.

| Maps | Completion triggers |
| --- | --- |
| TNT01 | Existing scripts 110 / 111 |
| TNT02 | Existing scripts 211 / 212 / 213 |
| TNT03A1, TNT03A2 | Existing 211 / 219 storage trigger; mining-facility entrance and final exits; 212 / 213 retained as adapters |
| TNT03B | Guard boss death in shared BOSSHP; portal exit |
| TNT04A | Plasma generator script 4; second Mastermind in script 11; portal exit |
| TNT04B | Existing scripts 25 / 24 in displayed objective order |
| TNT04CN, TNT04C | Source-arena arrival script 140; Source boss death in shared BOSSHP |
| TNTLE | Existing scripts 223 / 224 |

Six existing Teleport_NewMap linedefs use script 250 to record their milestone
immediately before forwarding the original destination, start and flags. Map
geometry, activation flags, node lumps and gameplay sequences remain unchanged.
No test handlers, invulnerability or test transition overrides ship in the PK3.

### Completion verification

```
python tools/test_objective_completion.py --all
python tools/test_objective_completion.py --map TNT02 --lang deu --renderer 0
python tools/test_objective_completion.py --map TNT04A --lang deu
python tools/test_objective_completion_travel.py --mode hub
python tools/test_objective_completion_travel.py --mode queue
python tools/test_objective_contracts.py
```

The completion tests invoke the authored ACS scripts and boss-death paths,
check saved state and notification identity, duplicate suppression, timing and
exit destinations. The hub test performs an actual A1 -> A2 -> A1 roundtrip.
Test-only MAPINFO skips the manual statistics screen for the two exit cases;
production transition presentation is unchanged. These are focused trigger
regressions, not a complete gameplay walkthrough or multiplayer certification.
Evidence: `tools/validation/objectives-completion-2026-09-08/`.

Shared layout, wrapped completion headings and current combined regressions: [UI refinement](UTNT_UI_REFINEMENT.md).
