# Continuous ending panorama

Updated: 13 September 2026.

The ending uses a single continuous painting based on the supplied Remaster
I_10B scene: a dark fractured planet with a glowing amber fissure, cool upper
atmosphere and a starfield continuing to the right. The small original
THE END inscription stays at the lower left.

The two opaque RGBA PNGs in tutnt/hires/graphics/interms/ are:

- TNTND02.png: LEFT half, 1280 x 960 pixels.
- TNTND01.png: RIGHT half, 1280 x 960 pixels.

Generate and resize the complete panorama to 2560 x 960 first. Split at x=1280
without overlap, padding or further resampling. Never generate, scale, sharpen
or color-correct the halves independently: concatenating D02 then D01 must
reproduce the panorama pixel for pixel. The outer edges do not wrap.

The original low-resolution resources remain unchanged. The built-in Imagegen
prompt and complete master are retained locally under
tutnt/.codex/work/border-and-ending/. Previous hires files are backed up under
tutnt/.codex/backups/ending-panorama-20260913/.

Validation checks the two export sizes, full opacity and exact pixel
reconstruction. Results: tutnt/.codex/validation/border-and-ending.json.
The full panorama was visually inspected for continuous atmosphere and detail
across the join. This does not change the ending timing or scroll logic.
