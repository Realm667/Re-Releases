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

The generator resolves current TEXTURES definitions, crop dimensions, patch sources and logical texture dimensions. Original flat/texture namespaces take precedence over similarly named artwork patches. It reuses identical data and supplies 159 base/expanded/band variants plus the environmental aliases discovered in current surface tables. Environmental shaders are composed from the current surface.glsl template, so wetness and underwater optics remain present. It does not edit other environmental outputs.

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
The sampled height range is shallower than the trace bound (about 0.15–2.55 units
below the original plane).

Metal uses one fixed, pointwise color-to-height transfer across the complete set.
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

Validation on 11.09.2026: all 16 native room arrangements at three viewpoints
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
