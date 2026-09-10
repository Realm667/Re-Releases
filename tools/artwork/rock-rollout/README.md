# Expanded QROCK materials

QROCK1X8, QROCK4X8 and QROCK5X8 were generated with the built-in image generation
tool from losslessly decoded original patches, shown at native scale in an
8x8 tiled reference field. The author reviewed the variants without requiring
another user approval, as expressly requested for this rollout.

Final assets: tutnt/patches/area-expanded/QROCK1X8.png, QROCK4X8.png, QROCK5X8.png. They are
unchanged 1254x1254 imagegen outputs; TEXTURES scale 1.224609375 and WorldPanning
make their physical repeat 1024x1024. The approved QROCK3X8 remains unchanged.

prompts.json contains the complete prompts. source-manifest.json identifies the
source patches and palette. texture-checks.json records image hashes, luminance
and edge statistics. These measurements supplement visual wrap review and do
not prove perfect continuity of individual rock contours at the tile edges.

manifest.json records every selected map/line/side/tier, original values,
new values, mapping context and deliberate closed-loop corner cuts. validation.json
independently verifies the frozen candidates. skybox-preservation.json verifies
the delta replay onto the newer live maps, including the TNT04B skybox.
