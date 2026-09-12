# Reforged menu logo

The main menu uses the approved Reforged runic logo as `M_DOOM`. It retains
the Quake-derived wordmark, bronze rune bands, central ampersand seal and amber
accents. This is menu branding; it does not rename every Remaster option or credit.

## Assets and placement

- Runtime patch: `tutnt/graphics/menu/M_DOOM.png`, 288 x 56 pixels, RGBA PNG.
- HiRes replacement: `tutnt/hires/graphics/M_DOOM.png`, 576 x 112 pixels.
  UZDoom keeps the base patch's logical 288 x 56 size and menu placement.
  This is rendered directly from the artwork source with twice the pixel dimensions.
- Main-menu placement: `StaticPatch 16,8,"M_DOOM"` in
  `tutnt/menudef/MENUDEF.base`, centered in the 320 x 200 menu coordinate space.
  Its bottom edge is 64; the first selectable row starts at 72.
- The background and letter holes are transparent; dark metal and outlines
  remain opaque. The patch uses binary alpha and colors from the mod's first
  PLAYPAL palette.
- The main-menu item labels, positions, shortcuts and navigation are preserved.
- The title is brand artwork, shared by all four interface languages.

## Rebuilding the artwork

`tools/artwork/menu-logo/approved-logo.png` is the approved source design.
`pixel-source.png` is its Imagegen pixel-art conversion with a magenta key;
the original request and the background correction are in `prompts.json`.
The earlier wordmark was typeset from Quake / DpQuake:
https://www.dafont.com/quake.font . No font binaries are shipped in the mod.

Run `python -B tools/build_menu_logo.py` to remove the key, tightly crop, fit
both native and double resolution, quantize to PLAYPAL and encode binary transparency.
Run with `--check` to verify the output against the source and current palette.
Changing PLAYPAL requires rebuilding both patches. The artwork sources and encoder
live outside the packaged game directory.

## Validation

Engine and visual checks are recorded under
`tutnt/.codex/validation/reforged-menu-logo/`.


Verified on 12 September 2026 with UZDoom 5.0.1:
- The current shared package rebuilt successfully with ACS compilation,
  localization/font checks and the engine load check (build `df48e91309bd`).
- English wide-window and German classic-window checks reached their completion
  markers. Visual review confirmed transparent letter holes, visible rune bands,
  centered placement and separation from the first menu row.
- A final TITLEMAP check loaded `tutnt.pk3` directly without the test overlay.
  The packaged PNG matched the source byte-for-byte and MENUDEF contained its
  StaticPatch call; the engine reached the completion marker.
- The logo encoder `--check` and definition-table `--check` both passed.
- Layout checking reported only five pre-existing TNT01/TNT02 editor/backup
  files belonging to other work; no logo-task artifact remained outside the
  prescribed directories.

## Double-resolution check (12 September 2026)

The 576 x 112 HiRes replacement passed the encoder check and the complete
package build with engine validation (build `9b1af87fe731`). TITLEMAP visual
review confirmed that the HiRes patch is selected, its text and runes gain
detail, transparency remains correct, and its screen position and logical size
match the base patch. Evidence: `tutnt/.codex/validation/reforged-hires-logo/`.
The checked package was promoted to `tutnt.pk3` after checking its source
fingerprint and comparing the resource inventory with the existing package.

## Sealed-skull menu selector (12 September 2026)

The selected fourth design replaces both original menu selection patches with
an ash-bone skull inside a bronze seal and short side horns. The second frame
lights the eyes and seal marks in amber. Both frames share exactly the same
silhouette and non-emissive shading, so the glow does not move the cursor.

- Native: `tutnt/graphics/fonts/M_SKULL1.png` and `M_SKULL2.png`, 25 x 19.
- HiRes: `tutnt/hires/graphics/M_SKULL1.png` and `M_SKULL2.png`, 50 x 38.
- Native PNG offsets are (5, -3), matching the replaced Doom patches. HiRes
  offsets are (10, -6); UZDoom's HiRes loader preserves the base logical size
  and derives its scaled offsets from that base.
- Both sizes use PLAYPAL colors and binary alpha, including the open seal gaps.
  The HiRes frames are rendered from the large source, not enlarged native pixels.
- A menu delegate blends the two fixed frames on a two-second cosine cycle.
  The dim skull stays fully opaque; only the amber illumination fades.
  UI time and fractional tics keep the fade moving smoothly during paused gameplay.
  The separate operating-system mouse pointer `doomcurs.png` is unaffected.

The approved concept, transparent Imagegen source and exact generation prompt
live in `tools/artwork/menu-skulls/`. Run
`python -B tools/build_menu_skulls.py` to rebuild, or add `--check` to verify
pixels, matching silhouettes and PNG offsets. The encoder fixes the geometry
to the dim frame and transfers only the generated amber illumination.

Validation: the encoder check passed for all four PNGs. UZDoom 5.0.1 ran both
native and HiRes asset overlays successfully; six screenshots per resolution
contained exactly two states, with differences confined to the selector.
The complete snapshot build `ef6b4a9961d8` passed localization/font checks,
ACS compilation, engine loading and its direct TITLEMAP menu check.
A newer concurrently built `tutnt.pk3` already contained all four identical
assets; its direct menu check also passed, so it was retained instead of
replacing newer integration. Evidence is under
`tutnt/.codex/validation/reforged-menu-skulls/`.

The fade is implemented in `tutnt/zscript/UTNT_MenuSeal.zc` and registered
through `mapinfo/MAPINFO.usability`. It inherits Doom menu sounds and only
handles the M_SKULL selector. The seal is shifted down by four logical menu
pixels to center it on the lettering, equally for native and HiRes images.
Menu scaling, navigation and alternate selectors retain their standard behavior.
Both draws disable texture animation so the engine cannot substitute the blinking endpoints.

Fade validation (12 September 2026): definition-table check and full build
`2950a53fd055` passed, including engine loading. Native and HiRes menu
captures contain 36 and 35 distinct selector states across 36 samples,
respectively; all TITLEMAP image changes stay inside the original selector
area. A paused TNT01 check also passed with 36 distinct states. The final
full package passed its direct menu test and was promoted to `tutnt.pk3`
after a source-fingerprint and resource comparison with no removed entries.
Evidence and animated preview: `tutnt/.codex/validation/menu-seal-fade/`.

Alignment validation (12 September 2026): the four-pixel downward adjustment
passed visual checks in native and HiRes menus. Evidence:
`tutnt/.codex/validation/menu-seal-alignment/`.
Full build `ac705d020353` passed engine validation. The shared
`tutnt.pk3` was verified identical to that checked build, including the
corrected selector code.
