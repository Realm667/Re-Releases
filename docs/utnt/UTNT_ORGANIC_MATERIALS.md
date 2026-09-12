# Organic surface relief

Implemented 11.09.2026. Large natural surfaces receive material-specific normal maps and parallax occlusion mapping on walls, floors and ceilings. QROCK3 now uses 7.92 map units, another 40% reduction from 13.2 following in-game artifact feedback (11.09.2026).

## Material groups

| Family | Depth in map units |
|---|---:|
| QROCK3 | 7.92 |
| QROCK1, IKWALL44 | 10 |
| QROCK4, QROCK5 | 9 |
| ROCKF5 | 8 |
| GRAVE01, GRAVE02, ROCKF6 | 5 |
| QFLAT07, ROCKF2 | 4 |
| GROUND2, GROUND3, RROCK19 | 3 |
| QGRASS, GRASS2 | 1.8 |
| ICEY | 3.5 |
| SNOW3 | 3.2 |
| OSNOW | 6 |
| OSNOW3 | 4 |

The selection follows a whole-map survey of wall extent and horizontal sector area, then visual inspection of the source graphics. These area estimates include hidden/control surfaces and are not screen coverage measurements. Dedicated skybox materials and liquids retain their existing effects. The winter extension adds ICEY, SNOW3 and OSNOW across their original, expanded and band variants, plus the original OSNOW3 transition material. Other natural families remain outside these groups.

The original diffuse images, texture scale, map geometry, collision and alignment tables are unchanged. Each selected original plus its expanded and finite-height variants receives matching data maps; legacy grass aliases remain supported without restoring previously rejected color expansions.

## Additional ground and masonry

Added 11.09.2026. This extension brought the registry to 33 families. New depths:

| Family | Depth in map units |
|---|---:|
| ASHWALL2 | 5 |
| GRAVE11, FLAT10 | 3 |
| QBRICK3, QBRICK6 | 6 |
| QWIZ, QCHURCH | 5 |
| QFLAT04 | 4 |
| ADEL_B14, ADEL_B01 | 5 |
| ADEL_F48, CITYF01 | 3 |
| BRICK9 | 4 |

Stonework and brick profiles recess darker joints while keeping the block faces broad and nearly flat. Their height is inferred from the source image; dark stains are not a geometric ground-truth height scan. Native IWAD texture compositions and repeated local patches are resolved before generating the data maps. No original diffuse art or map geometry is changed. All registry depths must be positive and at most 12 units; the new group stays at 3–6 units.

Parallax additionally fades at grazing view angles (normal/view dot product 0.08–0.30) to limit elongated samples. This reduces surface artifacts but cannot change silhouettes or remove every UV discontinuity.

## Build and integration

- Source registry: tools/organic-materials/materials.json.
- Common shader: tutnt/shaders/organic/relief.glsl.
- Generator: tools/build_organic_materials.py (NumPy and Pillow).
- Generated data: tutnt/materials/organic/.
- Generated definitions: tutnt/GLDEFS.organic, included after environment materials.
- Provenance and output hashes: tools/organic-materials/generated.json.

The generator resolves current TEXTURES definitions, crop dimensions, patch sources and logical texture dimensions. Original flat/texture namespaces take precedence over similarly named artwork patches. It reuses identical data and supplies 285 base/expanded/band variants plus the environmental aliases discovered in current surface tables. Environmental shaders are composed from the current surface.glsl template, so wetness and underwater optics remain present. It does not edit other environmental outputs.

build_utnt.py regenerates stale organic outputs before taking its immutable package snapshot. This also refreshes bindings after environmental aliases change. Only outputs previously recorded as owned organic data can be removed when obsolete. The manifest records both source and generated-file hashes.

Commands from the repository root:

    python -B tools/build_organic_materials.py --iwad /path/to/DOOM2.WAD
    python -B tools/build_organic_materials.py --check --iwad /path/to/DOOM2.WAD
    python -B tools/build_utnt.py --engine /path/to/uzdoom.exe --iwad /path/to/DOOM2.WAD

## Winter materials

Snow and ice were added on 11.09.2026. SNOW3 uses broad, rounded height variation with filtering measured in map units, so higher-resolution expansions do not become rougher. OSNOW and OSNOW3 use pale raised snow caps over recessed substrate. ICEY uses continuous shallow ice faces and grooves, variable specular strength and restrained angle-dependent sheen. Ice sheen is an ambient approximation shaded with the sector, not a reflection of map objects or transparency. Snow is matte; the existing dry rock profiles and depths remain unchanged.

