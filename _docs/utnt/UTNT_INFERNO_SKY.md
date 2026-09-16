# TNT04B inferno sky

Implemented 17 September 2026 for the second, floating-island area.

The dedicated fire viewpoint (TID 3) now surrounds both island rooms with orange/gold flame fronts, dark smoke, distant basalt silhouettes and lava falls. A separate overhead fire ceiling and lower magma field cover steep viewing angles. Slow cloud drift and restrained flame/lava brightness variation keep the fire alive. The original first-area ash sky and the four connecting portal viewpoints are preserved.

The lower island sides receive local, nonblocking ember haze with world-space turbulence and soft edges. The effect stays below the playable tops. The original brick/rock textures, routes, actors, void floors and tower remain intact. The haze is authored as 83 editable map Things covering 338 boundary segments across the two rooms; it survives save/load and does not modify collision. Sky-room sectors use special 90 to exclude ambient occlusion.

## Editable production assets

All final resources are in `tutnt/`: `maps/tnt04b.wad`, `graphics/inferno/`, `textures/UFI*.png`, `models/inferno/`, `shaders/inferno/`, `zscript/UTNT_Inferno.zc`, and the inferno definition modules. The map contains the final compiled BEHAVIOR alongside SCRIPTS. Neither `.codex/` nor a package-only map edit is required.

Normal packaging must preserve these authored resources. `tools/build_inferno_sky.py` explicitly regenerates the six fallback faces and sky material from the three editable artwork images and `tools/inferno-material.glsl`. It is not part of normal packaging. `tools/author_inferno_sky.py` and `tools/author_inferno_haze.py` are historical one-time authoring steps; they refuse an already authored map. Edit final Things, models, room textures and materials directly in UDB or the source files. Rebuild generated definition tables after changing their source modules.

Generated-art prompts are recorded in `tools/artwork/inferno/prompts.json`. The live shader samples the three RGB images with explicit bilinear filtering, preserving smooth distant imagery even when sprites use nearest filtering. The sky material is fullbright to avoid directional wall shading at cube seams; other map actors keep their lighting. The static six-face fallback remains available without custom material shaders.

## Validation

`tools/test_inferno.py --engine <uzdoom.exe> --iwad <DOOM2.WAD>` checks structural counts, map-owned haze placement, the fire camera, both original void floors, sky sector specials, and save/load. It accepts `--renderer 0` for OpenGL and `--mod <package>` for packaged validation. Visual views cover four horizontal directions, both island rooms, above, below and the connecting portal.

A baseline comparison confirms unchanged vertices, all 1,293 original Things, and unchanged BSP/other map lumps. Only two sky-room sectors, eight enclosing lines and 80 sky-room sides change; 83 cosmetic Things are appended. Three obsolete sky scale/fog ACS calls are removed and the map script recompiled.

The existing package pipeline omits non-runtime definition source modules and source artwork metadata and adds build metadata and MAPINFO precache lists. Those are pre-existing source/package differences; inferno artwork, map, models, scripts and materials must match their editable production files byte for byte.
