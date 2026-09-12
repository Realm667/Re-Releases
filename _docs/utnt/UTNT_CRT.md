# CRT monitor materials

48 existing monitor resources use a shared CRT material shader. CAM_T1–CAM_T4,
their live feeds, and their frame/overlay resources are excluded. Original pixel
art, map texture assignments, animation sequences and palette data are unchanged.

The shader applies independently authored glass rectangles to the Q2COMP/Q2CMP
families (including their colored/rotated variants), OCOMP, QTWALL04/05,
QPLANET1–4 and EE_ENJ/EE_GZ/EE_TDA. The authoritative list and masks are in
[tools/crt-materials.json](../../tools/crt-materials.json). Electronics, switches,
frames and vents outside those rectangles retain their original material.

## Appearance

Each display gets an outward-convex glass faceplate, rounded glass corners, fine
scanlines, a quiet edge vignette and color-preserving phosphor emission. Dark
content gains readability without replacing the original graphics. OCOMP and
the blank Q2COMP14/Q2CMP091 displays retain their powered-off appearance.
The rotated Q2FCMP08/18 resources use the corresponding rotated scanline axis.

The shader ray-traces a convex height field within each glass rectangle:
`height = depth * (1 - x²) * (1 - y²)`, with normalized face coordinates and
zero height at the seated rim. The center rises by 5.5% of the shorter display
side. World-space UV derivatives account for texture scale, mirroring and floor
orientation. A bounded search finds the first view-ray intersection; its analytic
surface gradient drives both material normals and the live reflection direction.
This produces actual view-dependent relief/parallax within the shader, including
in the original display artwork, rather than only fixed barrel-distorted UVs.

The faceplate is virtual shader geometry: it does not subdivide map walls, alter
collision, write scene depth or extend the outer wall silhouette. The original
bezel clips the effect. Relief fades with distance and at extreme grazing angles
to keep the aperture stable. `CRT_BULGE` is generated from the optional per-screen
`bulge` value in the material manifest.

Scanlines fade before their frequency becomes undersampled, including at oblique
angles, and the effect softens with distance. Optional motion is a slow,
low-contrast scanline phase drift; it does not introduce flashing, tracking
breaks or alter existing texture animation timing. This does not add temporal
phosphor history buffers.

## Actual room reflections

The reflections use live 128 × 128 camera views of the map, including visible
actors, rather than an invented reflection image. Invisible non-interacting
probe actors are initialized deterministically from the selected wall/floor/
ceiling surfaces, independent of each player's effect settings. Nearby probes
are merged only within the same sector and plane. No gameplay RNG, lighting,
collision, action or map-texture writes are used.

Client-local presentation chooses at most two nearby visible probes (one at
medium quality). Each points out from its surface into the room with a 120°
field of view. The shader projects the reflected view direction into that
capture, bends it slightly with the glass normal, and explicitly filters it
even when the original pixel art uses nearest filtering. Reflection strength
increases at oblique angles and diminishes over bright display content.
Out-of-capture directions and unmatched/distant planes fade out.

This is a local environment-probe approximation, **not a geometrically exact
planar mirror**: nearby objects do not have correct reflection parallax, the
capture has a finite field of view, and the two-view budget can leave additional
monitors with only the CRT treatment. Concave sector surfaces without a valid
interior probe point also retain the CRT treatment without reflection. Probe
origins are fixed after initialization; this is intended for the existing static
monitor installations, not arbitrary moving monitor geometry.

UCRTSTAT and UCRTP0/1 are private resources, unrelated to CAM_T*. The private
metadata canvas issues tiny capture-texture draws to request fresh camera
renders: UZDoom does not request updates merely because a camera is bound as
an auxiliary material sampler. Those draws never appear in the HUD. Reflections
are suppressed inside the probe views themselves to avoid recursive feedback.

## Controls

In **Remaster → Surfaces and water**:

| CVAR | Default | Purpose |
|---|---|---|
| UTNT_crt | true | CRT material treatment |
| UTNT_crtreflections | true | Live room reflections |
| UTNT_crtmotion | true | Subtle scanline drift |

All labels are available in English, German, Spanish and French. Quality 0
disables the treatment; quality 1 retains static CRT treatment without captures;
quality 2 permits one capture and quality 3 permits two. Reduced effects suppress
reflection captures and motion while retaining the static CRT material.
Individual toggles remain available. Disabled reflections stop requesting
further capture renders.

## Build and validation

The regular package builder invokes `tools/build_crt_materials.py`; its
`--check` mode verifies the generated GLDEFS bindings and runtime selection list.
The original diffuse images are never generated or overwritten.

`tools/test_crt_materials.py` builds a separate gallery of all 48 materials.
Use `--mod tutnt.pk3 --packaged` to test the built package without source
overrides. Batches select six materials at a time; batch 0 also checks settings and
save/load. Pixel comparisons verify a changed glass image, unchanged housing,
and a reflected response when only the room wall behind the viewer changes.
The `--map TNT02` / `--map TNT03A2` paths capture original map placements.

Local captures and results: `tutnt/.codex/logs/crt-*` and
`tutnt/.codex/validation/crt/`. They are not packaged or committed.

Validated on 12 September 2026 with UZDoom 5.0.1:

- All 48 generated bindings and four definition tables passed consistency checks.
- Vulkan and OpenGL gallery batches 0–1 covered twelve representative resources,
  a rotated source, a horizontal console and repeated UVs with negative offsets.
- Batch 0 passed initialization/CAM exclusion assertions before and after save/load.
  The final Vulkan run used the shared package without source overrides: glass
  changed with CRT enabled and with the reflected room changed; housing difference
  was exactly zero in the comparison region.
- Original placements in TNT02 (Vulkan) and TNT03A2 (OpenGL) loaded and rendered.
- The convex/flat faceplate comparison changed the angled glass region while
  leaving the sampled housing exactly unchanged. Rotated and horizontal displays
  also passed the OpenGL gallery with the convex faceplate enabled.
- Catalog/font validation and 14 localization unit tests passed. Actual runtime
  lookup, glyph and layout checks passed in English, German, Spanish and French
  (2,520 assertions per locale); the new settings were captured in all four menus.

The gallery covers all resources, but the captured runtime batches do not claim
individual visual review of every placement in every map. Performance was bounded
by capture count and distance; no cross-hardware frame-time benchmark was performed.
