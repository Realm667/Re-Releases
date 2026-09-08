# Weather on the player view and skybox continuity

Rain refracts the rendered scene through individually moving water drops, with a curved-edge graphic contribution capped at 20% per pass. Drops land, pause, slide, leave narrow refractive tracks, merge when close, and expire. Frost uses a unique full-frame crystal image, with an uneven edge, refractive detail and local scattering. The texture is sampled once across the viewport, never tiled. Its center is clear. The Scene postprocess leaves HUD text sharp.

## Exposure and transitions

The map-local weather handler saves a separate deterministic visor state for every player. It samples the authored precipitation region at the first-person eye and traces back towards incoming precipitation. Solid roofs, walls, 3D floors and submerged positions block new deposits. Adjacent open air alone cannot wet a sheltered eye. Up to three rays every four tics provide a partial doorway response. Private random state does not consume gameplay RNG.

Intensity follows the existing five-minute weather cycle. At peak exposure, water reaches full strength in approximately one second and ice grows over approximately twelve seconds. In shelter, water drains in at most 3.6 seconds and frost thaws in approximately 5.6 seconds. Death, camera replacement, submersion and teleports clear stale accumulation; ordinary movement into cover preserves fading residuals. Freeze and save/load preserve accumulated state. Third-person view and full-screen automap disable drawing.

Local settings: `UTNT_visoreffects` (default true), `UTNT_visorstrength` (default 1, clamped 0–1). Reduced effects and quality 0 suppress the visor. Rain uses at most 28 simulated drops, drawn as 28/20/10 at high/medium/low quality. Two compact passes carry up to 14 drops each; the second pass is disabled when unnecessary, including snowfall. Coordinates and shape are packed into exact 24-bit float payloads, keeping each custom uniform block at 128 bytes. Position quantization is below half a pixel at 1440×810. Frost has no full-screen blur: additional samples are confined to covered edge pixels.

## Snowstorm veils

Peak snow allows three emission attempts per tic instead of one, with limits of 160/56 veils at high/medium quality. Air and ground veils have longer lives, broader shapes and a seven-tap anisotropic texture filter. A broad smooth envelope and elliptical fade remove rectangular sprite boundaries. Snow veils no longer expand beyond their initial wall-clearance width. These are soft directional approximations to motion blur, not a fluid simulation.

## Skyboxes

All authored `SkyViewpoint` actors are collected, including TID-selected skyboxes. A separate clipped 3D precipitation field is emitted inside each skybox at 1:8 world size and velocity. Geometry traces adapt the sample volume to each viewpoint's visible free space. The field has its own short-distance fade and receives emission priority before the main world exhausts its budget. Initial distribution is warmed across the volume. Density and shape follow the same intensity cycle; the original sky openings and skybox terrain provide occlusion. No map geometry or player starts are modified by this change.

## Reproduction and validation

Set `UTNT_ENGINE` and `UTNT_IWAD`, then run:

```
python tools/test_weather_visor.py --kind rain --renderer 1
python tools/test_weather_visor.py --kind snow --renderer 0
```

Use `--root` for isolated outputs and `--mod` for a candidate package. The fixture checks exposure, actual residual decay on entering cover, drop movement, scaled sky particles, freeze, save/load and eventual clearing. Existing weather geometry and multiplayer fixtures cover particle accounting and shared simulation. Evidence is in `tools/validation/weather-visor-2026-09-08`. Tests run on UZDoom 5.0.1 with OpenGL and Vulkan; software rendering is not a shader target.

The generated frost asset's exact prompt, tool and hash are recorded in `tools/artwork/weather-visor/provenance.json`. No stock reference image is shipped. Postprocess integration follows the engine's [GLDEFS API](https://zdoom.org/wiki/GLDEFS#Post-processing_shaders).
