# TNT04CN: dark cloud ceiling and Source rift

The approved second mockup replaces the saturated nebula with dark charcoal and earth-brown cloud masses, restrained red reflections, and one pale-orange fiery opening overhead. The surrounding sky fades downward into black. Floating basalt and the shared TNT04A/B comets remain, including size variation and rare dispersing groups.

## Beam and portal alignment

The beam is entirely existing **level geometry** (T4_BM2/T4_BM2B); neither production image contains a beam. No map, ACS, sector lighting, Source actor or beam material is edited by this revision.

The lower cylinder ends at 8392, but the visible upper section continues through the original stacked-sector portal into sectors 1195/1245, with ceiling 20000 and center (10624,-192). Portal lines 8554–8557 translate by (10496,128,0). Its endpoint in the lower room's coordinates is therefore **(128,-320,20000)**.

The hardware sky material intersects each viewing ray with that virtual cloud plane. It normalizes the translated render camera in the upper room (X > 6000), so both portal passes use the same ceiling and the opening stays over the actual endpoint as the player moves. The cloud image's empty center is at UV (0.5,0.425); its 30000-unit span matches the approved large opening. This is a sky projection only, without adding geometry or drawing another beam.

The existing TNT04CN-only handler selects URFSKY and removes the obsolete decorative star camera through normal engine portal cleanup. The secondary viewpoint remains. Save/load reapplies the selection; TNT04A/B/C retain their own skies.

## Layers and fallback

- `graphics/rift/zenith.png`: cloud ceiling and orange-rimmed opening only.
- `graphics/rift/dark-clouds.png`: dark cloud panorama fading to black; no opening or beam.
- `graphics/rift/rocks-key.png`: retained independent rock silhouettes, with subdued grey-brown shading.
- `tools/war-comets.glsl`: unchanged shared comet implementation, composited behind rocks.

The hole stays fixed while the surrounding clouds and floating rock fields drift slowly. All six materials reconstruct a continuous world ray and share the same projection. Six 1024-square static fallback faces use a representative camera directly below the opening; static rendering cannot reproduce camera-dependent parallax. Hardware OpenGL/Vulkan materials provide the aligned view.

## Moving mountains and debris

`tools/rift_rocks.py` defines seven independent fields: the original debris, three additional mountain masses, and three smaller rock clusters. Intact UV regions of the existing `rocks-key.png` are reused without modifying its artwork. The shared layout generates the GPU material calls and the static fallback at time zero.

Groups are distributed around world yaw 20, 80, 120, 175, 215, 265 and 315 degrees, with varied elevation, scale and occasional mirroring. Each follows a small closed ellipse around its fixed world-space rest position, using a single phase in quadrature. Different signed periods of 130-240 seconds give varied speeds and opposite directions. Gentle rocking remains below one degree.

Rock cards have fixed plane orientations and physical spans scaled from their reference distance. The shader intersects the viewing ray with these planes using the portal-normalized camera position. Near debris is 18000-32000 units away, the original field 55000, and distant mountains 90000-140000. Thus nearby groups show stronger lateral and vertical parallax while the distant mountains stay comparatively stable. All fields use the same reference eye (128,-320,3241) and render far to near. Rotating the view alone does not move their world positions.

A soft exclusion around the opening's center leaves the geometric beam endpoint readable. Rocks remain in front of the comets; the approved clouds, opening, map geometry and shared comet source are unchanged. Both stacked-room render passes use the same normalized camera for clouds and rocks.

Motion and parallax require hardware materials. Static fallback faces use the same layout at time zero and the representative reference eye. Evidence for elliptical motion and parallax is under `tools/validation/rift-parallax-2026-09-09/`; earlier gentle-drift evidence remains under `rift-floating-2026-09-09/`.

## Rebuild and validation

Run `python tools/build_rift_sky.py` (NumPy/Pillow). `build_war_sky.py` also regenerates this sky. Approved art and complete generation prompts are in `tools/artwork/rift/v2/`; original generated inputs remain unmodified.

`tools/test_rift_structure.py` checks 12 cube edges, registrations and identical comet code across all 18 TNT04A/B/CN faces. `tools/test_rift_zenith.py` derives the upper beam endpoint and portal translation from the actual map and verifies the black nadir. `tools/test_rift_sky.py` captures twelve directions/positions, including both stacked rooms, and checks save/load, the secondary camera, Source actor, sector count and map transitions in OpenGL/Vulkan.

Evidence for this revision is in `tools/validation/rift-zenith-2026-09-09/`. Earlier v1 evidence and artwork remain archived. The final package is rebuilt with all 14 ACS modules and checked against the current source assets.

`tools/test_rift_orbits.py` checks closed paths and world-space centre projection at 17 orbital positions and two camera offsets for each field. `tools/test_rift_parallax.py` freezes shader time in an isolated alpha diagnostic, translates the camera sideways by 512 units, measures near/far displacement and compares equivalent views on both sides of the original portal. It accepts the same engine/IWAD arguments as the other runtime checks, plus `--work` and `--renderer`.