No new diffuse images or terrain geometry are introduced. Footprint and weather systems keep their existing surface assignments; footprints remain planar decals and do not deform the height field. The 3.2–6-unit winter depths are intentionally below the current 7.92-unit QROCK3 relief.

## Rendering

The shader traces 16–32 height steps and five refinement steps, with at most ten additional steps for local relief occlusion. Height and normal samples remain bilinear even with unfiltered color textures. Rock/gravel use rounded fracture relief; soil/grass use shallower continuous height fields. The original palette remains in the diffuse texture.

Parallax and additional facet shading fade between 512 and 1024 map units. Normal response then fades to the geometric surface by 1536 units. Shared shader/data bindings save resources, but large close-up surfaces still cost fragment work. The fixed directional facet term is artistic shading, not a physical sun or geometry shadow; its strength is reduced for finer materials. Dynamic lights use the material normals, and rain uses the resulting normal before adding wet surface response.

POM changes visible internal relief, not silhouettes or collision. Grazing angles and abrupt UV/geometry changes retain the usual surface-displacement limits. No claim of universal low-end GPU performance is made.

## Verification

tools/test_organic_materials.py loads maps, checks native floor texture names against the material registry, captures repeatable viewpoints and exercises save/load in TNT02. Cameras for floors follow runtime floor planes, including ACS/slope changes. tools/organic-materials/views.json provides the selected rock, gravel, soil and grass locations.

    python -B tools/test_organic_materials.py --mod tutnt.pk3 --engine /path/to/uzdoom.exe
    python -B tools/test_organic_materials.py --mod tutnt.pk3 --engine /path/to/uzdoom.exe --capture --maps TNT01 TNT02 TNTLE TNT03A1 TNT04C
    python -B tools/test_organic_materials.py --mod tutnt.pk3 --engine /path/to/uzdoom.exe --capture --baseline --maps TNT01 TNT02 TNTLE TNT03A1 TNT04C
    python -B tools/test_organic_materials.py --mod tutnt.pk3 --engine /path/to/uzdoom.exe --renderer 0

The baseline overlay disables only the new organic material definitions. Runtime logs and captures are local under tutnt/.codex/logs/, reports under tutnt/.codex/validation/organic-materials/. Native reference images must be reviewed alongside the numeric checks.

Winter capture set (separate reports and images):

    python -B tools/test_organic_materials.py --mod tutnt.pk3 --engine /path/to/uzdoom.exe --tag winter --views tools/organic-materials/winter-views.json --capture --maps TNT03A1 TNT03A2

Add --baseline for the flat comparison and --renderer 0 for OpenGL. The views cover snow, snow-covered rock, transition patches, a visible ice wall.

The masonry-views.json set includes native map locations and seven QROCK3 viewpoints. probe-views.json temporarily assigns each new material to the same test wall at two angles, using the test fixture only; these are controlled material probes, not their actual placement in the released map. Pass either with --views and use a distinct --tag.

## Metal and rust (11.09.2026)

66 additional original textures bring the registry to 99 entries: QMET01–34,
ORUST01–06, METALF01–24 and ADEL_W53–54. All belong to one explicit compatibility
group with a 3-map-unit maximum trace depth, also on floors and ceilings. The
build rejects differing depths/profiles within the group or metal depths above 6.
The trace span stays at 3 units. After the neutral-height revision below, the
metal base is anchored at the geometric surface and details protrude from it.

Metal uses a shared, pointwise color-to-height transfer. ORUST01–04 have one
separate raised-rust transfer, and ORUST03 adds explicitly placed rivet caps.
There is no independent per-image contrast stretch and no artificial raised border
around each texture. Identical artwork therefore produces identical height and
surface response even when the surrounding panel decoration differs. Repeating
patches retain the same height and normals; texture definitions, original scale,
diffuse colors and UV offsets remain authoritative. Normals derive from height
changes at the actual logical pixel spacing. Matching normal neighborhoods also
produce matching normals.

A shared surface map supplies low specular strength and broad gloss. Warm corrosion
is more matte than neutral exposed metal. This color heuristic is an approximation,
not a hand-authored physical metal/roughness scan. There are no new map reflections
or emissive highlights. Current wetness behavior is composed from the environment
shader. Metal adds only a subdued facet-shading contribution (0.28).

Compatibility preserves shared source details; it cannot repair unrelated diffuse
edges, deliberate trim changes or misaligned/scaled UVs in a map. At a material
boundary, parallax also cannot sample the neighboring texture. The conservative
3-unit trace and existing grazing/distance fade limit these effects.

