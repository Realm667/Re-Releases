# Approved TNT04CN cosmic rift artwork

The user approved `approved-mockup.png` and requested implementation with the same appearance. `clean-background.png` removes the playable foreground and comets. Runtime layers in `tutnt/graphics/rift/` separate the nebula from blue-keyed floating basalt and provide complementary surrounding space.

Created with the built-in Imagegen tool. Complete prompts are in `prompts.json`; original mockup prompt is in `mockup-prompt.txt`. No raster source is painted or retouched by the build scripts. `tools/build_rift_sky.py` projects the supplied textures into six static engine cube faces and emits matching animated materials.

The main projection uses the approved camera yaw 315 degrees, pitch -12 and widescreen 90-degree base FOV. A feathered boundary joins the primary view to the surrounding panorama. Pole caps use planar coordinates. The rock layer is keyed before bilinear interpolation to prevent blue fringes. Slow independent nebula movement and the exact shared TNT04A/B comet shader are runtime effects; baked images contain no comet trails.

The mockup is a visual reference. The playable architecture, actors, lighting, and scripts remain those of the actual map.
