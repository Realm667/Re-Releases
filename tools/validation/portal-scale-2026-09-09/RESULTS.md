# Larger portal intake volume — 2026-09-09

The user's green outline calls for the particle intake to extend across a larger
area in front of the portal. Start positions are now independent of the smaller
target area: 1.6 times the portal width, 96% of its height, and depth scaled from
128–320 map units for a 192-unit opening. Both mapped sizes and automatic sources
share this code. Curved paths converge on the existing targets. Emission rates,
lifetimes, particle sizes, budgets and the 128-unit postprocess gate are unchanged.

UZDoom 5.0.1, Vulkan, TNT03B, ordinary first-person camera at the same oblique
position, noclip/fly. The baseline overlays the committed previous portal ZScript;
the after run uses the new complete package with only a measurement handler.
Across the sampled particles the start span changes from 144.8 to 297.2 units,
and depth changes from 64.2–144.0 to 128.5–319.9 units. The matching screenshots
show the embers spreading into the room. Values are sampled extents, not the
theoretical extremes. Both measurement checks pass.

The existing Vulkan suction suite also passes for both 128/192 decorations:
activation, distance gates, rendering, settings, shutdown, save/load and wall
occlusion. Four runs, 200 logged passing assertions
(including the baseline measurement). No ACS or map data changed in this fix.

Test package: tutnt-portals-scale.pk3, build 6218da0df2be.
SHA256: f240e15e671f5fe6e779c05421ad8b5e672fe405eda28666905d81c0215c716d
The package contains the current shared working tree, including other tasks'
local changes. The portal ZScript matches the tested source byte-for-byte.

The normal tutnt.pk3 was locked by another program during publication; the fully
built scale package remains available separately. This record describes that
tested package rather than claiming that the locked normal package was replaced.
