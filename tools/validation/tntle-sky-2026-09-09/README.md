# TNTLE sky validation, 2026-09-09

Both complete ten-assertion runtime suites use the built PK3 in UZDoom 5.0.1,
renderer 0 OpenGL / renderer 1 Vulkan, 1920x1080 on an NVIDIA RTX 4080.
Result JSONs and full logs document map layout, freeze and save restoration.
`structure.json` compares every original map block and recompiles ACS.
Both logs retain all 7597 area bindings with zero failures.

`*-motion.json` measures downward lava motion against stationary/upward
translation and a separate stationary-rock control, cloud change over five
seconds, and the reduced-effect setting at fixed game time. Corresponding
screenshots can be reproduced with `tools/test_tntle_sky.py`. The fixture waits
one second after view changes before measuring; earlier exploratory captures
could still show the previous camera and are deliberately not this evidence.

Included PNGs are actual Vulkan screenshots: 0/1 cavern gameplay/upward,
2/3 ember-night gameplay/upward, 8 cavern zenith, 14 cloud zenith, 16 secret area.
These are separate from the approved illustrative mockups in the artwork folder.

`package.json` identifies the exact full working-tree package used here. The
build includes the pre-existing local edits from other tasks, while the TNTLE
commit contains only TNTLE changes. Package identity predates the documentation
commit. Sources and the package were verified to contain identical owned assets.
