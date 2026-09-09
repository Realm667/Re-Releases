# Credits validation, 2026-09-09

Latest Quake SMALLFONT layout: all 25 cards checked at 1280x720/OpenGL and
960x720/Vulkan, including actual SMALLFONT identity and vertical spacing.
These layout checks use an immutable integration baseline with the current
credit resources overlaid. Screenshots were visually inspected.

Full shared-source package b75ec30dc525: native compilation, save/load during
credits and THE END, host skip, exactly-once finale, empty Remaster block,
filled Remaster block with automatic pagination, and two actual co-op peers
passed. All 14 ACS modules were current. The only changed ENDMAP lumps relative
to the approved sky adaptation are SCRIPTS and BEHAVIOR; scripts 51/52/102 retain
their contents. Test fixture names in 05b are demonstration data only and are
not included in the release credits.

Earlier checks also exercised natural timeout into the complete authored finale.
They preceded the final supporting-font change. Sound was disabled in automation.
This does not claim subjective audio review, old-version save migration, a full
campaign playthrough or an uninterrupted five-minute credits run.

Two restricted OpenGL launches stalled at engine initialization; the normal
permission run completed all layout checks. One build refused publication when
parallel work changed its inputs. A separate concurrent build replaced a later
package with an older revision; the final shared-source rebuild was then copied
under the build lock and validated by exact package hash. The retained logs
and results describe successful final checks, not those superseded attempts.
