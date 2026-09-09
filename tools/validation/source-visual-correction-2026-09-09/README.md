# Source visual correction — engine evidence

All PNGs here are direct UZDoom 5.0.1 captures of the isolated candidate PK3.
They are not the AI paintovers in tools/artwork/source.

The old build lost closed-shield opacity in 44 of 136 sampled render frames,
including alpha zero. Network-event assertions alone missed it: ACS wrote alpha
later in the same frame. The new render-time probe checks the closed membrane.
Original scripts 701 and 121 only animate legacy alpha; the Source stops them
and explicitly selects additive blending. Script 122's collision/open-window
timing, attack scripts, all monster states and the map remain unchanged.

OpenGL and Vulkan each pass 82 assertions plus all sampled closed render frames.
Both local cooperative peers pass with opposing FX settings. Save/load, open and
closed shield, attack announcements, reduced FX, death and TNT04C isolation pass.
The GL suite needed a 180-second timeout on this machine (final run about 91 s;
Vulkan about 48 s); an earlier 100-second GL run timed out without an assertion
failure. These are functional runs and visual checks, not a frame-rate benchmark.

The reference image uses the test's normal arena position with pitch -22, rather
than -15, to include the whole seal. Front, side and wide views are also tested.
This is a closer implementation of the approved composition, not a claim that
an AI paintover can be reproduced pixel for pixel from arbitrary player views.
