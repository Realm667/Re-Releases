# Cursed Peak: shared winter sky for TNT03A1 / TNT03A2

Implemented from the user-approved winter mountain concept and comparison
mockup. Both maps show one fixed snow-streaked mountain panorama, with two slowly
moving cloud layers. Pearl-grey daylight fades through a localized amber sunset in the south
into charcoal blue night. A light blue-grey tint conveys cold without
the mountain source image's stronger blue cast. Existing snowfall controls a low veil over
the distant mountains. A diffuse southern sun sinks behind the mountain ridge; no moon, lightning
or stars are introduced.

## Authored daylight tags, including roofs

Lighting follows **sector tags**, independently of ceiling texture or visibility
of the sky. This deliberately includes the roofed areas called out by the user.

| Tag | Day light | Night light | TNT03A1 sectors | TNT03A2 sectors |
| --- | ---: | ---: | ---: | ---: |
| 1 | 150 | 110 | 289 | 255 |
| 2 | 150 | 110 | 5 | 0 |
| 3 | 130 | 100 | 8 | 0 |
| 19 | 150 | 110 | 1 | 1 |
| 14 | 120 | 100 | 45 | 0 |
| Total | | | 348 | 256 |

Tag 1 includes 90 roofed sectors in A1 and 159 in A2; all 45 tag-14 sectors
in A1 are roofed. Tag 19 belongs to the retired sky scene. Tags 1/2/3/19 use
the ACS fade level, fading from 255 to 90 for readable night contrast.
Tag 14 changes light and colour but receives no new fog. The existing weather
system retains ownership of fog density; its former grayscale-only discovery
also recognises these explicitly owned daylight tags. Their clear-weather density
is explicitly 32, including with `weatherfx` off; storms retain the existing
32-to-54 density curve. The same restrained cold palette is
applied to sky, mountains and fade: RGB ratios 0.94/0.975/1 by day, easing to
0.92/0.96/1 at night. The actual sector fade RGB is passed to the material;
low horizon haze and snowfall veils use that exact colour. Thus the blue hint
also exists in the map's fog and does not detach the mountains from the scene.

## One clock across the hub

The original ACS global slot **1** remains the daylight authority. The original
18,000-tic duration (about 8 min 34 s at 35 Hz) remains; night then holds.
Previously unused global slot **12** now stores the shared cloud/weather clock.
It wraps at 1,050,000 tics, a common multiple of both cloud layers and the
10,500-tic snowfall cycle. Reserve this slot for Cursed Peak.

Script 23 starts script 21, which advances the clock. The engine suspends it
with the hub snapshot. Script 22 no longer writes stale time or terminates the
updater. RETURN uses ordinary `ACS_Execute`, which is idempotent even when
several players return simultaneously; `ExecuteAlways` would duplicate the clock.
The serialized `UTNTCursedSkyHandler` presents the clock, updates the tagged
sectors, and restores snowfall phase on hub entry/return. Saving/loading keeps
the clock; freeze holds both daylight and cloud movement. The sky clock does
not advance while another map is active. A new game starts at daylight.

The material reads packed 16-bit daylight and phase, an 8-bit weather value and
the exact sector-fade RGB from the 16x4 `UCPDATA` canvas. The canvas columns
are daylight/weather (0–3), cloud phase/fade scalar (4–7), fade RGB (8–11),
integrated wind X/snow enabled (12–13), and wind Y/quality (14–15). Both map scripts supply
the fade level `255 - 165 * g_lightval / time`; the colour is derived once and
shared by sectors and material. It does not use the renderer's independent timer.
Cloud layers rotate once per 1000 and 625 seconds, while mountains stay fixed.
All six cube faces use the same world direction, projection, keyed mountain
sampling and cloud coordinates. Explicit bilinear filtering also works when
ordinary game textures use nearest filtering. A planar zenith blend avoids a
polar pinch; wrap blending closes the panorama seam.

OpenGL and Vulkan render continuous daylight and moving cloud layers. The
software renderer uses three precomputed day/dusk/night skies, with discrete
sky changes; sector light still changes continuously. The static fallbacks do
not animate cloud or storm veils.

## Map scope and reproduction

Each map's one anonymous `SkyViewpoint` becomes an inert `MapSpot`. Geometry,
sector tags, node data and other actors are unchanged. Only that TEXTMAP thing
type, the daylight SCRIPTS block and the corresponding BEHAVIOR differ. Other
map scripts remain byte-for-byte intact. New map code takes effect when starting
the updated maps; saves made with the old map version are not migrated.

Production artwork and exact generation prompts are retained under
`tutnt/graphics/cursed-peak/` and `tools/artwork/cursed-peak/`. The approved mockup
is design provenance; validation screenshots are actual engine captures.

From the repository root, with Python/Pillow/NumPy, ACC, UZDoom and DOOM2.WAD:

```text
python tools/build_cursed_sky.py
python tools/patch_cursed_maps.py
python tools/build_utnt.py --acc <acc.exe> --engine <uzdoom.exe> --iwad <DOOM2.WAD>
python tools/test_cursed_sky.py --engine <uzdoom.exe> --iwad <DOOM2.WAD> --case views --renderer 0
python tools/test_cursed_sky.py --engine <uzdoom.exe> --iwad <DOOM2.WAD> --case views --renderer 1
python tools/test_cursed_sky.py --engine <uzdoom.exe> --iwad <DOOM2.WAD> --case hub
python tools/test_cursed_sky.py --engine <uzdoom.exe> --iwad <DOOM2.WAD> --case freeze
python tools/test_cursed_coop.py --engine <uzdoom.exe> --iwad <DOOM2.WAD>
python tools/check_cursed_motion.py logs/cursed-views-0 logs/cursed-views-1
python tools/test_cursed_structure.py --before <directory-containing-pre-change-tutnt/maps>
```

