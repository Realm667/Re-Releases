# SteamSpawner pressure steam

Implemented from the user's approved image mockup on 2026-09-08.

The existing UpwardSteamer (19996), ForwardSteamer (19997) and DownwardSteamer
(19998) emit a narrow pressure jet which slows, expands into irregular rolling
wisps and dissolves. Four independently rotated density shapes, internal material
motion and modest emission-pressure variation break up repetition. Steam uses
neutral translucent shading and native sector/dynamic lighting, with
no additive glow, attached light or fullscreen effect. The density artwork is
reused unchanged from the existing fire smoke atlas; USTM materials are separate
from UFSM, so the fire's appearance is unaffected.

Map actor names, IDs, direction, downward -8 offset, flags, arguments and native
Activate/Deactivate state labels remain compatible. No campaign map, ACS script,
sound or gameplay damage is changed. Steam1..5 remain available for external
references, but the three spawners no longer create these old projectile actors.
The historical forward A_CustomMissile pitch uses abs(cos(pitch)); the new effect
therefore follows actor yaw, preserving the actual old forward direction.

## Lifecycle and limits

One local controller per visible active source, capped at 64 controllers. Sheets
live 38â€“47 tics, with one birth every 1/2/3 tics at high/medium/low quality. Sources
beyond 640 units and Reduced FX use low quality. Births consume the existing
ambient budget, never the combat budget. UTNT_fxquality=0 and UTNT_lod disable or
cull the visual. Controllers remain for 12 tics after shutdown, allowing the final
8-tic fade to finish and avoiding duplicate streams on rapid reactivation. Owner
removal, distance culling and map changes retire local visuals; save/load recreates
them from the saved actor switch state. Private per-controller random state avoids
consuming gameplay random streams. Steam has no physical actors or actor hits.

Each wisp traces its short movement through walls, floors, ceilings and solid 3D
floors. This prevents particle centers travelling through solids; billboard edges
can still intersect nearby geometry. This is a layered sprite effect, not a fluid
simulation or volumetric renderer. Performance remains subject to scene overdraw;
the stress test is a bounded-lifecycle check, not a general FPS guarantee.

## Validation

UZDoom 5.0.1 on the local NVIDIA hardware, OpenGL and Vulkan:

- 65 lifecycle assertions per renderer: all three directions, finite lifetime,
  non-additive/non-fullbright material, quality 0/1/2/3, Reduced FX, distance,
  deactivate/reactivate, rapid toggles, owner removal, save/load, walls/floor/ceiling
  and 48 simultaneous sources.
- Six more assertions per renderer against a solid 3D slab, including upward and
  downward collision on its two faces. Total: 142 assertions.
- Two real local Koop peers, quality 3 vs 0, synchronized off/on: 26 assertions,
  completion markers from both peers and no reported consistency failure.
- Existing forward source in TNT03A1 visually inspected against the approved
  mockup. Its start position is (-4222, -2591, -224), angle 180. The 20 existing
  campaign placements were inventoried without editing their maps.

Evidence: tools/validation/steam-2026-09-08. The isolated tested package is based
on the recorded Git HEAD plus only the seven Steam runtime paths; unrelated
concurrent work is not included. Full live-source compilation was separately
attempted and initially blocked by concurrent, unfinished UTNT_Portal.zc code.
Package integration evidence, when present, is recorded separately in package.json.
No full campaign playthrough or compatibility claim for pre-update saves.

Reproduce with UTNT_ENGINE and UTNT_IWAD set:

```
python tools/test_steam.py --mod tutnt.pk3
python tools/test_steam_coop.py --mod tutnt.pk3
```

## Darker, softer steam refinement — 2026-09-08/09

At the user's request, the material now ranges from neutral gray 0.46 to
0.60 (#999999) before scene lighting and transparency. A wider normalized
3x3 Gaussian sampling kernel and gentler alpha edges soften the fine contours.
The actor motion, density schedule and other effects are unchanged.
The updated shader compiled and was visually checked at the TNT03A1 source
in Vulkan, with a matching-camera baseline capture. OpenGL campaign-start
attempts timed out before reaching the map (50/95 seconds); the dedicated
Steam fixture also timed out (45 seconds). The UNCHANGED original package
then reproduced the same pre-map timeout in that fixture (45 seconds).
OpenGL visual acceptance is therefore not claimed for this refinement;
the original implementation's earlier OpenGL checks remain historical.
All attempt logs and the baseline result are retained.
The tested PK3 was assembled from the existing package, changing only this shader
and generated build metadata. Evidence: tools/validation/steam-softening-2026-09-08.

## Native sector brightness — 2026-09-09

Removed the +28 sprite-light bonus. Steam now explicitly inherits the current
render sector lighting (AddLightLevel=false, LightLevel=-1); no fixed brightness
or fullbright flag is used. This follows lighting changes for existing wisps as
well as new ones. Native movement updates the render sector. The gray material
and softened density contours remain unchanged. In a nearly unlit sector the
steam can become nearly invisible, like other normally lit surfaces.

Vulkan and OpenGL: compilation and 16 runtime assertions passed. The same frozen
wisps were visually checked at sector light 224, then 32, then 224 again.
Evidence: tools/validation/steam-lighting-2026-09-09.
