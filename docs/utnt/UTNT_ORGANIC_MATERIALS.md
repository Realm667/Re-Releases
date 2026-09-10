# Organic surface relief

Implemented 11.09.2026. Large natural surfaces receive material-specific normal maps and parallax occlusion mapping on walls, floors and ceilings. QROCK3 uses the reviewed depth of 13.2 map units, 40% below the original 22-unit prototype.

## Material groups

| Family | Depth in map units |
|---|---:|
| QROCK3 | 13.2 |
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

## Build and integration

- Source registry: tools/organic-materials/materials.json.
- Common shader: tutnt/shaders/organic/relief.glsl.
- Generator: tools/build_organic_materials.py (NumPy and Pillow).
- Generated data: tutnt/materials/organic/.
- Generated definitions: tutnt/GLDEFS.organic, included after environment materials.
- Provenance and output hashes: tools/organic-materials/generated.json.

The generator resolves current TEXTURES definitions, crop dimensions, patch sources and logical texture dimensions. Original flat/texture namespaces take precedence over similarly named artwork patches. It reuses identical data and supplies 58 base/expanded/band variants plus the environmental aliases discovered in current surface tables. Environmental shaders are composed from the current surface.glsl template, so wetness and underwater optics remain present. It does not edit other environmental outputs.

build_utnt.py regenerates stale organic outputs before taking its immutable package snapshot. This also refreshes bindings after environmental aliases change. Only outputs previously recorded as owned organic data can be removed when obsolete. The manifest records both source and generated-file hashes.

Commands from the repository root:

    python -B tools/build_organic_materials.py --iwad /path/to/DOOM2.WAD
    python -B tools/build_organic_materials.py --check --iwad /path/to/DOOM2.WAD
    python -B tools/build_utnt.py --engine /path/to/uzdoom.exe --iwad /path/to/DOOM2.WAD

## Winter materials

Snow and ice were added on 11.09.2026. SNOW3 uses broad, rounded height variation with filtering measured in map units, so higher-resolution expansions do not become rougher. OSNOW and OSNOW3 use pale raised snow caps over recessed substrate. ICEY uses continuous shallow ice faces and grooves, variable specular strength and restrained angle-dependent sheen. Ice sheen is an ambient approximation shaded with the sector, not a reflection of map objects or transparency. Snow is matte; the existing dry rock profiles and depths remain unchanged.

No new diffuse images or terrain geometry are introduced. Footprint and weather systems keep their existing surface assignments; footprints remain planar decals and do not deform the height field. The 3.2–6-unit winter depths are intentionally below the approved 13.2-unit QROCK3 relief.

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
