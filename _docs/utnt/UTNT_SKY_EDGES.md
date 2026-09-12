# Natural skyline edges

Updated: 12 September 2026.

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

Only one-sided walls ending at a sky ceiling and lower walls against closed
sky sectors qualify. Both visible and backing ceilings must be F_SKY1 for the
latter case. Ordinary outdoor steps and open elevated terraces are excluded,
as are horizon/portal lines and walls too short to contain the lower join.

Current generated coverage:

| Map | Edges |
| --- | ---: |
| TNT01 | 106 |
| TNT02 | 185 |
| TNT03A1 | 179 |
| TNT03A2 | 32 |
| TNT03B | 40 |
| TNT04A | 45 |
| TNT04B | 199 |
| TNT04C | 17 |
| TNT04CN | 22 |
| TNTLE | 282 |

Total: 1,107 edges, comprising 871 rock and 236 snow/ice edges. The complete
manifest records each map, line, side, material and generated mesh.

## Geometry and material continuity

`tools/build_sky_edges.py` generates OBJ meshes and registrations without
rewriting WADs. Each cross-section curls over the skyline, projects toward the
playable side and returns to the original wall. Snow uses an interpolated soft
profile; rock uses fewer profile divisions and finer irregularities. Base radii
scale with wall clearance, capped at 24 map units for snow and 22 for rock;
spatial variation and separately raised crests produce the final silhouette.
Connected ends share positions and bounded miter directions. Unmatched ends
taper into the wall so architecture and material changes retain their borders.

Authored Plane_Align slopes, triangular vertex heights and plane-copy setup
are resolved during generation. UVs use the current area-expansion mappings,
wall pegging, scales and offsets. Texture distance follows the curved profile
and meets the wall at its lower seam. Generated material wrappers reuse the
existing diffuse textures, normal/height maps, parallax and weather state;
a restrained orientation-dependent shade makes the underside readable without
adding a dark border to the vertical join. Weather aliases are explicitly
registered, rather than accepting arbitrary runtime material replacements.

Height maps and normal maps continue through the original POM shader on the
curved surface; they do not independently displace the mesh silhouette.
Sector-defined ceiling glow is transferred through a small live state canvas,
using each sector's current color, reach and ceiling plane. The material adds
the resulting light before surface color multiplication, preserving texture
relief. Sloped ceilings, disabling glow and runtime color/range changes are
supported. Material instances share their shader programs; per-sector metadata
is a texture binding, not a separate compiled shader. Global GLDEFS texture-glow
fallbacks are not queried by ZScript; the existing F_SKY1 ceiling sectors use
explicit sector glow instead.

The total is 265,410 triangles across all ten maps, not simultaneously in one
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

`python -B tools/test_sky_edges.py` verifies material/boundary filtering, reversed
lines, shared corner positions, outward and raised geometry, slope alignment,
and generated-asset freshness. Runtime cases check exact actor/visible counts,
noncollision flags, invalid-material fallback, live ceiling-glow restoration and save/load. They capture front,
close and oblique views with the edges disabled and enabled.

Example against the built integration package:

```text
python -B tools/test_sky_edges.py --runtime --packaged --map TNT03A1 --renderer 1 --engine <uzdoom.exe> --mod tutnt.pk3
```

The initial geometry rollout passed all ten maps under Vulkan. The final
ceiling-glow build passed TNT02 on Vulkan/OpenGL, TNT03A1 and TNT03B on Vulkan,
and TNT03A2 on OpenGL, with eight runtime assertions per case. Screenshots were
inspected for the natural glow and a temporary red test light. Six automated
checks cover the geometry contracts, Vulkan include-name portability and asset
freshness. The isolated commit package and shared integration package are
validated separately.

Renderer 1 is Vulkan; renderer 0 is OpenGL. Local screenshots and logs are in
`tutnt/.codex/logs/sky-edges-*`; structured results are under
`tutnt/.codex/validation/sky-edges/`. The test harness and its development
overlays stay under `tutnt/.codex/work/sky-edges/`. Full campaign playthrough and
software-renderer equivalence are outside these checks.
