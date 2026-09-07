# Objective completion validation — 2026-09-08

All 21 goals across ten campaign maps/nine objective groups are covered by
authored ACS triggers, boss deaths and exit adapters. Source checks exercise
English/Vulkan, German/OpenGL, the Mastermind consequence, exact saved timelines,
duplicate suppression, FIFO snapshots and an actual A1 -> A2 -> A1 hub roundtrip.

Final live PK3: German three-goal completion and all-nine-layout 1024x768 checks,
plus 16 black/white pixel comparisons of the existing full-plaque cap joins.
The preceding package also passed the 75-assertion O/fire/fade suite and TNT01
completion/save/load suite. The final change only raised the footer five logical
units and allowed the completion toast while O is held on non-objective maps.
The saved screenshots before this final spacing adjustment retain their role
as trigger evidence; the German TNT02 and 1024x768 images show the final footer.

The layout runner's default window border assumption (18x47) was insufficient
on this desktop. A local wrapper adds 8x24 to its window request; the suite then
verifies the PNG is exactly 1024x768. Gameplay settings and saves remain isolated.

The structural contract report compares against 6bf2e7ae3 and permits only the
six documented exit-linedef wrappers; all other geometry and node lumps match.
The build report confirms all 14 ACS modules have current bytecode and the live
PK3 passes the engine startup check. summary.json records objective-file hashes,
package hash and scope limitations. Test addons are outside the game package.
