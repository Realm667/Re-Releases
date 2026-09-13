# Distance Blur

Implemented and hardened 13 September 2026. The global filter softens distant
world geometry and actors, including dry views. Find **Distance Blur** in
**UTNT options > Performance and presets** (localized menu heading).

- Enabled by default, independently switchable.
- Intensity: 0–100%, default 50%; zero bypasses tracing and all filter passes.
- Start distance: 128–2569 map units, default 640, with 32-unit slider steps
  and a clamped final endpoint.
- Blur grows smoothly over the next 1280 units, reaching a six-pixel sampling
  radius at maximum intensity (three pixels at default intensity).
- Reduced effects bypasses the filter. Local archived settings are
  `UTNT_distanceblur`, `UTNT_distanceblurstrength`, `UTNT_distanceblurstart`.
- Underwater optics and local heat remain independently controlled. Their
  existing sampling range and behavior are unchanged.

## Distance reconstruction

`UTNT_DistanceBlur.zc` traces a camera-aligned 24 × 19 grid out to 16384 map
units. Native traces resolve walls, floors, ceilings and traceable 3D floors,
plus actors in the blockmap, including non-solid pickups. The camera actor,
invisible actors and empty TNT1 helpers are skipped. Walls occlude actors.
Distances use the trace's travelled range, avoiding subtraction of positions
from different portal coordinate systems. Sky hits use the far range instead
of the local sky ceiling height.

Continuous surfaces use reciprocal axial-depth interpolation, then convert
back to radial distance from the camera. At large depth discontinuities,
color-guided sample weighting reduces rectangular sharp patches around near
actors. A separable Gaussian blur gates neighboring samples by depth; it no
longer preserves distant high-contrast texture detail merely because its
colors differ.

Nine band passes assemble the distance mask in scene alpha, followed by two
blur passes. Each band packs three 8-bit square-root distances per float
(exact within 24 bits) and fits the portable 128-byte uniform budget. This
costs up to 456 traces per game tic or camera change and eleven fullscreen
passes while enabled. Stationary views reuse the trace cache within a tic.

## Weapon protection and remaining limits

All passes run at `beforebloom`, before the engine draws ordinary HUD weapon
sprites. The blur therefore cannot sample those weapon pixels. HUD and menus
are also drawn later. Add-ons using 3D HUD weapon models are a remaining
exception: the engine draws those earlier.

This is still reconstructed depth, not the renderer's per-pixel depth buffer;
UZDoom 5.0.1 does not expose that buffer to custom postprocess shaders. Thin
objects, same-colored silhouettes, sprite transparency and actor collision
bounds that differ from visible artwork can still produce boundary errors.
Actors excluded from the native blockmap cannot be traced this way. Render
events update uniforms after the world pass, so fast camera/actor motion can
also produce a frame of mismatch. Exact per-pixel coverage and synchronized
depth would require engine support. The denser reconstruction improves the
existing mod-only effect without claiming those engine limits are solved.

## Validation

`python -B tools/test_distance_blur.py --mod tutnt` exercises menu controls,
32-unit steps, defaults, bounds, console clamping, reduced effects, save/load,
four menu languages and off/zero/default/maximum/distant-start comparisons
under OpenGL and Vulkan. Additional checks cover visible and invisible actors,
non-solid pickups, distant actors, wall occlusion, floor range and sky range.
Weapon image comparisons aim upward against distant scenery, including a
reduced viewport and wider FOV. Opaque weapon interiors must remain unchanged;
antialiased edges and thin animated overlay lettering are excluded from the
comparison mask. Evidence lives in `.codex/validation/distance-blur/`.

The earlier off/zero image test did not expose weapon blur because its view
placed nearby geometry behind the gun. The new upward-view regression covers
that failure directly. Environment contract tests also verify packing error,
exact float transport and the portable parameter budget. These are targeted
rendering checks, not a campaign playthrough or a performance benchmark.

OpenGL and Vulkan each passed 151 engine assertions. Both upward weapon views
had zero RGB difference inside the opaque weapon mask; off and zero intensity
were also pixel-identical. All six environment contract tests passed.
