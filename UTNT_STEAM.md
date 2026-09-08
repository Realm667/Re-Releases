# SteamSpawner pressure steam

Implemented from the user's approved image mockup on 2026-09-08.

The existing UpwardSteamer (19996), ForwardSteamer (19997) and DownwardSteamer
(19998) emit a narrow pressure jet which slows, expands into irregular rolling
wisps and dissolves. Four independently rotated density shapes, internal material
motion and modest emission-pressure variation break up repetition. Steam uses
neutral translucent shading, sector/dynamic lighting and +28 sprite light, with
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
live 38–47 tics, with one birth every 1/2/3 tics at high/medium/low quality. Sources
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
