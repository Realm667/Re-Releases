# ENDMAP: TNT01 storm sky

ENDMAP01 uses the same USTSKY cube, cloud animation and mountain panorama as TNT01.
The map-specific sky1 binding reuses the existing materials without duplicating artwork.

In the binary THINGS lump, anonymous legacy SkyViewpoints 0, 227 and 288 become
MapSpots (9080 to 9001): three changed bytes. All other WAD bytes are unchanged.
The explicitly identified SkyViewpoint with TID 6 remains available to the finale.
Credit artwork, scrolling scripts, camera sequence and ending scripts are unchanged.

Validation: source structure comparison, incremental package update and OpenGL/Vulkan ENDMAP
starts with ten assertions each across save/load. Assertions cover sky assignment,
default sky camera removal, sector count, and the preserved named finale viewpoint.
Five credit-camera views plus camera 98 were inspected in an isolated capture fixture.
This is not a full timed end-sequence or multiplayer acceptance test.

Re-run tools/test_endmap_sky.py with --mod tutnt.pk3, --out <output directory>,
--engine <uzdoom.exe> and --iwad <DOOM2.WAD>.
Results: tools/validation/endmap-sky-2026-09-09/results.json.
Credits design mockups remain outside the game pending user approval.

Two full source builds refused publication because concurrent work changed the
project during the build. The existing package was updated only in MAPINFO, ENDMAP
and build provenance, preserving the compressed bytes of every other entry.
Package integrity and engine loading passed; both renderer/save-load checks were
repeated against this package. Full-source build consistency is not claimed.
