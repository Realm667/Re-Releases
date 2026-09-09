# TNT04CN: The Beginning and The End — cosmic rift sky

The approved epic mockup is integrated as a full spherical cosmic abyss: a huge torn copper-gold nebula arc, crimson/violet cloud depth, fixed floating basalt masses and the same animated comets used in TNT04A/B, including their size variation and rare dispersing groups.

## Integration

- `UTNTRiftSkyHandler` runs only in TNT04CN. It removes only the untagged original star camera at (-7296, -5056), invoking the engine's normal SkyViewpoint portal cleanup, and selects URFSKY.
- The second viewpoint remains present. Map files, geometry, sector lighting, actors other than the obsolete decorative camera, ACS, the Source battle and its effects are not edited.
- World load/save restoration reapplies the sky idempotently. TNT04A, TNT04B and TNT04C keep their own sky systems.
- The primary image projection preserves the approved player view at (1440, -2080, 3200), yaw 315, pitch -12. Other directions and the view down into the void use the complementary surrounding nebula.
- Rock silhouettes remain fixed while the nebula drifts slowly. Comets are drawn behind these rocks using `tools/war-comets.glsl` without altering its appearance, flight timing, size distribution or fragmentation probability. No new gameplay random state, sounds or damage.
- The six 1024-square cube faces are static fallbacks. Hardware materials reconstruct a continuous world ray across every face and include pole caps and boundary feathering.

## Rebuild and checks

Run `python tools/build_rift_sky.py`; `build_war_sky.py` also regenerates this sky so a shared comet edit propagates to all three maps. Requires NumPy and Pillow. Artwork, approval and prompts: `tools/artwork/rift/`.

`python tools/test_rift_structure.py` verifies all 12 cube edges, material registration and identical shared comet code across 18 faces. `tools/test_rift_sky.py` checks real OpenGL/Vulkan views, movement, save/load, preserved secondary camera/sector count/Source, and map transitions. Runtime evidence is under `tools/validation/rift-sky-2026-09-09/`.

## Validation result (2026-09-09)

UZDoom 5.0.1 accepted all 14 compiled ACS modules and the packaged resources. The final package passed 42 assertions across OpenGL and Vulkan, including save/load and transitions to TNT04C/B/A and back. All 12 static cube edges match within one channel value; all 18 TNT04A/B/CN shader faces contain the same comet source.
