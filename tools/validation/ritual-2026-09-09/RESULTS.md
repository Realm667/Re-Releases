# UTNT ritual materials — 2026-09-09

Approved warm amber portal reference, retaining original TNT03B QRUNT63 glyphs.
User's final correction: orange frame and airborne runes, unchanged portal/pad colors.

- UZDoom 5.0.1, hardware renderer: 15 passing runtime cases, 768 assertions.
- TNT01 detailed regression in OpenGL and Vulkan: all 14 QSLIP/QSLIPP frames,
  scripted replacements, saved/restored UVs, explicit script UV edits, original
  rune sprite identity, activation/deactivation and quality-off cleanup.
- Teleporter discovery and visible rune emission in all eight red-source maps.
- Static scan: all 28 QSLIP/QSLIPP floor sectors fit the supported bounds;
  no matching campaign floor was skipped.
- Portal suction: both decoration sizes, proximity, options, activation, save/load,
  occlusion; TNT03B, TNT04A and TNT04B campaign cases.
- Direct TNT03B noclip/fly approach and local effects, including save/load.
- Inspected actual TNT03B and TNT01 screenshots; frame/airborne runes are orange,
  floor and portal surfaces retain their earlier warm amber/gold appearance.

The first OpenGL launch timed out before entering a map. A later complete OpenGL
run passed (initial startup remains slow on this machine). One parallel Vulkan
launch also timed out before map entry; final campaign runs were sequential and
passed. No test game/editor belonging to the user was terminated.

The screenshots also show unrelated work present in the shared checkout. Those
changes are not part of this patch. Software rendering and network multiplayer
were not exercised in this pass. Existing non-red teleporter classes retain their
original emission path; optional particle/postprocess settings preserve materials.
