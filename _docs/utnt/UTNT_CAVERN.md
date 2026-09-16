# TNT03A2 cavern presentation

Updated: 16 September 2026.

## Authoritative, editable production sources

The final cavern is authored directly in `tutnt/maps/tnt03a2.wad`. Its three
blocked fissures, recesses, distant skybox rooms, 102 scenery Things, three
lights, rock materials and sector light/fog settings are present in the source
map. The package builder no longer changes this map or creates these placements.
The original map's vertices, Things, gameplay actions and script lumps were
preserved; only the three original entrance lines become blocked two-sided windows.

Open this WAD in Ultimate Doom Builder with the current `tutnt.pk3` or the
`tutnt/` source directory as resource, using the existing UZDoom/ZDoom UDMF
configuration. Reload resources after updating them. Enable model display in
visual mode. The scenery is in the **UTNT/Cavern** Thing category (editor numbers
25000–25101); the parallax sky camera is 25110 and the lava-fall light is 25111.
Models are cosmetic, so moving them does not add collision or new platforms.

| What to edit | Authoritative file under `tutnt/` |
| --- | --- |
| Rooms, openings, model positions/angles/scales, lights, fog and texture assignments | `maps/tnt03a2.wad` |
| Rock and lava-fall mesh surfaces | `models/cavern/*.obj` |
| Model skins and rendering definitions | `modeldef/MODELDEF.cavern` |
| Editor numbers | `mapinfo/MAPINFO.cavern` |
| Editable scenery actor definitions and editor labels | `zscript/cavern-actors.zc` |
| Local materials, including the fog window tint | `textures/definitions/TEXTURES.cavern`, `gldefs/GLDEFS.cavern`, `shaders/cavern-*.fp` |
| Lava haze positions/radii | `cavern/haze.txt` |
| Falling ceiling-dust positions | `cavern/fall-sources.txt` |
| Main-room parallax anchors | `cavern/skyviews.txt` |
| Particle behavior, budgets, light color/radius and parallax speed | `zscript/UTNT_Cavern.zc`, `zscript/UTNT_CavernAtmosphere.zc` |

Map camera Things determine each skyroom's actual initial camera position.
Their saved `MapOrigin` prevents parallax drift after save/load or hub return.
The skyview table supplies the corresponding main-room anchor; its historical
origin columns are only a compatibility fallback for native cameras.

`cavern/authored.json` switches the former cavern generator to read-only
validation in both normal and check builds. It never regenerates the map,
meshes, actor definitions, shaders or effect manifests. `tools/author_cavern.py`
records the one-time migration and validates required production resources.
The old `cavern-generated.zc`, scenery/sector/platform/portal manifests and
`skyrooms.json` are legacy migration inputs, not active placement instructions.
Edit the WAD and `cavern-actors.zc`; do not regenerate the old layer. Keeping the
legacy class file separate preserves the concurrent editor-skip optimization.

## Windows and closed lava-fall meshes

All three entrance floors, ceilings and borders use UCAVROCK. The entrance
middle texture UCAVFOG is a solid `#1b1814` tint matching the distant fog endpoint;
the line uses ordinary translucent rendering with alpha 0.5 and wrapped middle
texture. The original blocking flag remains set. These are ordinary editable
UDMF fields, not runtime overrides.

The lava curtain, both rock cheeks and the outlet lip have closed upper, lower
and rear surfaces. Their backs are buried in the supporting cliff. Every mesh
edge has two adjacent triangles, so looking down no longer reveals an open shell.

## Light, fog and lifecycle

Main cavern fog is authored as `#363029`, UDMF density 44 (runtime 22). The
entrance pockets use light 160 with that same fog. Distant rooms use `#1b1814`,
UDMF density 24 (runtime 12), light 96, floor light 80 and ceiling light 64.
Seven platform control ceilings carry a relative +36 light offset. These are
starting values: later manual edits remain authoritative. Runtime does not
reset sector light/fog or texture choices. A cache refresh preserves the actual
sector values after map setup.

