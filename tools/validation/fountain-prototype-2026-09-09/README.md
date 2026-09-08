# Fountain motion prototype validation

OpenGL: 15 runtime assertions passed. Vulkan stalled at startup before the test scene and timed out; its visual/runtime behavior remains unverified. Checked missile speed,
gravity and dimensions, all three breakup stages, wake lifetimes and scales,
activation, cleanup, save/load and switching back from the original fountain.
The 64-frame motion.gif is encoded from actual OpenGL screenshots, sampled
every two game tics. No painted mockup or postprocessed water was substituted.
The GIF palette is fixed across frames to prevent quantization flicker.
Only the separate tools/fountain-prototype add-on is changed; campaign effects
are not replaced. This is a prototype for visual approval, not a final rollout.
