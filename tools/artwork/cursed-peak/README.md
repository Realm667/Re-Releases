# Cursed Peak sky artwork

The user approved the concept and `approved-mockup.png` before implementation.
The map names were explicitly corrected to TNT03A1 / TNT03A2.

Two original ImageGen outputs are retained without destructive edits in
`tutnt/graphics/cursed-peak/`: `clouds.png` and `mountains-key.png` (2172 x 724).
`prompts.json` contains the full production prompts. The reference mockup is
design provenance, not a screenshot of the implemented engine rendering.

The mountain image uses magenta above the ridge for runtime keying. Key removal,
premultiplied bilinear sampling, wrap blending, world projection, colour grading
and lighting are reproducible in `tools/cursed-material.glsl` and
`tools/build_cursed_sky.py`. There is no repainted gameplay geometry in the mod.

See `UTNT_CURSED_SKY.md` for state ownership, sector tags and engine validation.
