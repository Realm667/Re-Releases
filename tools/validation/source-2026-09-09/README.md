# Source acceptance — 2026-09-09

All recorded runs use the isolated candidate PK3 containing master plus only the
Source change. OpenGL and Vulkan each pass 75 assertions, including genuine
guardian death, real attack scripts, save/load, zero/reduced FX and map isolation.
Two local network peers use opposing FX settings. Their per-peer assertion counts
and completion status are in coop/runtime.json. Raw logs and selected real engine
captures are included. Failed exploratory runs and unrelated portal intermediate
changes are excluded from this acceptance record.

All original geometry, map nodes, monster states, delays, random calls and rune
assets pass the baseline comparison in structure.json. The only map script edit
is the cosmetic shield-impact notification. The candidate-build record covers all
14 ACS modules and the packaged material files. Its temporary build root has no
Git checkout; tested_game_tree in summary.json identifies the exact candidate.
The final committed package is rebuilt with the final Git provenance.

This is local engine/loopback validation, not WAN or a full manual playthrough.
