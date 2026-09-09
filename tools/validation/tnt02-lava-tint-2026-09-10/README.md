# TNT02 lava spill color seam

The rounded model does not inherit sector wall special colors. TNT02's lower
wall on line 172 inherited orange (0xEB8100) from sector 53, producing a red
step where the model feathers into the wall. Setting neutral own colors on
the lower wall removes the reproduced seam while retaining the lava shader.

Apply the same correction to all five detected lava lower sides in TNT02
that inherit a non-neutral sector wall tint: lines 172, 179, 374, 2345, 2823.
Only their lower texture color overrides change. Sector colors, other wall
tiers, geometry, light levels, ACS and every non-TEXTMAP lump are preserved.
The temporarily equalized line 374 retains the correction for later movement.

OpenGL and Vulkan each passed 20 existing runtime checks including save/load.
Before/after views use the same camera and frozen shader time (3.75 seconds).
The Vulkan comparison reproduces and removes the red band on line 172.
Structural comparison verifies that exactly 15 UDMF properties were added
across five sidedefs and lava edge registration is unchanged.

OpenGL required a cold-start timeout of 180 seconds and finished in 120.52
seconds; the initial 60-second run timed out before entering the map.

The full integration package tutnt-tnt02-fix.pk3 passed engine compilation
and 20 more TNT02 Vulkan runtime checks with native animated shaders.
Its map payload matches the corrected source WAD byte for byte.
The usual tutnt.pk3 could not be replaced while held open by another application.
