# Environmental presentation

Updated 2026-09-11 after visual review. Four options remain under UTNT options >
Environment details, localized in English, German, Spanish and French.
The local lava heat experiment remains a separate, opt-in test addon.

## Current behavior

- **Rain-wet surfaces:** 3,178 candidate floor/wall faces in TNT02 retain their
  original texture scale, area alignment and terrain. Runtime rain-direction
  traces account for roofs and solid 3D floors. Wetness builds and dries gradually; light rain also develops a visible film.
  The wet reflection layer smooths coarse material normals without removing relief.
  Damp stone darkens, with irregular, angle-dependent blue-grey sky sheen and
  increased material specular response. Two-sided middle textures can participate.
  The state canvas's inverted GPU Y coordinate is now handled correctly.
  The combined relief shader fingerprints its includes to invalidate stale GPU programs.
  The sky sheen is an approximation, **not a reflected image of map objects**.
- **Underwater:** water level 3 enables mild general blur plus stronger blur with
  increasing estimated viewing distance. Water, slime and blood retain different
  tints. The existing underwater distortion is separate. Reduced effects disables
  this additional treatment.
- **Caustics:** slow, world-anchored cellular light patterns on eligible shallow
  water beds, lower/middle walls and the visible water plane. Wall reflections fade
  out within 24 map units above the waterline. The water skin receives a weaker
  contribution than the bed. Existing liquid shaders are preserved. TNT03A2 has
  twelve bindings, including its water-control ceiling.
- **Footprints:** the approved alternating snow and wet sole marks remain.
  Support checks, moving floors/3D-floor tops, budgets (32/80/160) and lifetimes
  (wet up to 7 s, snow up to 30 s) are retained.
- **Mechanisms:** watchers discover ordinary movement actions and literal ACS tags,
  then react to actual movement and a completed stop after meaningful travel.
  Dust is distributed across a jittered sector grid, rejecting other sectors and
  holes. A sector gets up to 16/36/64 puffs by quality. A soft RGBA sprite with a
  bottom pivot replaces the black-edged smoke patch; particles remain above a
  rising floor and disappear if the available space closes.
- **Scenic lighting removed:** the added accent lights, light shafts, lava-edge
  lamps, generated placement tables, shader, CVar and all four menu translations
  have been removed. Original map lighting and other existing effects remain.

No production WAD geometry is rewritten. Scripted texture replacements take
precedence over environmental aliases. Start a fresh map with the updated
package; old saves can contain classes removed with the scenic lighting.

## Rendering limits

Rain exposure uses a bounded grid, usually about 64 map units, capped per face.
It is not per-pixel tracing. Wetness transitions interpolate within each face;
partial overhang boundaries are approximate at this resolution.
Large/newly visited surfaces need time to settle.
Maintenance uses at most 40 surface visits per game tic.

UZDoom 5.0.1 custom postprocessing does not expose the scene-depth texture.
Underwater uses a camera-aligned **8 x 4 static-geometry ray grid** with interpolated
distance. This approximates distance blur; it cannot resolve every object or
silhouette. Strong color edges receive reduced blur weight.

The same helper measures a heat actor's projected bounding region instead of the
whole screen. Ray directions use interpolated camera position, yaw, pitch, roll,
actual FOV, aspect and viewport. Heat is clipped conservatively against nearby
geometry samples. Actors are excluded from the distance rays; thin occluders,
portals, stereo projection and complex stacked volumes remain prototype limits.

Shader parameters stay within a conservative 128-byte budget. Thirty-two distances
are encoded into eight exactly representable 24-bit integers carried by two vec4s;
each distance uses a conservative 6-bit square-root quantization. This avoids the
GPU failure encountered with the initial oversized parameter block.

Water discovery uses authored control heights; changing water levels and complex
stacked volumes are not fully supported. Computed ACS movement tags and polyobjects
are not guaranteed discovery. Snow marks are visual, not displaced geometry.

## Manual checks

Use hardware rendering, quality 3 and reduced effects off. Compare each switch
after several seconds at the same camera position:

```text
UTNT_fxquality 3
UTNT_reducedfx false
weatherfx true
UTNT_wetsurfaces true
UTNT_underwateratmosphere true
UTNT_footprints true
UTNT_mechanismfx true
netevent environmentstats
```

For the laboratory, load the current mod plus `tools/fixtures/environment`:

```powershell
& "F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe" -iwad "F:/DoomDev/DOOM2.WAD" -file "F:/DoomDev/Projects/realm667.git/tutnt.pk3" "F:/DoomDev/Projects/realm667.git/tools/fixtures/environment" +playerclass Marine +map ENVTEST
```

Useful laboratory commands:

| Check | Commands |
|---|---|
| Open wet floor | `netevent envpos 128 128 0`, then `netevent envview 0 35` |
| Roof / solid 3D floor | `netevent envpos 384 384 0` / `netevent envpos 640 384 0` |
| Snow marks | `netevent envpos 32 384 0`, walk forward, look back |
| Underwater bed and walls | `netevent envpos 384 640 -64`, then `netevent envview 90 25` |
| Platform dust | `netevent envpos 700 384 0`, then `netevent envmove` |
| Heat over lava | `netevent envpos 550 128 0`, `netevent envview 0 0`, `UTNT_localheatprototype true` |
| Heat wall / floor | `netevent heatlabmode 1` / `netevent heatlabmode 0` |
| Heat coverage mask | `UTNT_heatlabmask true`; return to the actual effect with `false` |
| Occluded heat source | `netevent heatlabmode 2`, `netevent envpos 128 384 0`, `netevent envview 0 -15` |

The red mask is diagnostic, not the effect. Heat refraction is irregular and below
one pixel peak displacement at the current output resolution, with a small
actor-defined volume. It is deliberately absent from the normal gameplay menu.

For campaign rain use `map TNT02`, then `warp 2944 3568 -496`.
Look along the island surface, wait about 10 seconds and compare
`UTNT_wetsurfaces true` / `UTNT_wetsurfaces false`.

For campaign water use `map TNT03A2` followed by `warp 6144 -7968 -280`;
this pool is shallow, so it tests caustics rather than full submersion.

## Generation and validation

```text
python -B tools/build_environment_fx.py
python -B tools/build_environment_fx.py --check
python -B -m unittest discover -s tools -p test_environment_contracts.py
python -B tools/test_environment_fx.py --case compile --mod tutnt.pk3
python -B tools/test_environment_fx.py --renderer 0 --mod tutnt.pk3
python -B tools/test_environment_fx.py --renderer 1 --mod tutnt.pk3
python -B tools/test_environment_fx.py --case prototype --renderer 1 --mod tutnt.pk3
```

Runtime fixtures cover exposure, roofs, 3D floors, real submersion, footprint
emission/budget, mechanism reaction and save/load. Visual comparisons cover wet
materials, caustics, dust, and heat mask location at changed yaw/pitch/FOV and an
occluded source. OpenGL and Vulkan are checked; this is not a full campaign or
multiplayer/performance certification.

Evidence: `tutnt/.codex/validation/environment-review/` and
`tutnt/.codex/validation/environment-fx/`. Test packages:
`tutnt/.codex/builds/`. Temporary work:
`tutnt/.codex/work/environment-fx-review/`.
