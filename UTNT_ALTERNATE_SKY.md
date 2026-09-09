# TNT04C alternate ending sky

Implements the two approved TNT04C mockups: dark charcoal/umber clouds with amber,
ochre and gold QLAVA reflections; a compact cloud opening at the original beam;
two distant mountains, two cuboid antenna platforms and one small debris group.
The existing level beam is never drawn into a sky raster or shader.

## Runtime

`UTNTRiftSkyHandler` selects `UACSKY` only for TNT04C. After the original SkyPicker
actors initialize, it removes the three decorative SkyViewpoints at X=6512,
Y=-432/-176/80 using the engine's portal cleanup. It changes the 68 original
STARSKY1 ceilings to F_SKY1 at runtime. Gameplay geometry, lava, scripts, Source
and stacked sector portals remain intact. TNT04CN retains URFSKY.

The map's tag-88 cylinder spans X=450..1474 and Y=13122..14018; its midpoint is
(962,13570), with ceiling Z=-992. The 8000-unit cloud plane is anchored to that
endpoint. The generated opening is centered at UV (0.5,0.425). Its interior is
empty; nearby cloud detail drifts gently. No TNT04CN portal translation applies.

Five world-space cards reuse the CN ray/plane intersection and premultiplied
blue-key bilinear sampling. Distances range from 36000 to 100000 world units;
elliptical periods are 220–280 seconds with opposing directions, small amplitudes
and less than a quarter degree of rocking. Nearer platforms show stronger parallax.
The material protects the opening from foreground cards. Rock and platform light
uses near-neutral charcoal/metal (RGB weights 1.02,1.0,0.97), matching the real map
geometry and removing the former uniform gold/brown cast. Source PNGs remain
TrueColor RGB; no PLAYPAL quantization is applied. Clouds retain their QLAVA palette.

One comet track reuses `WarCometLight` unchanged from TNT04A/B/CN. Each 65-second
cycle has a brief slow flight followed by an empty interval. Size varies between
flights; this variant never calls the splitting-group routine.

## Build and assets

Run `python tools/build_alternate_sky.py` with NumPy/Pillow. This creates six 1024px
fallback cube faces, six materials and GLDEFS.alternate. GLDEFS.rift includes the
variant; the CN builder preserves that include. Fallback faces are static at the
reference eye (962,13570,-5350); animation and parallax require hardware materials.

Production art was created using the built-in Imagegen tool from the approved
mockups. Source PNGs are in tutnt/graphics/alternate. The existing CN rock atlas
and shared material functions are reused. Prompts and approved references are in
tools/artwork/alternate. Build-derived cube projection and chroma-key compositing
do not alter those source PNGs.

Validation evidence: tools/validation/alternate-sky-2026-09-09.