`tools/test_metal_materials.py --data-only` checks group completeness, depth bounds,
shared artwork transfer, repeated patches, normals, surface data and environment
aliases. With `--engine /path/to/uzdoom.exe --mod tutnt.pk3`, it creates a separate
native UDMF test room and displays related variants side by side, with frontal,
oblique and floor viewpoints, verifies actual engine assignments and saves/loads.
Add `--baseline` for flat materials or `--renderer 0` for OpenGL (default Vulkan).
Fixtures stay in `.codex/work/metal-materials/`, captures in `.codex/logs/metal-materials/`
and reports in `.codex/validation/metal-materials/`. No production map is changed.

Validation of the initial metal rollout on 11.09.2026: all 16 native room arrangements at three viewpoints
passed on Vulkan and OpenGL (48 captures each), with save/load and 240 material
assignment checks per backend. The flat Vulkan baseline uses the same camera and
point light. Vulkan was checked against the shared package; OpenGL used the same
verified material resources as a live overlay. Four visually reviewed native map
views cover ORUST05 in TNT02 and QMET13 in TNT01; `metal-views.json` records them.
A first ORUST06 camera landed outside the playable volume and is excluded from
that fixture and from the visual evidence. ORUST06 is covered in the test room.
The four retained TNT01/TNT02 views also passed against the shared package on
OpenGL, including the composed environment shader and TNT02 save/load.
Shared package build `119ec7251ffe` passed the engine check; its 384 generated
material resources and both shader source files matched the working tree.

## Neutral surface plane (11.09.2026)

All 99 registered base materials / 159 variants now encode the geometric wall,
floor or ceiling plane as gray **127**. Darker height samples recess the surface;
brighter samples protrude. The shader traces both sides of that plane. Constant
neutral regions resolve to zero displacement, including when the tracing interval
contains both positive and negative heights. Linear interpolation after binary
refinement avoids a residual global offset on such regions.

The procedural profile establishes one reference height for the whole family,
not a separate mean or contrast stretch per image. Existing rock, gravel, soil,
grass, snow and ice profiles are re-anchored around a shared reference; block-face
heights anchor brick and stonework while the joints recede. The previous relief
span budgets remain unchanged. Normals derive from the quantized height actually
sampled by the shader, so a constant neutral patch also has a flat normal.
These profile references are approximations; this is not a hand-authored height
interpretation of every natural stone, stain or architectural feature.

ORUST01–04 share a neutral base plate and raised crust. ORUST02 has approximately
1.08 units of raised roughness. ORUST03 adds domed rivet heads, including their
painted dark sides, up to approximately 1.86 units. Their shared base-image pixels
retain matching heights outside the explicitly authored rivet regions. ORUST01
and ORUST04 use the same plate/crust treatment to keep the series compatible.
The diffuse artwork and subdued metal specular response are unchanged.

The encoding is `world height = depth * 2 * (sample - 127/255)`. The generator
records actual signed extrema and checks them against a common per-profile trace
interval. Shared tracing bounds keep related variants on the same GPU program.
Legacy definitions without the new reference fields retain their original
white-zero decoding, since test overlays can leave old programs in the engine's
compilation list. All newly generated production bindings declare the gray-zero
convention explicitly.

`python -B tools/test_neutral_relief.py` checks neutral planes in every profile,
analytical plane/ray intersections, encoded extrema, flat normals, raised rivets
and shared ORUST02/03 base pixels. Temporary evidence for this revision lives in
`.codex/validation/neutral-relief/` and `.codex/work/neutral-relief/`.

Neutral-height validation: 159 generated variants and 48 analytical constant-plane
cases passed. ORUST02/03 share 3,287 equal base-artwork pixels outside authored
rivets; flat neutral neighborhoods have flat normals. Native Vulkan and OpenGL
passed all 48 metal-room views per backend with save/load; 22 controlled Vulkan
wall views cover every existing profile. Additional native checks loaded TNT01,
TNT02, TNT03A1 and TNT03A2. Two historical QROCK3 camera positions now land outside
the visible play area, so their screenshots are excluded as visual evidence;
QROCK3 is covered in the controlled profile probes. The native ICEY viewpoint is
partially obstructed; its material rendering is covered by the controlled ICEY
probe. The shared package build `ffc63dd86355` passed engine validation.


## Initial five-category rollout (11.09.2026; geometry revised below)

The 872-name map audit retained the existing 99 materials and tested 193 further
candidates (132 initial selections plus 61 conditional candidates). Native frontal,
oblique and downward views informed the final selection: 110 additions, 83 rejected.
The registry now contains 209 base materials and 285 base/expanded/band variants.
Every candidate's final decision is recorded in [rollout.json](../../tools/organic-materials/rollout.json).