Scenery and light actors are ordinary serialized map actors. Only transient
smoke, dust, haze and local parallax controllers are rebuilt after loading.
Procedural particles, animated shaders and per-player parallax require the
running engine; UDB can edit their sources but cannot fully preview them.

## Verification of the authoring migration

The isolated production candidate passed 49 lifecycle assertions each on
OpenGL and Vulkan, 15 checks of deliberately edited map values through startup,
save/load and hub return, 14 cooperative parallax assertions, and six structural
regressions. An additional 14-point source comparison verified preservation of
original vertices, Things and non-geometry lumps, editor registrations, closed
meshes and unchanged manual source bytes after both build modes.

A direct ZIP of the production tree also passed the OpenGL lifecycle checks.
It has one existing texture-loader warning for `textures/definitions`; the
normal builder expands these modules and avoids that warning. Packaging still
adds precache lists/build metadata, so playable direct-ZIP content does not mean
byte-for-byte archive equivalence. See [production rules](PRODUCTION_SOURCES.md).
The source WAD checksum changes; begin a fresh TNT03A2 visit when updating from
the previous package. Saves made with the new map pass the lifecycle checks.

Local evidence is under `.codex/validation/cavern-tnt03a2/authoring-*.json` and
`.codex/logs/cavern-tnt03a2/authoring-*`. The saved source before migration is in
`.codex/backups/cavern-authoring-before.zip`. No runtime resource depends on it.

Final common package `fd7438eaf0ef` passed 49 Vulkan lifecycle checks and the
15 deliberate manual-edit checks. A fresh, direct ZIP of the current production
sources passed 49 OpenGL checks. Package/source comparison confirms identical
cavern map/model/runtime bytes (TEXTURES is assembled from the matching module).
The installed UDB parser recognizes all 102 scenery classes without syntax
errors; this is a parser check, not an interactive visual-mode acceptance.
The layout checker reports only the 15 pre-existing editor sidecars/backups.

## Earlier implementation notes

The sections below record the earlier generator/runtime implementation and its
visual refinements. The authoritative source and lifecycle rules above supersede
references below to package-only geometry, regenerated scenery and runtime
lighting overrides.

## Lava haze, smoke and suspended dust

The lava carries a visibly luminous orange haze reaching 320 map units above
the lava surface. Its density fades upward and
across the sides; slow world-space noise creates rising folds. The generator
joins the 206 adjoining lava sectors before measuring shoreline clearance,
then emits 119 fixed positions in `cavern/haze.txt`. Their horizontal radius
stays inside the shoreline, up to 320 units. Original WAD geometry is unchanged.

Haze uses additive, fullbright client VisualThinkers, native geometry depth
testing and the original lava palette color. This gives a smooth blended light
layer rather than a global color filter. VisualThinkers are important: the
actor sprite path applies a hard alpha test to the opaque shader carrier,
which would cut the soft gradients into visible shapes. The layer has a fixed
height and smoothly fades at distance and when effect quality is disabled.
It supplements the existing localized heat distortion.

Broad, translucent gray-brown wisps rise slowly above the lava; their entire
vertical footprint stays below 384 units. Sparse dust clouds drift higher in
the cavern. These use the same world-space noise with a soft radial boundary.
The deterministic emitter produces at most two lava wisps and one upper dust
cloud every 30 tics. Lifetimes cap this additional population below 32. Quality
zero stops new emissions and fades the haze; higher dust is omitted at quality
one. Save/load and hub return rebuild the local layer without duplicates.

## Organic rock overlays and ceiling dust

Twenty irregular rock faces interrupt the tall cliffs below their walkable rims;
eight broad roof masses break up the ceiling, in addition to the four existing
stalactites and four lava-fall pieces. The meshes use the local IKWALL44-based material, asymmetric ridges, smooth
vertex normals and buried perimeter rings. They add
13,500 triangles across these masses and the eight additional narrow cliff ribs. Wall bulges remain below ledges and the lava-fall
opening is reserved. These cosmetic models have no collision and do not create
new stepping stones or alter the platform route.

