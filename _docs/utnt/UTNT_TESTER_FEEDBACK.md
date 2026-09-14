# Tester feedback fixes

Implemented 14 September 2026 for UZDoom 5.0.1.

## Feedback checklist

“Fixed” means the source correction and the relevant compilation/runtime or visual checks passed. The door hitch remains a verification exception rather than a claim of universal stutter-free operation.

| # | Report | Status | Change |
|---|---|---|---|
| 1 | TNT01 opaque, dark, still water | Fixed | Lower plane opacity, brighter underwater lighting, bounded fog and visible surface motion. |
| 2 | ObjectiveNext called every tic | Fixed | Empty queues sleep and wake on progress. |
| 3 | Spatial index spawned during prediction | Fixed | Explicit client-side thinker lifetime; four-peer validation. |
| 4 | Archvile fire obscures combat | Fixed | Sparse, smaller, more transparent warning effects. |
| 5 | Rocket trail disappears abruptly | Fixed | Smooth fade, expansion and rotation. |
| 6 | Transition board numeric warnings | Fixed | Explicitly rounded rectangle coordinates. |
| 7 | Weather/portal deprecated calls | Fixed | Current shader/iterator APIs and explicit initialization. |
| 8 | Source light-radius warnings | Fixed | Explicit rounding shared by both arenas. |
| 9 | Weather visor/CreditsSpark warnings | Fixed | Current shader APIs and rounded light radius. |
| 10 | Missing silent lump and texture warnings | Fixed | Valid silent lump and source sprite paths; packaged texture definitions verified. |
| 11 | Menu background too bright | Fixed | Stronger dimming behind text. |
| 12 | Episode color, heading graphics and localization | Fixed | Bronze BIGFONT throughout; concise translations, all 20 title widths checked. |
| 13 | Missing abilities at screen size 12 | Fixed | Both cards above the fullscreen HUD. |
| 14 | TNT01 light-ray color | Fixed | Authored warm rays changed to #CF834C. |
| 15 | Green IDMYPOS | Fixed | Bronze coordinate glyphs. |
| 16 | Thick Imp smoke | Fixed | 30% original opacity, original lifetime. |
| 17 | One-second TNT01 door freeze | Mitigated; exact hitch unconfirmed | Native map-load model precaching and preset-controlled GL precaching; no sight-triggered geometry generation found. |
| 18 | Yellow chaingun/minigun light | Fixed | Amber firing blend and impacts. |
| 19 | Excessive TNTLE fog | Fixed | Explicit bounded density with ownership-aware restoration and save migration. |
| 20 | Large PK3 | Improved | 17.71 MB lossless saving on identical model payload; size breakdown below. |
| 21 | Headline/subline gap | Fixed | Three additional logical HUD pixels. |
| 22 | Lock icons, including requested half size | Fixed | Correct card/skull icons and combinations at half preview size. |
| 23 | TNT02 lava scrolling direction | Fixed | All layers follow authored floor panning/orientation. |
| 24 | Bonus items lit by their own lights | Fixed | DontLightSelf for health and armor bonuses. |
| 25 | Yellow enemy hitscan lights | Fixed | Amber #FFA300, retaining relative intensity. |
| 26 | TNT02 switch lacks texture/sound feedback | Fixed | Preserve native switch texture identity instead of wet aliases; switch/reset tested. |
| 27 | Green/blue armor hard blinking | Fixed | Continuous illumination fade on a stable opaque sprite/voxel frame; pickup values preserved. |
| 28 | CandelabraNew yellow dynamic light | Fixed | Dedicated amber #FFA300 light, preserving radius, offset, attenuation and self-light exclusion. |
| 29 | TNT04CN black rectangles along the boss beam | Open: not reproduced | Current package checked in TNT04CN/TNT04C on Vulkan and OpenGL; original engine/renderer/package identification requested. |
| 30 | Build line beneath Status Bar and Statistics | Fixed | Removed the build label from the HUD options menu and regenerated MENUDEF. |

## Visibility and lighting

- TNT01 pool at (6056, 1671): water-plane opacity reduced from 240/255 to 136/255; both control sectors use brighter underwater lighting, a softer green light color and explicit low fog density. Geometry and gameplay remain unchanged. Liquid wave timing is separated from slow surface drift; underwater blur is reduced globally.
- TNTLE atmosphere: adding a fade color with zero explicit fog density made dark sectors inherit excessive light-dependent fog. The optional added haze now uses density 8, preserves authored nonzero densities and restores owned state when disabled. Saves retain the state; older active saves acquire the bounded density on their next update.
- TNT02 lava layers now use the floor texture matrix's authored panning and orientation instead of unrelated timer-driven travel. Surface turbulence remains. Model spill lips retain stable world mapping.
- TNT01 warm ceiling rays use #CF834C. Hitscan enemy muzzle and bullet-impact lights use amber #FFA300 (impacts retain half intensity). Chaingun/minigun firing blends use the same hue.
- Green and blue armor keep one opaque sprite/voxel frame and smoothly fade its light level between local ambient and bright over a two-second cycle. Native pickup values, inventory semantics and voxel rotation remain intact; overlapping transparent voxel copies are avoided.
- Health and armor bonus lights use DontLightSelf: the environment is still illuminated without tinting their own sprites.
- Imp projectile smoke uses 30% of its former opacity and proportionally reduced fade increments, preserving lifetime. Archvile warning effects use fewer, smaller low-opacity flames/smoke near the feet; attack targeting, timing and damage remain native.
- Rocket trails fade smoothly, rotate and expand, reaching transparency before removal.

