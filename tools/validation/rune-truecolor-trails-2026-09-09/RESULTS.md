# Truecolor runes and slower trails — 2026-09-09

UZDoom 5.0.1: 7 passing runtime cases / 1645 assertions.

- OpenGL and Vulkan, TNT03B portal and TNT01 teleporter: three owned trail
  segments for every rune, visible low-opacity ribbons, slower flight lifetime,
  gradual fade-in, save/load and complete cleanup with effects disabled.
- Existing Vulkan portal tests: both decoration sizes, proximity options,
  activation/deactivation, save/load and wall occlusion.
- Existing TNT01 ritual tests: texture animation frames, scripted replacements,
  UV restoration, activation/deactivation and effect quality settings.
- Actual screenshots inspected: orange glyph outlines and warmer hot cores,
  unchanged original rune silhouettes and stone frame, subtle short ribbons.
- RGBA PNG conversion asserts native dimensions, identical alpha, unchanged
  non-rune pixels, and PNG color type 6. Conversion report records source and
  palette hashes plus colors outside the original palette (220 frame / 135 glyph).
- Fixed-size history and three reused ribbons per rune keep effects bounded;
  no continuous spawning of trail particles. Emission density is compensated
  for the doubled lifetimes. The pad light is refreshed before emission thinning.

Original LMP inputs and the captured first PLAYPAL palette are archived under
tools/artwork/portal-runes/source. No generated rune shapes or palette quantization.
The separate masks preserve the existing portal/pad seal color treatment.

The shared project's newly added CanvasTexture directive initially prevented
startup when placed immediately after a Texture/pic animation. An isolated
engine probe accepted that directive; placing it before animation blocks fixes
the integration without changing animation timing or the unrelated lava edits.

OpenGL's first material startup was slow (about 70–75 seconds per case), but all
tests reached completion. Vulkan cases took about 17 seconds. Multiplayer and
software rendering were not exercised. Screenshots include unrelated shared work.
