# Source impact effects - engine evidence

Direct UZDoom 5.0.1 OpenGL and Vulkan captures, without retouching. The two impact
runs each pass 44 assertions and execute all ten camera/shader checks. Restored
finale: 72 assertions; actual level ending: 27; local cooperative peers: 55 each.
The first restore run exposed a narrow test delivery window (saved age 75,
check arrived at 103 rather than at most 100). The fixture now tolerates through
105 and the full restore run passes; the runtime clock was unchanged.

OpenGL, restored finale, actual ending and coop use the official full live-tree
integration build identified in package-check.json. Initial Vulkan impact tests
use the current shared package plus this feature's runtime files. Final shared
publication uses tools/build_utnt.py on the live repository, never this test ZIP.
The only post-test runtime change is a shader comment clarifying HUD composition.

Orange/red lights reuse the nine existing anchors. Three bounded light-burst
groups and 18-tic local refraction pulses use the saved defeat clock. Quality
zero, reduced effects, shader toggle, looking away and map cleanup are exercised.
Each positive particle check verifies actual outward travel; reduced effects
leave two dim rays and quality zero leaves none. Images do not represent a
frame-by-frame performance benchmark or a complete campaign playthrough.
