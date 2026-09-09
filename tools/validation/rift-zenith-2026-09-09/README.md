# TNT04CN dark zenith validation, 2026-09-09

UZDoom 5.0.1: OpenGL and Vulkan each pass 21 assertions (42 total), covering sky selection, removal of the obsolete star camera, preserved secondary viewpoint and Source, original sector count, save/load, TNT04C/B/A map guards and return to TNT04CN. Twelve camera views include the starting area, different sides of the beam, cardinal directions, zenith, black nadir, floating rocks and the actual upper portal room.

Visual inspection confirms a localized orange opening at the geometric beam endpoint from multiple viewpoints and continuous clouds across the stacked portal. The Source beam, forcefield, map geometry and ACS are unchanged; the complete map hash is in verification.json. Neither new production image contains a beam.

All 12 static cubemap edges are pixel-identical; the nadir is black. All 18 TNT04A/B/CN shader faces retain the exact shared comet implementation. A geometry-derived check confirms the upper beam center, 20000-unit ceiling and original (10496,128) portal translation.

The complete PK3 compiles all 14 ACS modules without bytecode changes and is accepted by the engine. Eighteen relevant runtime resources match the checked source byte-for-byte. A further packaged Vulkan smoke run passes six assertions and captures package-view.png. Working-tree runtime checks include concurrently present local project work; the separately staged commit tree is compile-checked before commit to isolate this patch from that work.

Original gameplay particles occasionally enter the test camera, especially in later captures; they are not painted in the sky. No image has been retouched. Full temporary motion/save captures remain in the local test output.
