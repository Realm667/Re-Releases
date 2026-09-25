# TNT04B inferno sky

Implemented 17 September 2026 for the second, floating-island area.

The dedicated fire viewpoint (TID 3) now surrounds both island rooms with orange/gold flame fronts, dark smoke, distant basalt silhouettes and lava falls. A separate overhead fire ceiling and lower magma field cover steep viewing angles. Slow cloud drift and restrained flame/lava brightness variation keep the fire alive. The original first-area ash sky and the four connecting portal viewpoints are preserved.

The lower island sides now fade transparently into the fire landscape. A render-only Transfer_Heights controller truncates opaque lower walls at Z=-128; 83 matching, lit wall models continue the original HOTROCK/HOTSTONE textures down to Z=-224 and fade out in world space. Their eight-unit upper overlap hides the join, while a gently uneven alpha boundary avoids a ruler-straight silhouette. The 83 existing ember-haze contours provide a second, wider transition. Together they cover 338 island boundary segments, including the brick platforms.

The physical void floors remain at Z=-224, with original damage, collision, island heights and actors preserved. The controller uses flags 34 (fake floor only, no transferred lighting), retains the original sector tag 255 and adds the dedicated visual tag 64123. The control sector and all cosmetic Things are editable in the source map; compiled nodes include the appended geometry. Sky-room sectors retain special 90 to exclude ambient occlusion.

Both island rooms and the tower surroundings use the requested #F2C9AF ambient color, preserving their original light levels. The 25 September 2026 correction also covers all exterior sectors explicitly assigned to the fire viewpoint (TID 3), including eleven previously neutral sectors outside the original island-room bounds. There are 71 authored ember sources: 63 among the islands and eight smaller, slower sources around the fire sky camera. Twenty world sources carry local orange dynamic lights with independently phased fluctuations in both brightness and radius. Short-lived cinders rise and drift; the existing effects quality setting controls their density. Serialized sources and lights resume after save/load.

## Editable production assets

All final resources are in `tutnt/`: `maps/tnt04b.wad`, `graphics/inferno/`, `textures/UFI*.png`, `models/inferno/`, `shaders/inferno/`, `zscript/UTNT_Inferno.zc`, `zscript/UTNT_InfernoAtmosphere.zc`, and the inferno definition modules. The map contains the final compiled BEHAVIOR alongside SCRIPTS. Neither `.codex/` nor a package-only map edit is required.

Normal packaging must preserve these authored resources. `tools/build_inferno_sky.py` explicitly regenerates the six fallback faces and sky material from the three editable artwork images and `tools/inferno-material.glsl`. It is not part of normal packaging. `tools/author_inferno_sky.py`, `tools/author_inferno_haze.py` and `tools/author_inferno_finish.py` are historical one-time authoring steps; they refuse an already authored map. Edit final Things, models, room textures and materials directly in UDB or the source files. Rebuild generated definition tables after changing their source modules.

Generated-art prompts are recorded in `tools/artwork/inferno/prompts.json`. The live shader samples the three RGB images with explicit bilinear filtering, preserving smooth distant imagery even when sprites use nearest filtering. The sky material is fullbright to avoid directional wall shading at cube seams; other map actors keep their lighting. The static six-face fallback remains available without custom material shaders.

## Validation

`tools/test_inferno.py --engine <uzdoom.exe> --iwad <DOOM2.WAD>` checks structural counts, map-owned haze and alpha-band placement, active cinder sources, changing light radii, ambient color, render-only floors, the fire camera, both original physical void floors, sky sector specials, and save/load. It accepts `--renderer 0` for OpenGL and `--mod <package>` for packaged validation. Visual views cover four horizontal directions, both island rooms, above, below and the connecting portal.

The original inferno authoring retained all 1,293 original Things and removed three obsolete sky scale/fog ACS calls. The atmosphere follow-up preserves all previous 1,376 Things, all previous vertices/lines/sides, and identical SCRIPTS/BEHAVIOR. It appends four control vertices, four lines, four sides, one control sector and 154 cosmetic Things; 379 existing sectors receive the warm tint and only the two void sectors receive the extra visual tag. Heat-source volumes and movement bindings remain unchanged. Nodes are rebuilt without altering authored TEXTMAP indices or values.

In-game validation covers Vulkan and OpenGL, save/load, close rock transitions, distant brick platforms and the tower. Material shaders provide the true alpha fade; the model skins remain based on the original map textures. This change does not modify engine source.

The existing package pipeline omits non-runtime definition source modules and source artwork metadata and adds build metadata and MAPINFO precache lists. Those are pre-existing source/package differences; inferno artwork, map, models, scripts and materials must match their editable production files byte for byte.
