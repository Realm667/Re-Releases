# Quake-Reliquiar validation — 2026-09-10

Approved option 01 implemented as native ZScript and generated frame textures.
All 65 original attributions remain unchanged; the empty Remaster template ships
without test names. The existing ENDMAP WAD, finale and TNT01 sky adaptation are unchanged.

## Runtime checks

UZDoom 5.0.1, DOOM2.WAD. Every result JSON reports success.

| Suite | Input | Verified |
| --- | --- | --- |
| wide-final | Source, 1272 × 696 window | All 25 original cards, font, bounds and spacing; 113 assertions |
| animation | Source, 1280 × 720 | Stagger, slide, entry and save/load during entrance; 12 assertions |
| remaster-final | Source plus isolated fixture, 1280 × 720 | Conditional chapter after thanks, pagination, chapter save/load, natural progression and finale; 35 assertions |
| package-classic | Full shared candidate, 960 × 720 | All 25 cards, dense and explicit multiline names; 113 assertions |
| package-regression | Full shared candidate, 1280 × 720 | Next/debounce, card save/load, finale and THE END save/load; 39 assertions |
| package-coop | Full shared candidate, two real clients | Guest input ignored, host next/skip synchronized; 24 assertions per client |

The early wide source run used a slightly smaller client area due to Windows DPI.
The runner now produces exact 1280 × 720 / 960 × 720 client areas. Animation preceded
only the Remaster category-label correction; later source and package checks include it.
Remaster screenshots contain test-only names from the fixture, absent in the shipped data.

## Build and scope

`package.json` records the full shared-worktree candidate, including concurrent local
integration work, all 14 compiled ACS sources and the engine compile check. The PK3
is an ignored local artifact and is not committed. At validation time the user's
running TNTLE game held the common `tutnt.pk3` open, so the new package was built as
`credits-reliquiar/final-credits.pk3` in the task output directory. It was not possible
to replace the common package while that instance remained open.

Representative native engine screenshots are in `screens`. Tests ran without audio;
they do not constitute subjective audio review, a full campaign run or migration
testing of saves made with the previous version. Enter ENDMAP afresh for new data.
