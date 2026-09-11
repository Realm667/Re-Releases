# ENDMAP Ember Fracture

Implemented from the approved 11 September 2026 concept. The built-in Imagegen tool produced the diffuse art using the approved mockup as reference; the generation prompt is in prompt.txt. The runtime diffuse PNG is the source artwork, preserved without resampling or color edits.

- Source: tutnt/materials/credits/fracture/diffuse.png, 1254 × 1254 pixels.
- Display: UECRACK, 192 × 192 map units (150% of the initial implementation). Pan (4576, -352) centers it at (-4480, -448).
- Data generator: python -B tools/build_ending_fracture.py; verification: add --check.
- Data: brightmap.png, height.png, normal.png in the same material folder.
- Definitions: tutnt/credits/ember-fracture.gldefs, included once through credits/ash-ember.gldefs.
- Shader: tutnt/shaders/credits/ember-fracture.fp uses the shared signed-height organic POM implementation.

The emission mask selects saturated amber interiors, not neutral/brown gravel. Channels expand from that mask to include the dark crevice banks; bright cores are recessed, not treated as high terrain. Normals derive from the quantized height in world units and use the existing green-up convention. Black/white height is never inferred from the bright flame alone. Height 127 is the map plane, maximum depth parameter is 4 units; generated range is approximately -3.8 to +0.6 units. The maps are registered pixel-for-pixel; the POM hit UV samples diffuse and brightmap together via SetMaterialProps.

A round world-space feather blends back to the original ROCKF7 texture and neutral geometric normal. Original ROCKF7 phase is maintained by subtracting the material pan from its underlay UVs. The world-space mask suppresses repeated fissures on adjacent slopes. No glossy/specular response is added. Existing view-distance and grazing-angle fades bound the parallax effect. This material changes shading, not physical collision or silhouettes.

Map sectors 501 and 513 become coplanar at z=392, share lighting/tag/material and retain invisible internal boundaries, existing BSP, line identifiers and script timing. Two TID-7 actors lose their old four-unit relative height to preserve their absolute z after the former lava floor is raised by four units. Camera targets and authored lightning remain in place.

Native credits spark tests check shared floor material, continuous UV phase, removal of the height step, focus, line of sight, save/load, actual lightning pulses and transition to THE END. Additional visual checks should compare a close oblique view with/without parallax; data generation alone is not proof of in-engine appearance.

For native oblique/overhead captures use tools/test_ending_fracture.py with --out, --work, --engine and --iwad; --baseline disables POM while retaining the material and normalmap for comparison. Final stage enlargement also assigns the material to sectors 480 and 502–512 without changing their heights or lights. Only the unique world-space crater mask reveals the fracture.
