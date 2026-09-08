# TNT03B caldera artwork

Generated with the built-in Imagegen tool on 2026-09-08 from the user-approved screenshot mockup. These are new environment assets for UTNT, not copied game textures.

Runtime source: `tutnt/graphics/caldera/panorama.png` (1774 × 887) and `tutnt/textures/UCBASALT.png` (1254 × 1254). The image tool did not produce the requested larger resolution, so the package uses the actual source resolution. The discarded enlargement was not used.

`python tools/build_caldera_sky.py` deterministically projects the authored panorama into six 768 × 768 faces, softens its rear wrap, and regenerates the spherical cloud shaders. Requires Pillow and NumPy. Projection raises the panorama's authored horizon to fit the map's camera, then applies the same restrained canopy exposure as the runtime shader. The source image stays unchanged.

The near foothills are actual sloped sectors. The detailed distant mountains, valley haze, and smoke silhouettes belong to the panoramic artwork. Slow motion is restricted to high clouds; mountain silhouettes and distant smoke remain stationary. No physical volumetric rendering is claimed.

The approved mockup and the exact generation prompts are retained here for reference.
