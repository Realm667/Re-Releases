# Lava crust height asset

`tutnt/materials/lava/crust-height.png` is a 1254 x 1254 RGB grayscale image
generated with the built-in Imagegen tool. It is sampled as height data; the
shader derives charcoal color, normals and parallax intersections from it.
The user supplied a geological reference photograph. That photograph is not
included in the package. The generated asset has an independent arrangement.

The shader explicitly filters heights and masks distorted atlas boundaries;
the generated image alone is not relied upon to have perfectly matching edges.

## Generation prompt

Create a NEW original grayscale HEIGHT MAP texture asset for a 3D lava shader, using the attached photograph ONLY as a concrete geological shape reference. Not a cleaned copy of the photograph. Square 1024x1024 or higher, seamless tileable orthographic top view. Capture the reference's sharply broken angular black basalt plates with curled rope-like folds, overlapping wrinkled rock laminae, chipped raised rims, fine rough fracture striations. Approximately 12-20 irregular medium sized plates of varied shape, interspersed with branching open gaps. This is a technical displacement height map, NOT a color photograph: pure BLACK flat zero-height channels between rocks occupying 25% of area, dark gray steep bevelled sides, medium/light gray rock plate tops at varied elevations 40-80% gray, lighter raised folded ridges on each top. Lighter means physically higher everywhere, no directional lighting, no cast shadows, no specular highlights, no red/orange, no perspective, no ambient background gradient. Broad plateau tops should contain clearly sculpted flowing folds like reference, not smooth featureless blobs, not round pebbles. Very fine realistic craggy detail. Seamless all edges. Full bleed asset only, absolutely no text, logos, watermark, labels, border or UI. Original independent arrangement distinct from reference.
