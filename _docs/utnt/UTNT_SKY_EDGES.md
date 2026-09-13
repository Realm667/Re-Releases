# Natural skyline and terrain edges

Updated: 13 September 2026.

Outdoor rock walls gain irregular outward bulges and overhangs; snow/ice walls
receive softer cornices. Crest height and outward reach vary independently,
with additional raised lobes along the skyline. This implements the approved
rock/snow mockups and the requested stronger upward irregularity.

## Material and boundary rules

The generator inspects actual wall materials, not map names. Snow profiles are
restricted to ICEY, SNOW3, OSNOW and OSNOW3, including their registered expanded
variants. This covers the snow/ice scenery in TNT03A1/TNT03A2 and the same
materials where authored elsewhere. Rock profiles cover QROCK1/3/4/5, IKWALL44,
ASHWALL2 and ROCKF5 and their registered variants. Masonry, metal and liquids
never acquire a cornice merely because they stand outdoors.

One-sided walls ending at a sky ceiling, exposed upper textures below a sky
ceiling, and lower walls against closed sky sectors qualify. Upper walls require
a non-sky backing ceiling and at least eight map units of visible wall height;
the cornice radius shrinks to fit that strip without extending into the opening
below. Closed-sector lower walls require both ceilings to be F_SKY1. Ordinary
outdoor steps and open elevated terraces use the separate terrain profiles below.
Horizon/portal lines and other skyline walls shorter than 48 map units are excluded.

Skyline coverage (unchanged by the terrain extension):

| Map | Edges |
| --- | ---: |
| TNT01 | 136 |
| TNT02 | 256 |
| TNT03A1 | 386 |
| TNT03A2 | 49 |
| TNT03B | 57 |
| TNT04A | 67 |
| TNT04B | 396 |
| TNT04C | 159 |
| TNT04CN | 88 |
| TNTLE | 560 |

Total: 2,154 edges, comprising 1,702 rock and 452 snow/ice edges. The complete
manifest records each map, line, side, material and generated mesh.

## Outdoor terrain profiles

`tools/build_terrain_edges.py` extends the shared generator to open outdoor
ledges and selected wall-foot deposits. It uses the existing organic material
profiles: rock, grass, soil, gravel, snow, snowrock and ice. Both the upper floor
and the exposed wall must be natural materials. Snow appears only when the
corresponding floor or wall actually uses a snow/ice material.

Soil, gravel and snow ledges use two meshes with an identical shared
seam: an upper cap using the floor material and a lower shoulder using the wall
material. Grass instead uses a feathered skirt over the original wall plane. This supports a
grass or snow covering over a rock face without replacing that face's material.
Rock ledges use a continuous, smoothly shaded shoulder with overlapping floor
and wall skins. The upper material fades into the wall material over a band
below the authored floor plane, including slopes. Both skins share the same
profile normals; a small separation prevents depth fighting. The broader curved
join and lighter underside shading remove the hard cut while retaining the
projecting rock form. Snow caps form a continuous rounded arc;
its wall-side section remains smooth even over rock. Grass uses a low, smooth
transition into the neighbouring floor, fading to the actual underlying map
materials at both ends instead of forming a hanging turf fringe. The cap follows floor rotation, scaling, panning and
expanded texture bindings. Its light/glow origin lies in the receiving floor
sector, and its horizontal seam has no artificial brightness boost. Lower wall pegging uses the backing ceiling only
when both ceilings are sky; otherwise it uses the front ceiling, matching the
engine and area-texture handler.

Grass/soil steps qualify from four map units; other ledges from sixteen. Both
sides must have sky ceilings and the upper floor must retain at least 56 units
of headroom. Base radii are capped at fourteen units for rock/grass, ten for
soil, and eight for snow/gravel. Rock and soil project further to make their
profiles readable. Crowded upper floors retain the smaller radius; grass also
shrinks to fit the receiving lower floor. Caps rise at most one unit above the
authored floor (snow and grass retain only a small separation offset). Selected
broad wall feet receive wider, smoothly rounded deposits at most 1.5 units high,
with translucent feathering into the wall/floor junction.
Polygon checks require room on the receiving floor. Narrow ledges, short wall
feet, technical materials, scrolling floors and action/portal lines are excluded. Authored slope
setup lines remain supported. These are cosmetic edge details, not new walkable
platforms or collision geometry.