| Category | Added materials | Maximum trace span, map units |
|---|---:|---:|
| Stone slabs and joints | 23 | 6 |
| Large rustic blocks | 7 | 8 |
| Wood, crates and shelves | 21 | 3 |
| Cables, pipes and technical panels | 41 | 6 |
| Riveted frames and borders | 18 | 3 |

Following the user's expanded allowance, every new material is checked against
a signed limit of -6 to +6 map units relative to gray 127. These are trace
budgets, not a uniform displacement of the surface.
The actual relief occupies only part of each budget. Gray 127 remains zero;
recesses and raised details extend from that plane. The previous 99 materials,
including the reduced QROCK3 depth and ORUST rivet geometry, keep their profiles.

The first noisy local-contrast prototype was discarded following visual feedback.
The final generator supports authored joints, complete polygonal bodies and rivet
caps. For suitable technical surfaces it also uses their baked top lighting:
a bright upper slope and a dark lower slope contribute to one raised body.
This directional reconstruction is an approximation from painted artwork, not a
measured height scan; highlights, paint and emissive colors cannot determine
geometry unambiguously. Fine wood grain, flat decorative patterns and the tested
demon ornaments were rejected where the result lacked benefit or reliable shape.

Families share a fixed plane, depth and transfer settings; printed crate variants
share the same geometric body. No per-image mean or contrast normalization moves
the surface. Altered artwork may need distinct masks, so identical heights are
only asserted for genuinely shared geometry, not arbitrary neighboring pixels.
Expanded TEKWALL4 tile/band variants preserve their pre-existing color border
blend and apply matching blending to the relief data and environmental aliases.

`tools/test_material_rollout.py --data-only` checks neutral planes, periodicity,
locality, a synthetic top-lit body, crate/girder family geometry, height limits,
normal-map dimensions and complete accepted/rejected decisions. Native fixture
runs exercise walls and floors at three camera angles, save/load, and expanded
edge variants. Use `--live --engine /path/to/uzdoom.exe --renderer 0` for OpenGL
or `--renderer 1` for Vulkan. Initial conditional trials and their screenshots
remain local and are not part of the game package.

The final data audit also removes neutral-only results; CITYF17/18 remain flat together. The stable fixture retains these flat companions to exercise adjacent unchanged surfaces.


Final validation: 96 OpenGL fixture views, Vulkan coverage of all fixture groups
and direct package probes, nine native surface checks in TNT01/TNT02/TNT03A1,
save/load, and the previous neutral/rust regressions passed. The complete shared
PK3 passed UZDoom compilation, localization/font checks and ACS compilation;
all 624 generated organic outputs were verified byte-for-byte inside the package.
A short fixed-resolution CPU-render timing probe recorded 0.217/0.259/0.513 ms
without relief and 0.335/0.272/0.340 ms with relief on the local machine. These
single-frame CPU snapshots are not GPU frame times or a campaign FPS guarantee.
The local final report is under `.codex/validation/material-rollout/final.json`.


## Geometry reanalysis (12.09.2026)

The 99 textures identified in the visual review now use new height and normal
maps from [material_geometry.py](../../tools/material_geometry.py). QTECH21 is
also updated to keep its adjoining frame family on the same neutral plane.
This replaces the rejected directional-light reconstruction for these 100 base
materials, covering 114 original, expanded and band variants. The total registry
remains 209 base materials / 285 variants / 2,746 bindings.

The new `authored` profile uses gray 127 at zero and a symmetric ray interval
of -6 to +6 map units. The 12-unit interval is the total search budget, not the
surface displacement. Actual details currently range from approximately -4.05
to +2.17 units. Flat panel faces remain flat; printed logos, color variants,
painted highlights and lower shadows do not become independent height features.
Small data maps are evaluated at twice the original texel resolution, with
normals derived from the same quantized heights and the logical map scale.
Original color artwork is unchanged.

