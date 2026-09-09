# Lava lip validation — 2026-09-09

UZDoom 5.0.1 / RTX 4080. Ten structural tests passed. The angled fixture passed
12 assertions in each of OpenGL and Vulkan: nonblocking visible actors,
vertical motion, non-lava fallback, switching both lava-floor and fall variants,
restoration and save/load without duplicate actors. TNT02 passed 20 checks:
nine registered actors, with the sector-109 edge correctly hidden after the
map's startup script equalizes it with sector 113. TNTLE passed 238 checks in
each backend. Its Vulkan run loads the actual full `tutnt.pk3`, with no shader,
material, model or map override; the add-on supplies only a camera/test handler.
The two local coop peers each passed four checks, including vertical motion.

TNTLE-0 images use the same frozen material time for direct visual comparison.
Packaged images use the archive's unmodified animated shaders; their differing
animation phase must not be interpreted as a geometry/material regression.
The curved lip visibly covers the old sharp edge, and blends to both existing
surfaces. Source maps and gameplay collision are not rewritten.

`package.json` records the full integration archive and verifies each owned
runtime resource byte for byte against its packaged entry. This is a focused
render/runtime regression, not a complete campaign or performance benchmark.
