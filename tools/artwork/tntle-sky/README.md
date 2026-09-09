# TNTLE sky artwork

Four approved mockups and four new ImageGen source textures, 2026-09-09.
Mockups are art-direction references, not actual engine screenshots.
Sources under `tutnt/graphics/tntle` are unchanged generated outputs:
three panoramas at 1774x887 and the cavern vault at 1254x1254.
`prompts.json` records the actual generation prompts and reference names;
requested resolution in a prompt is not the returned resolution.
`manifest.json` identifies source/derived files by SHA-256.

`tools/build_tntle_sky.py` derives the premultiplied mountain matte, RGB
lava/haze masks and twelve 1024x1024 static cube faces using Pillow/NumPy.
It also assembles the two shader programs from `tools/tntle-*.glsl`.
Runtime validation screenshots are under `tools/validation/tntle-sky-2026-09-09`.
