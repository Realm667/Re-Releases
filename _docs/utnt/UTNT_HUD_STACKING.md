# Pickup stacking and SBAR ability cards

Key/weapon/powerup cards are centered at the upper screen margin. The shared
top safe area keeps them below a visible boss bar. When a centered pickup overlaps
the horizontal footprint of a corner objective overview or completion card, that
corner card moves below the pickup with the standard gap. Wide screens keep the
two elements alongside each other. Pickup height follows the actual wrapped text.
Ability cards stay above the status bar; their horizontal margins still prevent
overlap when UI scale exceeds status-bar scale.

Both ability cards use `UABFRAME`, a native TEXTURES composition of the existing
STBAR stone and bevel patches. The original palette indices are retained, so their
backgrounds and borders follow PLAYPAL just like the status bar. There are no new
RGB background images or changes to PLAYPAL. Stepped corners, light labels and
recessed progress tracks replace the former bronze plaque treatment. Ability state,
timers, bindings and active class colors remain functional.

## Initial SBAR validation (2026-09-09)

UZDoom 5.0.1/Vulkan: 105 runtime assertions across 640x480, 960x540, 1024x768,
1920x1080 and 2560x1080; UI scale 0.75–1.5; HUD scale 1–3; screenblocks 9–11;
all three classes and English/German. Real red-skull touches, a deliberately long
three-line key name, ready/cooldown/active states and both horizontal and vertical
clearance are exercised. Runtime screenshots were visually inspected.

An isolated palette probe rotates RGB in every PLAYPAL subpalette. Its 21 checks
pass; screenshots show that the ability stone/bevels and SBAR both become violet.
The diagnostic palette is confined to the test add-on. The production palette is
never modified by this test.

The matrix uses a snapshot of commit 79fdfce94d87564ff914c00782860cbdede43732 plus
these HUD changes because other project work was changing concurrently. Evidence
and the exact changed-source hashes are under `tools/validation/hud-stacking-2026-09-09`.
Initial OpenGL attempts timed out during engine initialization; successful runtime
coverage reported here is Vulkan. This is a HUD regression check, not a campaign
or cooperative gameplay acceptance test.

The complete current local project was subsequently rebuilt with all 14 ACS
modules unchanged and engine validation passed. Build `a57a8bfb8493` contains
9,129 entries (SHA-256 `757e32ab33b85501426eaeda7bf82d16710288ac507235306433490f105cf18c`).
It includes concurrent local work; the HUD commit contains only this change.
A runtime check of that exact PK3 passes another 21 assertions and captures
cooldown/ready, wrapped-pickup and active states (`package-test` evidence).

Repeat with `python tools/test_hud_stacking.py --engine PATH --iwad PATH`.
`--mod PATH` accepts a source directory or PK3. Add `--quick --palette-probe` for
the diagnostic palette, or `--renderer 0` to request OpenGL. Test actors and palettes
are outside `tutnt` and are not shipped in the game package.

## Top-center revision (2026-09-09)

The updated current-project matrix passes 135 assertions in the same five sizes,
checking the upper safe edge, horizontal centering, wrapped text and collision
clearance for corner objectives as well as the unchanged ability-card spacing.
An additional simulated boss overlay passes 27 assertions and visually confirms
the pickup below the boss bar. Evidence is in
`tools/validation/pickups-top-center-2026-09-09`.

The engine-validated current package is `tutnt-top-center.pk3`; the existing
`tutnt.pk3` was open and could not be replaced during delivery.
