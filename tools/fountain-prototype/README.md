# Water-flow motion prototype

This isolated add-on demonstrates one narrow B1C fountain. It does not replace
campaign actors, alter tutnt.pk3, or change the accepted player splash and smoke.
Load after tutnt.pk3 and run `map UTNTFIRE` to enter the demonstration room.
The new fountain starts automatically in front of the fixed initial viewpoint.
Console controls: `netevent flow_old`, `netevent flow_new`, `netevent flow_off`,
`netevent flow_on`. These affect only the demonstration fountain.

The prototype retains the original B1C emitter schedule, speed 5, gravity .125,
81–101 degree pitch range, radius 1, height 2 and three size variants. Its
visuals have three stages: overlapping animated liquid segments, torn fragments,
and fine spray. Procedural shader materials vary the contour, moving density
and edge highlights; the legacy teardrop sprite is not used for airborne water.
Very short four-tic wakes connect motion without long comet tails. The source
uses the existing small crown animation and flat rings on water impacts.
All extra visuals use the ambient budget. FWATER1 is only an opaque material
carrier; the shader creates the actual silhouette and translucency at runtime.
There are no new generated raster assets in this prototype.

Set UTNT_ENGINE and UTNT_IWAD, then run:
`python tools/test_fountain_prototype.py --renderer 0`
and `--renderer 1` for OpenGL and Vulkan. Tests cover phase progression, unchanged
missile dimensions/physics, finite wake scales/lifetimes, activation/cleanup and
save/load. `--capture` records 64 screenshots at two-tic intervals (35 Hz game
time), for a short motion study. Capture commands stay below the console's line
length limit. The prototype remains an art-direction experiment for review.
