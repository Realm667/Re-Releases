# Expanded rock textures

The approved QROCK3X8 material is integrated on TNT04B's southern rock front
beside the lava lake: 18 connected linedefs, 23 upper/middle/lower sections.
It covers 1024x1024 map units per repeat, eight times QROCK3 in each direction.
The original material remains available for small surfaces and other maps.

## Alignment and scope

U follows cumulative actual line length around corners. All selected sections
share vertical anchor Z=512; per-tier offsets compensate original peg rules
and sector texture-plane references. Global offsets, peg flags, geometry,
numbering, actors and compiled map scripts are unchanged. The 17 internal
joins differ by at most 8.48e-10 world units. This is a UV continuity check;
it does not guarantee perfect generated contours at image wrap boundaries or
at the two ends where the expanded material meets the old material.

## Verification

Build using tools/build_utnt.py, then run tools/test_rock_expansion.py with
--engine, --iwad and --work-dir. The fixture checks actual engine texture size
and all 23 mappings before and after save/load, on OpenGL and Vulkan. Test
handlers and cameras stay outside tutnt and are not shipped. Integration
records are under tools/validation/rock-expansion-2026-09-09.

## Extending to other surfaces

1. Run `python tools/audit_texture_coverage.py --output coverage.json`.
   It ranks authored wall area and shared-endpoint groups. Slopes, 3D floors,
   moving sectors, masked two-sided middles and visibility require inspection;
   it is not a screen-visibility calculation and never edits maps.
2. Review remaining QROCK3 fronts in TNT04B, then high-coverage QROCK3 areas in
   TNT04CN, TNTLE, TNT02 and TNT04C. Reuse this approved material at its scale.
   Candidates for separate new assets include QROCK1 in TNT04B, QROCK5 in
   TNT04CN/TNTLE, QROCK4 in TNTLE and ASHWALL2 backdrops (inspect visibility).
3. Per new material: retain the original as reference, generate a larger
   unique field at the intended feature size, inspect 2x2 wraps and an in-game
   comparison, then approve the image before applying it across maps.
4. Per selected surface: record explicit map/line/tier scope, traverse actual
   wall lengths, compensate vertical anchoring and preserve unrelated fields.
   Branches, closed loops, mixed scales, moving planes and transitions require
   explicit seam placement or separate groups, not blind global autoalignment.
5. Check mapping continuity, map scope and package resources; compare matching
   camera views and test save/load. Integrate in small material-based batches.

Organic surfaces are good candidates. Masonry and panels need their module
spacing preserved; animated liquids and sky assets need separate treatment.
Floors and ceilings use different mapping and are outside this wall scanner.