The generator resolves authored Plane_Align/Plane_Copy slopes in memory before
sampling roof attachments, stalactite roots, ledge heights and dust sources.
This is necessary because some native ceiling slopes only take effect when the
engine loads the map. No WAD data is rewritten. Eight verified source positions
are stored in `cavern/fall-sources.txt` below the roof masses.

`UTNT_CavernAtmosphere.zc` adds small suspended grains around the local camera
and slowly moving translucent smoke sheets. Emission follows effect quality;
particles have finite lifetimes, soft alpha, near/distance fades and checks
against floors, ceilings and solid 3D floors. They stay inside the cavern.
No gameplay random stream or interactive actor is used.

After an initial 12-second delay, a nearby unobstructed roof source can release
a short fall of dust and grit. Successful events are separated by approximately
20-37 seconds; unavailable sources are retried after five seconds. A burst emits
32 falling grains and eight expanding puffs with gentle downward acceleration.
Three spatial sound cues reuse the original stone/gravel recordings through
`sndinfo/sndinfo.cavern`, with lowered pitch, restrained volume and distance
attenuation. Save/load and hub return clear/rebuild the local emitters. Effect
quality zero stops new ambient particles and roof events; existing particles
finish their bounded fade.

## Cliff edges, corner ribs and lava-foot formations

A second geometry pass adds 46 cosmetic models: twenty folded cliff-edge skirts,
fourteen tapered corner ribs and twelve rock fans at the lava shoreline, using
3,608 additional triangles in total. The
skirts follow sloping ledges, curl outward beneath the top and disappear into
the wall at both ends. Corner ribs span two adjoining cliff faces with unequal
heights; straight stretches and tight turns remain open. Each shoreline fan
combines three differently sized, partly submerged rock mounds in one model.
The existing lava-fall mouth is excluded.

`tools/cavern_rock_details.py` derives these meshes from the original cliff
boundaries. Every generated vertex is checked against the neighbouring walkable
floor plane: rims remain at least eight units below it, corner ribs at least
110 units below both adjoining planes. The source map and collision remain
unchanged. Per-model vertex/triangle counts and minimum clearance are recorded
in `cavern/detail-clearance.txt`; duplicate model names and degenerate triangles
are rejected, and face normals point outward. Together
with the existing scenery, the main cavern has 90 static decorative models before the skybox extension.

## Fissures into distant cavern skyboxes

Three irregular rock frames reveal native UZDoom wall skyboxes at original
boundary lines 4783, 4729 and 4969: the first chamber's northern rim, the second
chamber's northeastern wall and the southern cavern boundary. Each opening has
a shallow 96-unit recess behind the original wall. `Sector_SetPortal` type 2
creates a `SkyCamCompat` portal, then type 5 transfers it to the recess's rear
wall. These are real scene portals, with native depth testing and camera rotation.
Each viewpoint follows the local player's active camera at one eighth of its
translation speed. The offset is rotated by that sky camera's authored yaw, so
forward and sideways motion stay aligned with the visible hall. These are scenic
views, not traversable passages.

Each of the three isolated scenes contains two connected large halls, lava,
six differently sized occluding rock pillars and three hanging rock formations. Varied
camera positions/yaw and layered fog expose different views. Their fog colour
retains the main cavern's warm hue at lower brightness (`#1b1814` versus
`#363029`). Hall lighting is 96, floor lighting 80 and ceiling lighting 64.
The distant rooms use UDMF fog density 24 (runtime 12). Entrance recesses use
light 160, floor offset +16, ceiling offset -16, and UDMF fog density 44
(runtime 22), so their nearby rock reads through the main cavern haze.
Sky-room rock walls, pillars, ceilings and the nine distant models use UV scale
4, corresponding to one eighth of the enlarged foreground rock size. Lava uses
scale 8. Foreground fissure frames and shallow recesses share the main room's
world-projected rock material. The `UCAVSLAV` carrier uses `shaders/cavern-lava.fp`, generated
from the shared lava shader: its world-space pattern and relief are scaled
consistently, while fog distances remain in actual scene units. This is necessary
because ordinary lava deliberately ignores flat UV scaling.

