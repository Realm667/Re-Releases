# Portal interior artwork

`tutnt/materials/portal/hell-curtain.png` is original artwork generated with the
built-in Imagegen tool on 2026-09-09, using the user's approved portal mockup as
a style reference. The generated PNG is copied without raster edits. It is a
1254 × 1254 RGB material, not a screenshot or a seamless noise map.

Art direction: front-facing square interior of an infernal portal, torn dark
crimson smoky curtains, fine glowing red threads, strong asymmetry, a winding
tall central black chasm occupying about 40 percent, a tendril at lower left
and upper right, dark red masses cut off at the edges. No circular spiral,
eye, funnel, faces, skulls, stars, baked embers, frame, HUD or surrounding room.

Runtime uses three independently warped depth layers, camera parallax and
normal relief derived from the same artwork. Embers remain live local actors.
The existing procedural flow map supplies only the displacement field.
`tools/build_portal_assets.py` generates those auxiliary legacy assets; it does
not regenerate or overwrite this authored curtain image.
