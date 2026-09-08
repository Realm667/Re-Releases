# TNT03B: detailed terrain and faster vortex

UZDoom 5.0.1, 1920 × 1080, OpenGL and Vulkan. Each run passed six runtime/save-load assertions. The annular comparison measures approximately 4.3 degrees over five seconds. The horizon control differs by 0.0103/0.0921 RGB levels; the tolerance is one quarter of an 8-bit channel step to allow subpixel camera/render rounding. The low panorama's shader path has no time dependency.

Terrain: 192 angular samples and 18 radial bands; 6,529 sectors replace 769. All pre-existing gameplay blocks, things and non-node lumps match the supplied working baseline. Shared slope endpoints agree within 0.000001 map units. The default camera stays at (18000,18000,0), with the miniature camera unchanged.

The tested local snapshot includes unrelated working changes, which are excluded from this commit. The committed WAD is generated from the parent revision using the same terrain generator; its gameplay content therefore remains that of the parent revision. Validation fixtures are not packaged.

Repeat: `python tools/test_sky_motion.py --map TNT03B --engine <uzdoom.exe> --iwad <doom2.wad> --mod <pk3>`.
Terrain: `python tools/refine_caldera_terrain.py --input <coarse-baseline.wad> --output <detailed.wad> --zdbsp <zdbsp.exe>`, followed by `python tools/test_caldera_detail.py <coarse-baseline.wad> <detailed.wad>`.