`UTNTCavernSkyView` uses three client-side thinkers to position the native portal
viewpoints for the current local camera, including spectator/camera switches.
It leaves portal bindings and all gameplay actors intact. Normal motion uses
native interpolation; camera switches and large teleports clear interpolation.
Offsets are relative to immutable origins in `cavern/skyviews.txt`, never to a
previous saved offset. Save/load and hub return rebuild the local thinkers.
Horizontal offsets are bounded to 512 units per axis and vertical positions stay
inside the sky room. Parallax remains active even with effect quality zero.

All twelve added models (three foreground frames, nine distant formations) bring the full scenic
population to 102. The three indoor cameras are explicitly excluded from the
outdoor weather controller, preventing snow or rain inside these halls.

`tools/cavern_skyrooms.py` generates `cavern/skyrooms.json` from the current map.
`build_utnt.py` applies that manifest only to the immutable package payload.
The editor's source WAD is never overwritten. Existing vertex, sector, thing and
script data remain unchanged; exactly three original linedefs become two-sided,
retaining their blocking flag, and their three sidedefs receive upper/lower rock
textures. Recesses and skybox geometry are appended without reindexing existing
elements. Obsolete node lumps are removed so the engine rebuilds the BSP.
The patch rejects a changed geometry fingerprint, mismatched topology or a second
application. Behind-wall clearance and coordinate extents are checked during
generation. Skybox tags/TIDs occupy 65200-65402 and must remain reserved.
Use the built PK3 to see the full presentation; the editable WAD intentionally
does not contain these generated recesses or sky rooms.

## Validation

Run `python -B tools/build_cavern.py --check` and
`python -B tools/build_definition_tables.py --check` before packaging.
`tools/test_cavern.py` captures thirteen room/detail views plus a ceiling-dust sequence
and checks model/light counts,
noncollision, bounded clouds, haze height and sector lighting before and after
save/load. Two low views specifically expose the haze's upper boundary.
Use `--renderer 0` for OpenGL and `--renderer 1` for Vulkan. `--live-overlay`
tests current cavern resources over an existing complete cavern package during
iteration; final acceptance uses the rebuilt package without this option.

Local screenshots and logs: `tutnt/.codex/logs/cavern-tnt03a2/`.
Machine-readable results: `tutnt/.codex/validation/cavern-tnt03a2/`.
`--hub` adds effect-quality shutdown and travel through TNT03A1 back to TNT03A2.
It requires 43 lifecycle/movement assertions; the ordinary save/load run requires 29.
Seven additional structural tests in `tools/test_cavern_skyrooms.py` verify map
preservation, native portal wiring, blocked entrances and stale/double-patch
rejection. Runtime checks also verify the three cameras/portals and their
exclusion from outdoor weather. A controlled 256 / 128 / 64 unit view movement
must produce exactly 32 / 16 / 8 units of skybox movement, rotated by camera yaw.
`python -B tools/test_cavern_coop.py` launches two real peers with different local
views and effect quality settings. Fourteen checks cover independent viewpoints,
portal bindings, immutable origins, measured movement and active-camera switching.
The checks include all eight valid roof sources, a single atmosphere controller,
bounded particles, actual falling grit and all three sound triggers with resolved
audio resources. Runtime tests use `-nosound`; this verifies sound binding and
triggering, not an auditory evaluation of the mix.
The shared integration package must be built from the full current workspace;
the isolated cavern package must never be copied over it.

Acceptance on 15 September 2026: UZDoom 5.0.1 passed all 22 lifecycle assertions
on OpenGL and all 22 on Vulkan, using complete packages without a live overlay.
The OpenGL test package and the newly built root `tutnt.pk3` have identical
SHA-256 hashes; Vulkan tested the root package directly. Six views per renderer
were captured and representative views were visually inspected. Source-map
geometry matches the task's starting snapshot, and
all generated cavern files also match generation against the committed map.
These checks cover single-player save/load, effect shutdown and hub return;
network multiplayer was not exercised for this change.

