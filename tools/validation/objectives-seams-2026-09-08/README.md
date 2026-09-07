# Objective artwork joins — 2026-09-08

The original fractional destination rectangles fail six of sixteen pixel checks:
white/black contrast backgrounds remain fully visible through one-pixel gaps.
After deriving all three cap rectangles from shared integer edges, all sixteen
checks pass in both Vulkan and OpenGL. Four scale/height pairs cover both joins
at full and half opacity; screenshot subtraction also detects double blending.
The addon draws the same DrawArtwork method used by the full plaque. The two
white-background screenshots preserve the reproduced fault and its correction.

The rebuilt package passes engine validation and the TNTLE controls regression
(75 assertions, including 0.2-second fade endpoints/reversal and save/load).
Its objective renderer matches the working source byte for byte. No bitmap,
ACS, localization or gameplay changes were needed. Package hashes are recorded
in results.json. Independent checkout work is excluded from this commit.