| Materials | Construction and corrected ordering |
|---|---|
| ADEL_D11/G02/G03/GXX/S69/W39, QWOOD1/4, WOOD8 | Plank cuts, door braces and complete metal hardware above the wood |
| ADEL_F59/M02/M03/M06/R90/V98/V99 | Flat metal plate faces, recessed seams; the red strip is a shallow inset |
| IKCRATE1/2/3, IKCRATE6, IKTCR05B, QCRATE1/2 | Separate crate layouts: trapezoid handle recesses, vent slots, narrow stacked fronts and a diagonal wooden brace; printed panels remain planar |
| IKWALL10/15/18/21/23/25/26/28/30/31/50/54/55/64/69/86/88 | Framed inserts, lower polygonal openings, complete pipe sections and recessed runic strokes; dark rectangular/octagonal inserts sit behind the frame |
| QTECH09/20/21/25/26/27/30/31/32/33/34/35 | Light side panels below dark girders; separate cable, circuit-board and vent inserts |
| QTECH07/08/28/28B, OTECH2 | Domed rivets on flat plates and elongated recessed slots |
| FTUB2/3, QTECH01/02/05, QTWALL08, TECHF1/2, TECHG, OTECH6 | Cylindrical pipe/cable runs, mounting bands and recessed ventilation gaps; FTUB3 is the exact 90-degree rotation of FTUB2 |
| QCOMP1–8, QTWALL07/10/11/12, TEKWALL4 | Rectangular cabinets, planar boards, recessed sockets and connected pipe runs |
| PLATF2 | Recessed apertures and cables underneath the neutral grate |
| PANBOOK | Recessed shelving cavities, books in front of their backing and behind the wooden frame |
| ADEL_B15/Q60, CITYF14/15/16/20, QCITY01/02/03/04/16, QFLAT03, QWWALL | Shared slab/brick layouts, irregular courses and rounded block shoulders; mortar lies below the face |
| QFLAT09, SFLOOR2/3/5/6 | Shallow stamped treads on flat metal, rather than stone-like luminance relief |

Color families resolve to a common construction before normal differentiation.
CITYF14/15/16 share the same slab geometry. QTECH20/33 and QTECH25/26/34 share
their respective frame geometry. The source fingerprint includes the geometry
implementation and the effective variant model, so edits invalidate cached data.

The separately expanded artwork contains additional forms. Its broad component
boundaries are segmented into complete, flat-core bodies with rounded shoulders;
continuous dark mortar/clearance networks are recessed. This is a conservative
boundary approximation, not a measured reconstruction of every fine expanded
cable or irregular stone. Original-sized textures use the explicit constructions.
The existing TEKWALL4 tile/band border blend and environmental aliases remain.

`tools/test_material_geometry.py` checks all 114 variants, neutral neighborhoods,
physical bounds, exact family/rotation relationships, color independence for the
100 original constructions and 16 semantic front/back probes. The old neutral
plane/rust and 66-material metal regression checks also pass. All 96 OpenGL
fixture views and all 96 Vulkan views (including the corrected retry) passed
texture assignment, shader loading and save/load. There are 93 matching OpenGL
baseline captures and 12 direct Vulkan package views. Shared package build
`376b466a1ebf` passed engine, ACS, localization and font checks; all 624 organic
outputs match the source manifest byte-for-byte. The other 171 relief variants
retain byte-identical height and normal data.
The fixture caps frame rate and separates camera events from captures to avoid
occasional skipped view changes at very high frame rates.

The local review page is `.codex/work/material-reanalysis/vergleich.html`;
proofs are under `.codex/validation/material-reanalysis/`. Native comparison
images use the same camera and original artwork with relief enabled/disabled.


## Walkable relief test map

`python -B tools/build_relief_gallery.py` creates the separate addon
`tutnt/.codex/builds/tutnt-relief-gallery.pk3`. Load it **after `tutnt.pk3`**, with
DOOM2.WAD, and enter `map RELTEST`. It does not replace the shared package or
change the campaign maps. The generated local launcher
`.codex/work/relief-gallery/Relief-Test-starten.cmd` starts this combination using
its own configuration and save directory.

RELTEST contains 285 numbered rooms for all 209 registered base materials and
their expanded/band variants. Each room has matching sample walls and floor,
a texture-name sign, an overhead name display and a static light. Families stay
together in fifteen-room rows; both ends connect to side corridors. All 285
sample floors can be reached on foot. Environmental aliases that reuse these
same material variants are not duplicated as additional rooms.

The console supports `netevent reliefnext`, `netevent reliefprev` and
`netevent reliefgoto N` (one-based room number). A searchable text index is written
to `.codex/work/relief-gallery/Texturenverzeichnis.txt`. No gameplay keys are
rebound. The addon includes its own EN/DE/ES/FR map title and help text.

`python -B tools/test_relief_gallery.py` validates all floor bindings in UZDoom,
walks from the entrance into the first room, jumps across row boundaries and to
the final room, checks previous/next and save/load. Vulkan and OpenGL both passed;
the local geometry, runtime logs and screenshots are under `.codex/validation/relief-gallery/`
and `.codex/logs/relief-gallery-*`. The generator checks connectivity before writing
the addon. This is a test gallery, not a new campaign level.