Haze acceptance on 16 September 2026: the rebuilt root package passed all 28
assertions on both OpenGL and Vulkan in UZDoom 5.0.1, without a live overlay.
The eight-view captures include the platform approach and two views just above
the lava; representative views confirm continuous soft alpha boundaries. Tests
verify all 119 haze elements, the 320-unit height, the additional smoke budget,
its 384-unit vertical limit, clean quality shutdown and no load/hub duplicates.
Results: `cavern-haze-final-0.json` and `cavern-haze-final-1.json` in the local
validation directory.

Organic rock/atmosphere acceptance on 16 September 2026: the rebuilt root
`tutnt.pk3` (build `3a15357b57c1`) passed all 33 assertions on OpenGL and all
33 on Vulkan in UZDoom 5.0.1, without a live overlay. Representative room and
fall-sequence screenshots were inspected. Both sound resources resolve and all
three cues execute; the automated runs have audio output disabled. All vertex,
sector, sidedef and linedef data match the original task snapshot. Results:
`cavern-organic-final-0.json`, `cavern-organic-final-1.json` and
`organic-geometry.json` in the local validation directory.

Cliff-detail and skybox acceptance on 16 September 2026: the rebuilt root
`tutnt.pk3` (build `0d812125b62c`) passed all 36 assertions on OpenGL and all
36 on Vulkan in UZDoom 5.0.1, without a live overlay. The six structural tests
also pass. Final fissure views were visually inspected in both renderers.
Package inspection confirms that the transformed TEXTMAP matches the manifest
and that SCRIPTS and BEHAVIOR are unchanged. The same manifest also applies to
the committed source map despite unrelated local editor formatting changes.
The original routes remain blocked at the three scenic openings; the added
recesses can extend projectile traces behind those walls. Results:
`cavern-skybox-final-0.json`, `cavern-skybox-final-1.json` and
`skybox-package.json` in the local validation directory.

Darkness/parallax acceptance on 16 September 2026: root `tutnt.pk3` build
`4c6cc0cec90c` passed 43 assertions on OpenGL and 43 on Vulkan, without a live
overlay. Two real network peers passed fourteen additional checks with distinct
local sky viewpoints, measured one-eighth movement, camera switching and opposing
effect-quality settings. Seven structural tests pass. Representative final
fissure screenshots were inspected in both renderers. Package/source comparisons
confirm the new lighting, parallax code and immutable camera origins are present,
while SCRIPTS and BEHAVIOR remain unchanged. Evidence: `cavern-parallax-final-0.json`,
`cavern-parallax-final-1.json`, `cavern-parallax-coop-final.json` and
`parallax-package.json` in the local validation directory.

Texture-scale acceptance on 16 September 2026: root package build `78944e691776`
passed all 29 save/load and movement assertions on OpenGL and all 29 on Vulkan.
Final fissure views were visually inspected in both renderers. Seven map
structure tests pass. Direct source/package checks cover all three hall sectors,
156 wall sides, nine model UV sets and the world-space lava variant; foreground
geometry and the shared lava shader remain unchanged. Evidence:
`cavern-texture-scale-final-0.json`, `cavern-texture-scale-final-1.json` and
`texture-scale.json` in the local validation directory.

## Screenshot-driven refinement (16 September 2026)

The three frames now have 52 contour points and seven radial bands (624
triangles each). Their outer perimeter sinks 48 units into the supporting wall.
Rock patches use eight rings with 25 points and smooth shared vertex normals;
eight narrower ribs add secondary structure beneath existing ledges. All 102
scenery actors remain cosmetic. Rock actors take their supporting sector light
instead of the brighter lava-floor light, reducing lighting seams.

