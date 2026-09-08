# TNT04B ash sky artwork

The user approved the courtyard and panorama mockups and explicitly authorized
integration with the same comets as TNT04A. Both approved references are here.
Artwork was authored/edited with the built-in Imagegen tool; exact production
prompts are in prompts.json. Source images retain their authored pixels.

Runtime/source artwork in tutnt/graphics/ash:
- panorama.png: approved panorama with baked comets removed.
- reverse.png: complementary opposite hemisphere, avoiding repeated mountains.
- mountains-key.png and reverse-key.png: the same landscapes with blue-key skies.
- clouds.png: independent cloud-only overhead tile matching the approved palette.

The shader keys each mountain texel before bilinear interpolation and removes
blue spill. All comets are supplied separately by tools/war-comets.glsl.
CPU reprojection produces the six static fallback faces; no code-painted art
or image retouching is substituted for the authored imagery.

The two landscape layers are fixed in world direction. Spherical cloud sampling
blends into a planar overhead projection, avoiding a pinched pole. Two cloud
layers use the same continuous clock in every lightning texture state.