## Interface

- Both ability cards remain visible above the fullscreen HUD at screen size 12.
- Title-menu backgrounds are dimmed by 78%. Episode and skill headings are live BIGFONT text; episode entries use the same bronze palette. Concise, equivalent translations keep every episode in BIGFONT on the native menu canvas.
- IDMYPOS glyphs are repainted in the notice bronze palette at the native positions without changing the engine CVar or global green translation.
- Map-entry subtitle spacing gains three pixels on the 640x480 logical HUD canvas.
- Denied-lock notices show the actual card/skull sprites, including alternatives and multi-key requirements. Icons are half the size of the first tester previews.

## Runtime and loading

- Objective completion processing sleeps after an empty queue. ACS progress notifications wake it; simultaneous completions, acknowledgements, save/load and hub transitions retain their existing ordering.
- Spatial indexes are client-side thinkers, created explicitly in the local thinker list. Cosmetic weather/heat indexing no longer creates network objects during prediction.
- Deprecated postprocessing calls use PPShader; actor searches use the level iterator API. Uninitialized temporary variables are explicit, draw rectangles use rounded integer endpoints and light radii are deliberately rounded. Both Source arena variants share the correction.
- Silent sound sequences reference the engine's dsempty lump. Rocket flame composites reference their source sprite path to avoid a self-referencing texture. The existing definition packager expands TEXTURES includes and omits their source modules from the texture namespace.
- Generated terrain-edge and lava-lip classes expose their own states for native model precaching. Packaged MAPINFO adds only each map's generated classes; grass/deadwood frame catalogs are included globally. No new geometry is generated when a door becomes visible.
- Hardware uploads at map loading require the engine's **Precache GL textures** option (`gl_precache`). All three UTNT visual presets enable it. For an existing setup, reapply a preset or enable the option, then restart the map. This addresses a first-visibility upload cause; the tester's exact one-second freeze has not been quantitatively reproduced and is not claimed eliminated on every system.

## TNT02 switch

The switch at (4312, -324, 64), line 329 / side 539, was being rebound from QBASEB1 to the wet-surface alias EV000566. This hid its identity from the native ANIMDEFS switch lookup, preventing texture and sound feedback. Environment bindings now yield to walls with active line specials. Existing saved aliases are restored during maintenance, without overwriting newer scripted textures. The map action and switch definition remain native.

## Package size

The measured candidate contains 11,992 OBJ models, with 207.15 MB of text data. Lossless LZMA reduces their packed size from 67.47 MB (Deflate level 6) to 49.77 MB, saving **17.71 MB** for identical decoded assets. UZDoom supports this native ZIP method. The candidate is 369.28 MB; shared integration size can differ as other artwork is integrated.

Largest compressed categories in that candidate: organic material maps 54.56 MB, high-resolution graphics 52.52 MB, terrain-edge meshes 48.49 MB. Music and texture artwork add further size. No image resolution, audio quality or map content is removed. LZMA trades additional decoding work at loading for the smaller download; precaching helps move that work out of first visibility.

## Validation

- Full snapshot build, archive integrity and engine compilation without the reported warnings; localization/definition/font checks.
- The final shared package (including current production voxels) passes all eight focused runtime cases: preset, core, fog, menus, lava, armor, switch and door. The first six assert 530 conditions and the switch asserts three native texture states; door/lava captures complete without runtime errors.
- Real objective triggers (12 assertions), simultaneous queue completions (12), hub roundtrip (15).
- Four real cooperative peers pass 91, 91, 92 and 87 assertions, including divergent local cosmetic quality and client-side prediction checks.
- Cosmetic save/load in TNT02 and TNTLE (6 assertions each); both Source boss encounters (96 assertions each).
- Focused engine fixture validates empty-queue idling, client spatial index identity/boundaries, smoke opacity and the rocket fade/rotation/lifetime envelope. TNTLE option on/off and save/load validate bounded density and restoration.
- Captures cover TNT01 water and HUD, card/skull notices, menus in four languages, TNT02 lava and the reported door. New fixtures are test-only and excluded from the game package.
- Eight build snapshot regressions and a map-precache metadata preservation test pass.

Runtime tools: `tools/test_tester_feedback.py`, `tools/test_objective_completion.py`, `tools/test_objective_completion_travel.py`, `tools/test_cosmetic_lifecycle.py`, `tools/test_source_maps.py`. Local evidence is under `tutnt/.codex/logs/` and `tutnt/.codex/validation/`.

## Source beam rectangles: investigation, 14 September 2026

The supplied screenshot shows a vertical series of black squares on the energy
beam. This has **not** been marked fixed: no matching artifact was reproduced
with immutable integration build `0acf5ccce3a5` (source revision `ce0692e31`)
on UZDoom 5.0.1 / NVIDIA RTX 4080. Both TNT04CN and TNT04C were captured on
Vulkan and OpenGL. Comparisons include nearest/trilinear texture filtering,
bloom disabled, and the tonal filter disabled or highlights at -100. The
current captures remain free of the reported black squares; there are no
matching rows of placed actors along the beam axis. No speculative material
or combat change was made. Engine version, renderer and whether the reporter
used the latest package remain needed to reproduce the original result.

Unedited captures and engine logs use the `source-rectangles-` prefix under
`tutnt/.codex/logs/`; the exact tested package is retained in
`tutnt/.codex/builds/source-rectangles-baseline.pk3`. The first background-mode
capture rendered at reduced resolution; only subsequent full-resolution
captures were used for the visual assessment.