Main-room rock uses a local UCAVROCK material based on the existing expanded
IKWALL44 artwork. Walls, floor/ceiling rock and models share a world projection,
1024-unit texture period (twice the existing expanded material), broad coordinate
variation and blended normal detail. This avoids per-face UV discontinuities.
The replacement recognizes both original and generated area-material names and
is reapplied once after map startup. It does not affect other map areas. The
local shader uses normal detail rather than the shared UV-based parallax shader.
Distant rock uses scale 4, retaining one-eighth apparent features relative to the
enlarged foreground; sky lava retains scale 8 and the existing world-space shader.

Sky rooms keep precisely the main cave fog colour, but use UDMF density 6
(runtime density 3). UZDoom halves the authored integer, so a value of 1 would
become zero and fall back to excessive light-dependent fog. Reduced optical
depth removes the bright uniform fill. Two extra foreground pillars per distant
scene provide nearer silhouettes. The one-eighth camera movement is unchanged.

Lava haze now uses centered camera-facing soft clouds instead of floor-anchored
upright cards. Radial alpha and a world-height fade make tilted floor intersections
transparent before they clip. The 320-unit carriers are centered 160 units above
lava; their shader fades completely by height 336. Mist source heights and the
384-unit smoke bound remain unchanged. Three added regression views reproduce
the reported fissure, steep downward lava view and lower cavern wall.

Refinement acceptance on 16 September 2026: complete root package build
`0bc66f02b5b2` passed 46 assertions on OpenGL and 46 on Vulkan in UZDoom 5.0.1,
including save/load, hub return, quality shutdown, local material persistence,
measured parallax and effect budgets. Seven structural tests pass. Final views
17-19 and representative fissure views were visually inspected. The eight new
ribs have at least 355.7 units of clearance below neighbouring walkable planes.
Source/package comparison confirms the generated map patch and changed runtime
resources. Evidence: `cavern-refinement-final-0.json`,
`cavern-refinement-final-1.json`, `refinement-clearance.json` and
`refinement-package.json` in the central local validation directory.
The layout check reports only the fifteen pre-existing editor sidecars/backups
in `tutnt/maps`; this task did not create or move those files.

## Entrance and distant fog correction (16 September 2026)

The entrance recesses previously had runtime fog density 5 instead of the main
cave's 22. They now share the exact foreground fog colour and density, with
brighter rock lighting. Distant rooms have four times their previous density
(12 instead of 3), lower light, and the same warm hue at half RGB brightness.
The darker fog endpoint is intentional: increasing density with the old bright
endpoint would turn the distant scene into a brighter coloured fill.

`cavern/portal-atmosphere.txt` binds the three entrances, recesses, rear portal
lines and native viewpoint TIDs. Runtime validates these relationships and sets
the absolute presentation values after map startup and after loading a save.
This prevents serialized portal settings from bypassing the presentation setup.
Geometry, portal links, parallax and gameplay are unchanged. UZDoom rejects
saves from the previous package because the authored TEXTMAP lighting values
change its map checksum; start TNT03A2 fresh with this package.

Regression view 20 uses the reported (4594, -3695, -115) player position with
view-height adjustment. All three openings and this view are now captured with
UTNT_atmosphere both off and on: the optional atmosphere multiplies skybox thick
fog, which the earlier default-only captures did not exercise.

Acceptance: complete root package build `166283e3e2b6` passed all 49 assertions
on OpenGL and all 49 on Vulkan in UZDoom 5.0.1, including save/load and hub return.
Eight structure tests pass. Final view 20 was visually checked on both renderers
with the atmosphere option on, and on Vulkan with it off. Package/runtime/map
comparison passed. Evidence: `cavern-portal-fog-final-0.json`,
`cavern-portal-fog-final-1.json` and `portal-fog-package.json` in central validation.
The separate previous-package save probe was rejected by the engine as a
different level; it is recorded as an unsuccessful compatibility test, not a
passed lifecycle test. The layout checker still reports only the fifteen
pre-existing editor sidecars/backups under `tutnt/maps`.
