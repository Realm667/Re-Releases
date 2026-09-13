# Scene brightness

UTNT Options > Performance and presets provides a local brightness filter with separate Shadows,
Midtones and Highlights sliders. Defaults are enabled, +30%, +15% and 0%.
Each slider runs from -100% to +100% in five-percentage-point steps. Negative values
darken that tonal range. Disable the filter, or set all three sliders to zero,
to restore the original image. Changes preview immediately, including while the
menu pauses the game. Visual presets do not overwrite these preferences.
Existing saved preferences are retained when the defaults change.

The final `scene` postprocessing pass grades the composed world, including skies,
fog, effects and the weapon view, before the HUD, menu and credit text. It also
applies to cutscene camera views. This needs hardware postprocessing support.
No map light values, ACS scripts, sector controllers, gameplay state or engine
gamma settings are changed. Settings belong to the local player and are read
again after loading or changing maps; the filter never accumulates adjustments.

## Tonal response

Rec.709 luminance selects overlapping tonal weights. Shadows fade into midtones
between 0.00 and 0.50; midtones fade into highlights between 0.50 and 1.00.
The three weights sum to one. The slider percentages control the weighted gain,
not a promised percentage increase in perceived screen brightness.

For strongest RGB channel `p` and weighted control `g`, the exposure is `2^g`
and all RGB channels are scaled by `exposure / (1 + p*(exposure - 1))`.
At -100% the exposure is 0.5; at +100% it is 2.0, before the soft shoulder.
This wider-range response replaces the initial linear gain, which would divide
by zero at white with -100%. Exposure and the denominator stay strictly positive.
The response remains monotonic across the grayscale range, including mixed
extreme controls; RGB ratios, pure black, white and alpha are preserved.

Both UI and shader clamp controls to [-1, 1] after percentage conversion, even
when console values exceed the menu range. Zero settings bypass the pass
entirely. One scene sample per pixel; no depth buffer, history, random numbers
or sector traversal is required.

Implementation: `tutnt/zscript/UTNT_TonalFilter.zc`,
`tutnt/shaders/tonal-filter.fp`, and the `CVARINFO.tonal`, `GLDEFS.tonal` and
`LANGUAGE.tonal` modules. Translations live in the three standard catalogs.

## Validation (13 September 2026)

UZDoom 5.0.1 passed 99 Vulkan runtime assertions covering the ten gameplay maps,
INTERMAP and ENDMAP01, including the initial defaults, slider bounds and one-point changes,
console clamping, toggling, save/load and Cursed Peak hub return. The same
63-assertion control/save/load sequence also passed under OpenGL. Image checks
confirmed ordered dark/original/default/bright output, pixel-identical static
masonry at zero and unchanged opaque HUD labels across the tested strengths.
The broad tonal transitions were checked for monotonic grayscale response at all
27 combinations of minimum, zero and maximum controls.

All four language menus passed 988 engine assertions, plus the 14 localization
unit tests and definition/font checks. The isolated PK3 passed compilation and
its ACS bytecode matched the source. This is targeted runtime and visual coverage,
not a full campaign playthrough or a multiplayer soak test.

The shared integration package `b125352663ea` also contains the exact filter
sources and passed all 63 control/save/load assertions and the image comparisons,
alongside the current Distance Blur and other local integration work.

The follow-up defaults of +30% shadows and +15% midtones, with five-point menu
steps for all three controls, passed all 63 runtime assertions and the image
comparisons. Evidence: `tutnt/.codex/validation/tonal-filter/defaults-30-15/`.

The extended -100% to +100% range passed 63 assertions and the image comparisons
under both Vulkan and OpenGL. The shared integration build `adba34c87004` passed
engine compilation and contains this revision. A numerical sweep of all 68,921
five-point control combinations at 1,025 gray samples each confirmed finite,
bounded, monotonic output and preserved black/white endpoints; the denominator
never fell below 0.5. Evidence: `range-100-vulkan/` (including `curve-check.json`)
and `range-100-opengl/` beneath the same validation directory.

Local evidence: `tutnt/.codex/validation/tonal-filter/` (`package`, `opengl`,
`options-package`, `integration`). Reproduce with `tools/test_tonal_filter.py` and
`tools/test_options_menu.py`, specifying the engine, PK3 and central output paths.
