# Distance Blur

Implemented 13 September 2026. The global scene filter extends the existing
underwater blur technique to every map and to dry views. Find **Distance Blur**
in **UTNT options > Performance and presets** (localized menu heading).

- Enabled by default, independently switchable.
- Intensity: 0–100%, default 50%; zero bypasses both tracing and the shader.
- Start distance: 128–2569 map units, default 640, adjustable in single units.
- Blur grows smoothly over the next 1280 units, reaching a six-pixel sampling
  radius at maximum intensity (three pixels at the default intensity).
- Reduced effects bypasses the filter. Settings are local archived user CVARs:
  `UTNT_distanceblur`, `UTNT_distanceblurstrength`, `UTNT_distanceblurstart`.
- Underwater tint, blur and distortion remain independently controlled and may
  combine with the global filter. Existing underwater and heat ranges stay 2048.

## Rendering and limits

The [scene postprocess](https://zdoom.org/w/index.php?title=GLDEFS) samples the rendered world, including actor colors, before
HUD/menu rendering. It adds no tint. The existing color-sensitive nine-tap filter
reduces smearing across strong silhouettes. Sampling stays within the view window.

Like the underwater effect, this uses an approximate 8 x 4 camera-aligned static
geometry ray grid, not native per-pixel scene depth. Actor distance and silhouettes,
thin obstacles, portals and stacked geometry cannot be resolved exactly; a nearby
actor against a distant wall can receive blur. The independent cache extends the
trace range to 8192 units so the full start-distance slider remains useful. At most
32 extra traces run per update (game tic or camera motion), only while enabled.
Six-bit square-root distance packing fits exactly in floats. The shader uses seven
uniform slots, within the portable 128-byte parameter budget.

## Validation

`python -B tools/test_distance_blur.py` checks real menu interaction, defaults,
limits, out-of-range console settings, reduced effects, save/load, four menu
languages and rendered off/zero/default/maximum/distant-start comparisons on
OpenGL and Vulkan. Evidence stays in `tutnt/.codex/validation/distance-blur/`.
The shared environment tests cover underwater and local heat behavior.

Initial source tests passed 143 engine assertions per renderer (286 total),
including pixel-identical off/zero images. The German menu and scene comparison
were visually reviewed. Environment packing/budget tests and all 14 localization
unit tests passed. This is targeted rendering validation, not a campaign playthrough.
The existing underwater/environment runtime fixture also passed 20 assertions
with global Distance Blur enabled. HUD pixels in the comparison remained identical.