The map patcher is idempotent; the package builder recompiles map ACS in its
immutable snapshot. `--mod tutnt` can check live source instead of `tutnt.pk3`.
Runtime scripts use isolated settings/saves and terminate their own test
instances. `UTNT_CursedSkySetTime` is a named ACS hook for reproducible visual
checks; normal play advances the shared clock automatically.

## Validation (2026-09-09)

UZDoom 5.0.1, OpenGL and Vulkan on NVIDIA RTX 4080:

- 44 runtime assertions per renderer: day/dusk/night, both maps, correct sky,
  retired camera, shared state, matching cold fade and light under tag-1/tag-14 roofs.
- 45 hub/save assertions: A1 -> A2 -> A1 and save/alter/load preserve the shared
  clock and cloud phase. Two freeze assertions hold both clocks.
- Actual captures inspected at normal player height, all four directions and
  the zenith. Twilight, night and storm were inspected in the engine.
- Five-second fixed-camera pixel comparison separates moving clouds from the
  stationary mountain patch. Only the shared fade level may change that patch's
  tone slightly during the sample interval.
- Structural comparison verifies unchanged gameplay geometry, nodes and
  unrelated scripts in both WADs. All 14 ACS compilation units compile.

- Two real co-op peers: identical day/cloud/weather state at all three hub
  checkpoints, with one updater per map (six assertions on each peer).

Package, software fallback and detailed results are recorded under
`tools/validation/cursed-peak-2026-09-09/`.

## Stronger horizon haze (2026-09-09)

The low sky haze now blends up to 32% of the actual sector-fade colour
(previously 12%). Its smooth vertical falloff reaches 0.65 radians elevation
(previously 0.45), softening the lower mountain slopes and the transition from
the outdoor map sectors. Upper cloud detail, the light cold-blue palette,
sector fog density and the shared ACS day/night clock remain as before.
Static fallback textures use the same haze profile. The motion check now uses
completed night, keeping the fade constant while checking moving clouds against
stationary mountains. Engine captures: `tools/validation/cursed-peak-haze-2026-09-09/`.


## Southern sunset, distant snow and glare (2026-09-09)

The hardware sky now includes two fine falling snow layers in front of the
mountain panorama. They are part of the sky material, so the engine's sky mask
clips them against buildings and other foreground geometry. Weather visibility
and quality follow the existing particle controller; low quality uses one layer.
The saved sky clock drives falling motion, with integrated controller wind
projected onto the horizontal sky tangent. Freeze holds both. Ray derivatives
avoid antialiasing spikes across the longitude seam. No SkyViewpoint is restored.

The southern world axis (Doom yaw 270 degrees) owns all sunset illumination.
The old omnidirectional rose term is gone. A small diffused sun, amber halo and
apricot cloud light build during the middle of the transition. The sun sinks
behind the keyed mountain silhouette; residual cloud light then fades into
the existing cold night. Storms and the animated cloud texture attenuate the
sun. The static software fallback includes the corresponding day/dusk/night
composition; animated distant snow and glare require hardware rendering.

`UTNTCursedSun` is a scene postprocess shader. It produces a soft warm veil,
short horizontal streak and faint lens ghosts only within an 18-degree gaze
cone. A world trace rejects roofs, walls, solid visible actors and other blocked
sky sightlines, ignoring the observing camera. The postprocess samples the
same cloud and mountain masks as the sky over five points on the solar disc.
Thus a mountain can hide the sun even though the map trace hits sky. Projection
compensates for UZDoom RenderBox's inverse pixel-stretch transform and camera
roll/FOV. Glare is disabled underwater, outside these maps, in software,
with reduced effects, zero effect quality or shader overlays switched off.
Map load/unload resets the postprocess. The HUD is not a snowfall surface.

Clear-weather fog density is now applied after both sector colour updates.
This also preserves density 32 when entering A2 with weatherfx disabled.
The existing tagged lighting, shared day/night clock and sector fade remain
authoritative, including roofed sectors.

Debug in either map's console:

```
pukename UTNT_CursedSkySetTime 0
pukename UTNT_CursedSkySetTime 10800
pukename UTNT_CursedSkySetTime 14400
pukename UTNT_CursedSkySetTime 18000
```

These select day, visible southern sun, afterglow behind the ridge, and night.
Look south and slightly upward for the sun. Time continues from the selected
value; `freeze` toggles a held scene for inspection. `UTNT_shaderoverlayswitch
false` disables glare without removing the sun; set it to `true` to restore.

Validation and actual UZDoom captures:
`tools/validation/cursed-peak-sunset-2026-09-09/`. New test entry points are
`tools/test_sunset.py` and `tools/check_sunset_images.py`; the established
`tools/test_cursed_sky.py` and `tools/check_cursed_motion.py` cover the shared
clock, tagged lighting and stationary mountains.

Projection reference: UZDoom's `FSkyVertexBuffer::RenderBox` in
https://github.com/UZDoom/UZDoom/blob/trunk/src/common/rendering/hwrenderer/data/hw_skydome.cpp
and the native LineTracer interface in
https://github.com/UZDoom/UZDoom/blob/trunk/wadsrc/static/zscript/doombase.zs.
