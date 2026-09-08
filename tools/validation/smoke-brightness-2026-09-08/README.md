# Darker smoke, 2026-09-08

The visible smoke material now interpolates from a darker warm-gray shadow
(0.20, 0.18, 0.16) to neutral (0.60, 0.60, 0.60), equivalent to #999999.
Clamping the interpolation input bounds every material RGB channel at 0.60.
Screen gamma, bloom and the background may affect the final composed pixel.

Only shaders/fire-smoke.fp changes in the installed package, verified by
comparing every archive entry. The density atlas, alpha calculation, four
smoke shapes, distortion/filtering, actors, sizes, motion, glow, flames and
sparks are unchanged. The color change applies to every existing smoke user,
including torch variants, barrels and all FireSpawner sizes.

Four isolated engine runs cover the torch and FireSpawner fixtures on OpenGL
and Vulkan. All 16 runtime assertions pass; screenshots verify the rendered
effect. No new lifecycle tests or gameplay changes were needed for this
material-only adjustment. Exact package/source hashes are in results.json.
