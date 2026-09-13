# Cinematic TITLEMAP intro

Updated: 13 September 2026.

The four original illustrations play behind the original fortress border in a
22.6-second intro. Slow camera travel and overlapping dissolves lead into a
dimmed final illustration, a gently settling Reforged logo, and the three
localized project, author and UZDoom credit lines. The final scene continues
with a restrained anchored zoom, warm border illumination and a small number of embers.
Opening any menu hides the intro logo and credits immediately; closing it
restores the current composition without restarting the sequence or music.

## Musical timing

The original `music/D_DM2TTL.ogg` is unchanged. An analysis of its first 24
seconds finds strong positive RMS attacks at approximately 2.85, 9.60, 16.30
and 23.00 seconds. The montage follows the corresponding half-phrase grid:

| Time | Presentation |
| --- | --- |
| 0.00 | Black; start the original music and the presentation clock together. |
| 0.60 | Begin the border reveal, reaching full visibility at 2.70 seconds. |
| 2.86 | TITLE_1. |
| 6.22 | TITLE_2. |
| 9.58 | TITLE_3, aligned with the next strong musical attack. |
| 12.94 | TITLEPIC, always behind the border. |
| 15.20 | Begin darkening the illustration for the final title. |
| 16.30 | Reveal the logo on the next attack, with one quiet bass accent. |
| 18.60 | Fade in the Realm667 project credit. |
| 20.00 | Fade in the Daniel Tormentor667 Gimmer credit. |
| 21.40 | Fade in the UZDoom credit; fully visible at 22.60 seconds. |

Transitions use smoothstep curves, with 1.15-second scene dissolves and
1.2-second credit fades. The accent is a short synthesized, fading low-frequency
chord, without external samples. `tools/build_title_accent.py --check` verifies
its reproducible PCM data. It is played once at low gain and skipped if a menu
is open at the reveal, avoiding delayed playback when the menu closes.

## Renderer and lifecycle

`UTNTTitleIntro` is a per-level event handler. Its UI clock runs independently
of paused world simulation, so opening a menu does not desynchronize the
sequence from the music. Entering TITLEMAP again creates a fresh presentation.
All drawing is gated by the map name; gameplay maps receive no title overlay.
The embedded TITLEMAP ACS retains only the original camera and frozen-player
setup. Map geometry is unchanged.

`UTNTTitleCanvas` draws opaque black, the outgoing/incoming illustrations,
illustration dimming, the dark/light border pair, embers, logo and credits in
that order. Fully covered outgoing images stop drawing. Text uses existing
LANGUAGE keys and the mod's SmallFont with a parchment translation and shadow.
The three credits form a centered block, appearing successively from top to
bottom while earlier lines remain visible. All three share one scale, fitted
to the widest localized line. Their vertical step is exactly 1.5 times the
font's scaled line height, with the first row at 80% of viewport height.
No new player-facing text or language keys are introduced.

Illustrations and borders cover the viewport at every aspect ratio. Their
original proportions are preserved; the first three illustrations and border
are centered, while the final illustration follows its fixed beam anchor.
The transparent border opening and current viewport constrain the logo/text
widths. This avoids the previous ultrawide black side columns. Scene zoom has
overscan for lateral travel, so camera motion cannot reveal uncovered edges.

The initial zoom grows by 4.5 percentage points. TITLEPIC has no lateral travel:
its beam at x=831 in the approved 1716-pixel artwork is anchored to the logo
ampersand at x=286 in the 576-pixel logo. Scaling around this fixed point keeps
the beam behind the ampersand throughout the zoom and at every aspect ratio.
After the initial zoom, a smooth bounded extension approaches another 3.5
percentage points without a loop or reset. Reduced effects keep the same
alignment with a stationary image. The bright border variant blends gently
with the dark original, lighting runes and stone without full-screen flashes.
Only twelve analytic embers are drawn; there are no particle actors, random
streams, accumulating allocations or changes to gameplay simulation.

`UTNT_reducedfx` disables camera travel, logo settling, embers and border
pulsation. It preserves timing, smooth fades, readable text and menu behavior.
The completed reduced-effects composition is pixel-stable.

## Validation

Build `399efbebcfaa` passed all definition, localization/font, ACS and engine
checks. Five runtime cases passed (English, German, Spanish ultrawide, French
and reduced effects), including ten engine assertions. Image comparisons
confirmed moving illustrations and idle scenes, and a pixel-identical reduced-
effects final card. The menu-clock case advanced through 175 menu ticks.
The gameplay transition and fresh black restart were visually verified.

A separate normal-startup run of the full package, without a map command or
test overlay, passed and its title/menu/resume images were reviewed. The
reveal sound was observed on an active engine audio channel at its scheduled
time. The integrated `tutnt.pk3` is byte-identical to the tested package;
resource comparison found no removed files. Only SCRIPTS and BEHAVIOR changed
in the map WAD.

Evidence is stored under
`tutnt/.codex/validation/titlemap-cinematic/`; build logs are under
`tutnt/.codex/logs/titlemap-cinematic-build.log`.

The reusable `tools/test_titlemap.py` checks menu-independent timing, scene and
idle motion, a pixel-stable reduced-effects title card, original texture/font
availability, all four languages, 4:3/16:9/ultrawide layouts, leaving TITLEMAP
for gameplay and re-entering the intro. `tools/fixtures/titlemap/` contains the
independent engine-side observer. Tests create only central local artifacts.

The work-layout checker already reported eight unrelated TNT01/TNT02 editor
backup files before this task; those files are left untouched.

Beam alignment refinement: four UZDoom cases cover 4:3, 16:9, ultrawide and
reduced effects. Actual rendered beam positions at intro ages 18, 23, 60 and
180 seconds have zero horizontal pixel travel in every case. The measured
bright core below the logo stays within 1.5 pixels of the ampersand center.
The screenshot checks use controlled UI ages; all other rendering runs through
the normal title renderer. Evidence is stored under
`tutnt/.codex/validation/titlemap-beam-anchor/`.

The beam refinement package (`83a143c18d3f`) was built with the shared
packager and engine check from the previously validated integration
`399efbebcfaa`, because concurrent grass-source edits prevented a consistent
whole-project snapshot. The complete runtime resource comparison confirms
that only the title renderer and generated build identifiers changed; no
resources were added or removed. The shared `tutnt.pk3` is byte-identical to
this checked package. In-progress grass source changes remain separate.

Credit spacing refinement: UZDoom compilation and four language runs passed,
including 4:3 and ultrawide. Captures at 19.9, 21.3 and 23 seconds confirm the
cumulative one/two/three-line reveal and uniform spacing. Evidence is under
`tutnt/.codex/validation/titlemap-credit-spacing/`. Package `f8f5de999c58`
is derived from integration `67ef0e2f5d7b` with the shared packager and engine
check. Only the credit renderer and generated build identifiers changed;
the shared package is byte-identical to this verified package.

The credit block is lowered by 10% of viewport height to match the requested
placement. UZDoom checks and screenshots at 16:9 and 4:3 confirm the lower
position with spacing and sequential reveals preserved. Evidence:
`tutnt/.codex/validation/titlemap-credits-lower/`. Verified test package
`e360bddd7838` is derived from integration `f8f5de999c58`; resource comparison
confirms only the title renderer and generated identifiers changed.