The existing height maps now also influence these new meshes during generation.
A smoothed, tiled sample controls small variations in reach and rock facets;
its amplitude is bounded and shared material seams remain identical. Rock
ledges share the floor-height variation across both skins; separate wall-mesh
deformation is omitted inside this smooth overlap. Signed
height values are decoded relative to the existing neutral level. Fine surface
relief continues in the original POM shader. The existing skyline profile is
unchanged by this additional sampling.

Current total coverage: 2,154 skyline models, 4,152 terrain ledges represented
by 8,304 cap/shoulder models, and 974 wall-foot models. The combined 11,432 models
contain 2,075,400 triangles across ten maps. These totals span the whole campaign;
render visibility remains bounded per model. No measured performance gain is
claimed.

Terrain actors reuse the client-only skyline lifecycle and ceiling-glow canvas.
They validate both floor and wall materials, their texture transforms, and both
sectors' floor/ceiling planes. A changed dependency hides the affected model;
restoring it enables the model again. Save/load recreates the local models.

## Geometry and material continuity

`tools/build_sky_edges.py` generates OBJ meshes and registrations without
rewriting WADs. Each cross-section curls over the skyline, projects toward the
playable side and returns to the original wall. Snow uses an interpolated soft
profile; rock uses taller, narrower crests, asymmetric shoulders and angular
ridges at two spatial scales. Its upper faces use facet normals while the
lower join retains smooth shading. Snow uses a fuller rounded shoulder and finer sampling, including upper
textures, with only ten percent additional underside shading. Base radii
scale with wall clearance, capped at 24 map units for snow and 22 for rock;
spatial variation and separately raised crests produce the final silhouette.
Connected ends share positions and bounded miter directions. Unmatched ends
taper into the wall so architecture and material changes retain their borders.

Authored Plane_Align slopes, triangular vertex heights and plane-copy setup
are resolved during generation. UVs use the current area-expansion mappings,
wall pegging, scales and offsets, including upper-texture pegging. Texture distance follows the curved profile
and meets the wall at its lower seam. Generated material wrappers reuse the
existing diffuse textures, normal/height maps, parallax and weather state;
a restrained orientation-dependent shade makes the underside readable without
adding a dark border to the vertical join. Snow has a separate lighter wrapper;
feathered grass and wall-foot materials add no macro underside shadow. Their
alpha masks use per-edge world-space metadata, sharing shader programs while
retaining the original surface relief and live glow. Weather aliases are explicitly
registered, rather than accepting arbitrary runtime material replacements.

For skyline cornices, height maps and normal maps continue through the original
POM shader without independently displacing the silhouette. The new terrain
profiles additionally use the bounded build-time sampling described above.
Sector-defined ceiling glow is transferred through a small live state canvas,
using each sector's current color, reach and ceiling plane. The material adds
the resulting light before surface color multiplication, preserving texture
relief. Sloped ceilings, disabling glow and runtime color/range changes are
supported. Material instances share their shader programs; per-sector metadata
is a texture binding, not a separate compiled shader. Global GLDEFS texture-glow
fallbacks are not queried by ZScript; the existing F_SKY1 ceiling sectors use
explicit sector glow instead.

The skyline portion is 648,288 triangles across all ten maps, not simultaneously in one
scene. Each mesh has a bounded render radius for engine culling. No general
performance improvement is claimed.

## Runtime and maintenance

`UTNT_SkyEdges.zc` installs nonblocking, noninteractive model actors after the
existing material handlers. Map collision, triggers, sector tags and navigation
remain unchanged. Coordinates and sector identities are checked before spawn.
Changed materials, texture transforms, heights or slopes hide invalid edges;
restoring the original conditions restores them. Static cosmetic data and the
initialized handler survive save/load without duplicate actors. New map
boundaries require regeneration; arbitrary runtime geometry changes do not
regenerate meshes. Models-disabled rendering uses a transparent fallback sprite.

