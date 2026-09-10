# TNT04C alternate ending sky

Implements the two approved TNT04C mockups: dark charcoal/umber clouds with amber,
ochre and gold QLAVA reflections; a compact cloud opening at the original beam;
two distant mountains, two cuboid antenna platforms and one small debris group.
The existing level beam is never drawn into a sky raster or shader.

## Runtime

`UTNTRiftSkyHandler` selects `UACSKY` only for TNT04C. The three original
SkyViewpoints at (6512,-432,580), (6512,-176,500), (6512,80,470) and all 770
original SkyPickers remain intact. They preserve the background mountain/beam
and its different framing in the three height sections. After the pickers
initialize, the handler changes the 68 STARSKY1 ceilings to F_SKY1 and applies
sector special 90 only to the shared viewpoint sector (182). Applying it to
the decorative mountain sectors creates black ceiling cutouts. The retained
SkyViewpoint portal also excludes its sky-room pass from SSAO in the engine.
Existing lighting thinkers, gameplay geometry, lava, scripts and Source remain.
TNT04CN retains its existing URFSKY handling.

The 47 TorchTree, BigTree and Stalagtite decorations in the miniature sky room
follow their sector's transferred floor light each tic. Changing STARSKY1 to
F_SKY1 otherwise makes the engine use ceiling light (255) for these sprites,
producing a fullbright appearance despite their normal actor states. The local
actor light override restores the original ground lighting and survives save/load;
other actors and maps keep their existing lighting.

87 additional ceiling-only SkyPickers select the plain cubemap: 68 in the
miniature sky room and 19 in the final arena. This prevents recursive background
views and a duplicate miniature beam behind the final arena's real beam.
`Sector.ClearPortal` is deliberately not used: it selects default portal 0,
which would restore the default SkyViewpoint rather than the plain sky.
`tools/patch_alternate_sky.py` adds these things idempotently; it preserves all
original map blocks and non-TEXTMAP lumps, including scripts and BSP data.

The shader uses the actual rendering viewpoint to choose the matching beam
anchor. Inside the miniature room the endpoint is (6464,704,2848), with a
4200-unit cloud plane. In the final arena, the tag-88 cylinder spans X=450..1474
and Y=13122..14018: its endpoint is (962,13570,-992), with an 8000-unit cloud
plane. Both use UV (0.5,0.425) for the compact opening. Its interior is empty;
nearby cloud detail drifts gently. No TNT04CN portal translation applies.

The UACVIEW RGB canvas supplies the main rendering camera separately for card
parallax inside the sky room, where uCameraPos contains the SkyViewpoint's
coordinates. Three 24-bit signed coordinates have sub-unit precision; the
fourth block marks valid data. Like the existing sky-data canvases, this is
updated in RenderOverlay and can trail the main view by one rendered frame.
The beam opening uses the current portal viewpoint directly and has no such
latency. Direct arena rendering uses uCameraPos for both clouds and cards.

Five world-space cards reuse the CN ray/plane intersection and premultiplied
blue-key bilinear sampling. Distances range from 36000 to 100000 world units;
elliptical periods are 220â€“280 seconds with opposing directions, small amplitudes
and less than a quarter degree of rocking. Nearer platforms show stronger parallax.
The material protects the opening from foreground cards. Rock and platform colors
retain 70% of their source chroma, with red CN rock rims shifted toward QLAVA amber
at preserved luminance. This retains charcoal, bronze and amber material detail
without the former grayscale conversion or a uniform gold/brown cast. The CPU
fallback compositor applies the same correction. Source PNGs remain
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

Height-fix validation covers all three original viewpoints, the 218 middle and
445 lower ceiling bindings, the single skybox-special sector, 19 plain arena ceilings,
all four horizontal/upward views, save/load and C -> CN -> C map isolation.
The structural check compares the prior map: original geometry/things and all
non-TEXTMAP lumps remain unchanged; only 87 ceiling pickers are appended.

Initial artwork validation: tools/validation/alternate-sky-2026-09-09.

Color/light fix validation (2026-09-10): 35 runtime assertions in Vulkan and
OpenGL cover all 47 floor-lit decorations, save/load, height bindings and map
isolation. Matching before/after views verify material color and ground lighting.
