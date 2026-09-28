# TNT02 Mario secret CRT view

The Super Mario secret in TNT02 uses a local CRT postprocess on the world
scene. The effect turns on when the player's view enters the isolated Mario
cluster and turns off when the player teleports back, changes maps, or leaves
the gameplay view. HUD and menus render after the scene pass.

## Source and adaptation

The filter ports the complete visual vocabulary of Timothy Lottes'
[public-domain CRT scan-line shader](https://github.com/libretro/glsl-shaders/blob/master/crt/shaders/crt-lottes.glsl):
curvature, Gaussian scanlines and pixel sampling, an RGB shadow mask and
phosphor spread. Libretro's vertex/preset uniforms were replaced by UZDoom's
`InputTexture`, `TexCoord` and scene pass. The sampling grid is capped at
640 columns and follows the player's aspect ratio; this preserves widescreen
play and keeps the original Mario artwork readable. The port uses a lighter
bloom kernel, gentle curvature and an even, low-contrast vignette along all
four edges without black corner cutouts for the 3D scene.
It has no film noise or disruptive flicker.

The authored map contains 310 Mario-textured sectors inside the selected
coordinate window (`-8500 < x < -3500`, `-1100 < y < 2500`), with no
regular TNT02 sector center in that window. The handler additionally checks
the camera sector for an `SM_` floor or ceiling texture and requires
`TNT02` and the locally rendered camera. In multiplayer, each client evaluates its own
view independently; no effect state is replicated. No map geometry, teleporter, actor,
texture, savegame state or network gameplay is changed.

Production files: [shader](../../tutnt/shaders/crt/mario-view.fp),
[GLDEFS binding](../../tutnt/gldefs/GLDEFS.mario-crt),
[view handler](../../tutnt/zscript/UTNT_MarioCRT.zc). The conceptual
mockup is local at `tutnt/.codex/work/tnt02-mario-crt/mario-crt-mockup-v2.png`.
It was generated from an actual TNT02 screenshot and is an art direction
preview, not a captured engine result. ImageGen edit prompt: preserve all
game objects and composition; apply restrained curved CRT glass, horizontal
scanlines, RGB phosphor fringes, mild glow and a weak, even vignette along all four edges without black corners.

## Verification

Validated with UZDoom 5.0.1 on 28 September 2026. The full UTNT
`--check-only` build passed without stale ACS or generated tables.
The isolated test package at
`tutnt/.codex/builds/tutnt-mario-crt.pk3` loaded TNT02. Vulkan captures
show the CRT treatment in the Mario scene, its removal when the local
camera leaves the secret, and its restoration on reentry and save/load.
Two real cooperative clients ran simultaneously with the final package:
player 0 viewed the Mario secret with CRT, while player 1 saw a normal
TNT02 scene without the CRT treatment. Both reached their completion
markers without script errors, consistency failures or out-of-sync
messages. OpenGL rendered the final shader successfully on a small
TNT02 test sector with `SM_GRAS` under
`tutnt/.codex/work/tnt02-mario-crt/opengl-fixture/`. Logs and captures
are under `tutnt/.codex/logs/mario-crt-*`; the cooperative summary is
`tutnt/.codex/validation/mario-crt/coop.json`.

The test used controlled camera positions rather than walking both
teleporter lines. Full-map OpenGL did not reach the screenshot within
the 120-second test limit, although it initialized without errors;
additional resolutions and live teleporter crossings remain visual
review cases. The production shader, GLDEFS
binding and ZScript handler are byte-identical inside the test package.
The package's MAPINFO is intentionally expanded by the existing
packager, so the source MAPINFO file is not byte-identical to that lump.
The editable sources under `tutnt/` remain authoritative.

The required layout checker reports 15 editor `.dbs`, backup and autosave
files already present in `tutnt/maps/` before this task. None was created
or moved by this change.
