# Compact objectives acceptance — 2026-09-07

Four passing UZDoom cases, 354 assertions: German 4:3 and English Full HD layouts
cover all nine episodes; the TNTLE controls cases cover both languages and
Vulkan/OpenGL. The English layout and both controls cases use the built PK3.
All 14 ACS modules compile with no stale bytecode. The archive integrity and
engine load checks pass. Exact build/source/artwork hashes are in results.json.

The six TNTLE screenshots show actual automatic/manual/release/expiry/menu
behavior. Layout previews draw synthetic episodes over TNT01, so those two
screenshots deliberately contain both views. Actual gameplay selects one view.
Tests grant invulnerability only in the test addon, to allow repeatable combat
checks; they verify ammo consumption and advancing simulation in both views.
Frame-end screenshot capture is allowed to finish before changing a view.

The RGB art is unchanged. Native clips remove its outside black matte, and
separate translucent shadow rectangles retain opaque interior metal.

The live package also contains the checkout's independent ongoing work; that
work is excluded from this Objectives commit. No existing player config/save
was changed. Real ACS dispatch was already covered by the prior acceptance;
this revision does not change ACS or map data. The updated map-start regression
remains available but was not rerun. No full campaign/multiplayer certification.
