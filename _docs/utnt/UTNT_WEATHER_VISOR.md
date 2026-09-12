# Weather on the player view and skybox continuity

Rain refracts the rendered scene through individually moving water drops, with a curved-edge graphic contribution capped at 20% per pass. Drops land, pause, slide, elongate with their speed and travelled distance, leave tapered refractive tracks, merge when close, and expire. Sliding bodies stretch up to 2.8 times their radius and tracks can reach 28% of screen height. Shape and track length interpolate between simulation tics; graphic contributions remain capped at 20%. Frost uses a unique full-frame crystal image, with an uneven edge, refractive detail and local scattering. The texture spans the viewport once, never tiled. The visible frost mask uses the original sharp crystals at half the previous tint opacity (maximum 0.43). A separate 5x5 filtered normal field retains strong refraction without blurring the artwork; local scene scattering is reduced to 0.0018. Rain uses a broader soft silhouette and highlight, approximately doubled body/track refraction, and local five-tap scattering at medium/high quality. Rain defocus remains local to water-covered pixels. Its center is clear. Light accumulation is applied once to opacity instead of being repeatedly multiplied away. Sampling stays inside the image to prevent stretched border texels at low intensity. The Scene postprocess leaves HUD text sharp.

## Exposure and transitions

The map-local weather handler saves a separate deterministic visor state for every player. It samples the authored precipitation region at the first-person eye. Rain traces back towards incoming precipitation, with up to three rays every four tics for a partial doorway response. Snow uses one vertical sky trace: neighboring walls, gust direction, movement and view direction cannot stop frost accumulation while the eye is under open sky in a snow region. Solid roofs, 3D floors and submerged positions block accumulation. Adjacent open air alone cannot expose a sheltered eye. Private random state does not consume gameplay RNG.

Intensity follows the existing five-minute weather cycle. At peak exposure, water reaches full strength in approximately one second and light-snow frost reaches a subtle 25% accumulation in approximately 2.5 seconds; stronger snow smoothly increases accumulation up to full frost (approximately 7 seconds from dry). In shelter, water drains in at most 3.6 seconds and frost thaws in approximately 5.6 seconds. Death, camera replacement and submersion clear stale accumulation. A large position change rechecks exposure immediately and preserves frost; rain droplets retain their teleport reset. Frost persists at outdoor snow destinations and thaws smoothly after entering shelter or leaving the snow region. Freeze and save/load preserve accumulated state. Third-person view and full-screen automap disable drawing.

Local settings: `UTNT_visoreffects` (default true), `UTNT_visorstrength` (default 1, clamped 0–1). Reduced effects and quality 0 suppress the visor. Rain uses at most 28 simulated drops, drawn as 28/20/10 at high/medium/low quality. Two compact passes carry up to 14 drops each; the second pass is disabled when unnecessary, including snowfall. Coordinates and shape are packed into exact 24-bit float payloads, keeping each custom uniform block at 128 bytes. Position quantization is below half a pixel at 1440×810. Additional frost samples are confined to the border region; rain scattering samples are confined to wet pixels. Uncovered scene pixels pass through unchanged.

## Snowstorm veils

Peak snow allows three emission attempts per tic instead of one, with limits of 160/56 veils at high/medium quality. Air and ground veils have longer lives, broader shapes and a seven-tap anisotropic texture filter. A broad smooth envelope and elliptical fade remove rectangular sprite boundaries. Snow veils no longer expand beyond their initial wall-clearance width. These are soft directional approximations to motion blur, not a fluid simulation.

## Skyboxes

All authored `SkyViewpoint` actors are collected, including TID-selected skyboxes. A separate clipped 3D precipitation field is emitted inside each skybox at 1:8 world size and velocity. Geometry traces adapt the sample volume to each viewpoint's visible free space. The field has its own short-distance fade and receives emission priority before the main world exhausts its budget. Initial distribution is warmed across the volume. Each viewpoint has an independent population target derived from the nearest weather cell and a one-time 32-ray estimate of its free volume. Round-robin replenishment prevents one skybox from starving the others; fast-falling rain is refilled more frequently. The total sky reserve is capped at 40% of the existing particle budget and excess particles fade during calming. Density and shape follow the same intensity cycle; the original sky openings and skybox terrain provide occlusion. No map geometry or player starts are modified by this change.

## Reproduction and validation

Set `UTNT_ENGINE` and `UTNT_IWAD`, then run:

```
python tools/test_weather_visor.py --kind rain --renderer 1
python tools/test_weather_visor.py --kind snow --renderer 0
python tools/test_weather_response.py --kind rain --renderer 1
python tools/test_weather_response.py --kind snow --renderer 0
python tools/test_frost_persistence.py --kind snow --renderer 1
```

Use `--root` for isolated outputs and `--mod` for a candidate package. The frost persistence fixture surveys open-sky positions against the previous directional query, then checks continuous accumulation while walking, turning and making large outdoor position changes. The response fixture additionally checks light-snow frost, per-sky density/accounting and elongating rain tracks. The fixture checks exposure, actual residual decay on entering cover, drop movement, scaled sky particles, freeze, save/load and eventual clearing. Existing weather geometry and multiplayer fixtures cover particle accounting and shared simulation. Evidence is in `tools/validation/weather-visor-2026-09-08`, `tools/validation/weather-response-2026-09-09`, `tools/validation/weather-softness-2026-09-09`, `tools/validation/frost-refinement-2026-09-09` and `tools/validation/frost-persistence-2026-09-09`. Tests run on UZDoom 5.0.1 with OpenGL and Vulkan; software rendering is not a shader target.

The generated frost asset's exact prompt, tool and hash are recorded in `tools/artwork/weather-visor/provenance.json`. No stock reference image is shipped. Postprocess integration follows the engine's [GLDEFS API](https://zdoom.org/wiki/GLDEFS#Post-processing_shaders).