The normal `tools/build_utnt.py` refreshes the edges after the organic materials.
Generated OBJ files, registrations, material modules and the output inventory
are versioned. `--check-only` rejects stale generated assets. Definition modules
remain in their standard subdirectories.

## Validation

`python -B tools/test_terrain_edges.py` verifies cap/shoulder seams, material
selection, small grass steps, narrow receiving-floor clearance, height limits,
slope normals, rounded snow seams, grass floor-plane endpoints, floor UV transforms,
height-map decoding, bounded deformation, and overlapping rock skins with
matching smooth normals and sufficient blending coverage.

`python -B tools/test_sky_edges.py` verifies material/boundary filtering, reversed
lines, shared corner positions, outward and raised geometry, slope alignment,
upper-wall clearance and pegging, higher rock crests, and generated-asset freshness. Runtime cases check exact actor/visible counts,
noncollision flags, invalid-material fallback, live ceiling-glow restoration and save/load. They capture front,
close and oblique views with the edges disabled and enabled.

Runtime cases additionally test terrain floor material changes, texture-offset
changes and a moved floor, including restoration. Client-only thinker iteration
is used for counts before and after save/load. `--mode 1 --layer 1` selects a
terrain cap camera, `--mode 2` a wall-foot camera, and `--line` an exact map edge.

Example against the built integration package:

```text
python -B tools/test_sky_edges.py --runtime --packaged --map TNT03A1 --renderer 1 --engine <uzdoom.exe> --mod tutnt.pk3
```

The upper-wall and raised-rock refinement passed all ten maps under Vulkan,
plus TNT03A1 upper walls and TNT02 rock on OpenGL, with eight runtime assertions
per case. Screenshots were inspected from front and oblique views. Eight
automated geometry/portability checks and generated-asset freshness also pass.
The earlier ceiling-glow build additionally covered TNT03A2 on OpenGL and
captured a temporary red test light. The isolated commit package and shared
integration package are validated separately.

The outdoor terrain extension passed 18 geometry checks and 14 packaged runtime
cases: all ten maps on Vulkan, snow/grass/rock comparisons on OpenGL, and a
separate wall-foot case. Each runtime case passed 11 assertions. The final cap
lighting refinement passed six further material cases across both renderers.
The shared integration package passed the normal engine build check; all 12,759
compared skyline and terrain resources matched the final isolated test package.

The rounded-snow and feathered-transition refinement passed 22 geometry
checks, all ten maps on Vulkan, and OpenGL cases for upper snow walls, grass
and wall feet (11 assertions per runtime case). The final narrow-floor grass
limit passed both renderers. All 3,116 checked rock-skyline and gravel-ledge
meshes remain byte-identical to the approved version. The normal shared build
passed its engine check; 14,081 compared feature resources match the final
isolated package. Feathered materials retain shared shader programs; their
additional translucent rendering cost has not been separately benchmarked.

The rock-ledge seam refinement passed 24 geometry checks and six packaged
runtime cases (11 assertions each): TNT01 on both renderers, TNT03B, TNTLE and
TNT04CN on Vulkan, and the reported TNT01 slope again in the shared package.
Front, close and oblique screenshots were inspected. All 7,518 models outside
rock ledges remain byte-identical to the approved version. The regular shared
build passed its engine check, with all 14,642 compared feature resources
matching the isolated test package. The overlapping rock skins add translucent
rendering and geometry; their performance cost has not been separately measured.

Renderer 1 is Vulkan; renderer 0 is OpenGL. Local screenshots and logs are in
`tutnt/.codex/logs/sky-edges-*`; structured results are under
`tutnt/.codex/validation/sky-edges/`. The test harness and its development
overlays stay under `tutnt/.codex/work/sky-edges/`. Full campaign playthrough and
software-renderer equivalence are outside these checks.
