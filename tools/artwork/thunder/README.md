# TNT02 thunder artwork

The user approved the two-state mockup, then requested implementation with slightly blue, desaturated exterior light. The approved mockup is retained here; production source textures are `tutnt/graphics/thunder/clouds.png` and `mountains.png` (2172 × 724 each).

Created with the built-in Imagegen tool from the approved mockup and original TNT02 screenshots. Full generation and refinement prompts are in `prompts.json`. The intermediate mountain transparency attempt contained an opaque checkerboard and was rejected; the selected final asset uses a flat blue key removed before interpolation by both shader and CPU fallback generation. The source files are preserved without manual paint edits. CPU reprojection uses Pillow/NumPy in `tools/build_thunder_sky.py`.
