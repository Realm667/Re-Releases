# Secrets and automap presentation

Implements the approved secret-discovery plaque and automap mockups in UZDoom 5.0.1.

## Secret discoveries

The compact iron plaque sits horizontally centered at 40% screen height. A bronze seal accompanies the gold heading and the current level's discovered/total secret count. English and German strings are provided. The plaque uses the existing notice queue, fade timing and duplicate coalescing; notices wait while the objective board or full-screen automap is open.

`Marine.OnGiveSecret` also covers Scout and Commando through inheritance. The native engine still awards both personal and level secret counts and consumes secret sectors. The callback replaces only the original center message and sound: `printmsg`, `playsound`, local view and `cl_showsecretmessage` are respected. The level count advances after the callback, so the displayed discovery is the current count plus one. Loading a save does not replay old notices. Existing maps and ACS scripts need no edits.

## Automap

The full-screen map uses a subdued iron background, bronze architecture, an ivory player chevron, the map identifier/title and a compact localized lock-color legend. The original status bar remains visible. Statistics use the existing `fullhud_stats`, `fullhud_fullstats` and `fullhud_statspos` settings, including remaining counts and time. The overlay automap retains the gameplay HUD.

The engine draws the actual map geometry, zoom, rotation, discovered lines and player position. The mockup's schematic layout is not substituted for map geometry. No production code reveals unexplored lines or secret sectors. Native automap preferences are preserved; custom colors/background remain subject to the engine's automap options.

The renderer saves the screen clip rectangle in RenderUnderlay, limits the native HUD to its bottom 32 scaled units on the full map, then restores that rectangle at the start of RenderOverlay. This replaces duplicate native title/statistics labels without changing protected engine CVars or migrating SBARINFO. A different third-party status bar with content above that band would need its own integration.

`LOCKDEFS.exploration` repeats Doom locks 1–6 and 129–134 with only Mapcolor changed. Key requirements, card/skull alternatives and message keys match the installed UZDoom definitions. Other locks remain defined. The colors also match the legend. Blue is explicitly `#00759F` (RGB 0, 117, 159), following the user's PLAYPAL correction.

## Validation

`tools/test_exploration_ui.py` exercises real GiveSecret calls and a real secret sector, repeated discoveries, silent/print-only flags, the native notification option, personal/level counts, save/load, full-screen and overlay maps, localization and preserved automap preferences. Test-only code changes counters and reveals geometry for screenshots; it is excluded from the distributed PK3.

Acceptance runs cover Marine at 1920×1080, Scout with German text at 1024×768 using the OpenGL backend, and Commando at 2560×1080 using Vulkan. A fresh packaged build is checked on TNT02. Existing minor-notice and native-lock regressions are also run. Saved screenshots are engine captures, with synthetic secret counts supplied by the fixture. This is targeted single-player acceptance, not a full campaign or multiplayer playthrough; sound playback is implemented from the native contract but not acoustically measured.

Evidence is in `tools/validation/exploration-ui-2026-09-08/`. Reproduction requires `UTNT_ENGINE` and `UTNT_IWAD`; use `--mod tutnt.pk3` for the packaged build and `--lang deu --class Scout --width 1024 --height 768 --renderer 0` for the German 4:3 case.

## Engine references

- [P_GiveSecret and its callback/counter ordering](https://github.com/UZDoom/UZDoom/blob/trunk/src/playsim/p_spec.cpp)
- [Native automap colors, AUTOPAGE, discovery and arrow rendering](https://github.com/UZDoom/UZDoom/blob/trunk/src/am_map.cpp)
- [Native lock requirements and map colors](https://github.com/UZDoom/UZDoom/blob/trunk/wadsrc/static/lockdefs.txt)

The shipped UZDoom 5.0.1 definitions were compared directly when creating the lock palette; upstream trunk may subsequently change.
