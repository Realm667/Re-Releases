# Environmental presentation

The environmental extension adds five independently switchable options under
UTNT options > Environment details. English, German, Spanish and French labels
are provided. The local heat experiment is an isolated test addon.

## Implemented behavior

- **Rain-wet surfaces:** TNT02 binds ordinary floors and wall faces near the
  existing rain regions to material aliases. A bounded queue traces incoming rain
  against the live geometry, including roofs and solid 3D floors. Nearby surfaces
  receive extra checks. Wetness builds over seconds and dries gradually after
  shelter or rain cessation. Stone darkens more than metal; specular response is
  restrained. Liquid, sky, portal, switch and emissive materials are excluded.
  The original texture scale and area-alignment definitions are retained.
- **Underwater atmosphere:** automatically enabled at water level 3, with a mild
  depth-dependent tint. Water, slime and blood use different colors; the existing
  underwater distortion remains separately adjustable. Lit shallow water regions
  receive material caustics on their bed and walls, not on the HUD or the whole
  image. Reduced effects disables the additional underwater presentation.
- **Footprints:** distance-based alternating sole marks on snow; wet soles leave
  fading dark marks after water or rain. Traces verify floor support at the center
  and corners. Marks follow moving floors and 3D-floor tops. Teleports, death and
  player replacement reset the walking accumulator. Budgets are 32/80/160 marks
  for low/medium/high quality; wet marks last up to seven seconds, snow marks up
  to thirty seconds and disappear faster during heavy snowfall.
- **Mechanism reactions:** build-time discovery covers standard door, floor,
  ceiling, stair, pillar and platform actions plus literal sector tags in ACS
  movement calls. Runtime watchers react to actual movement and a completed stop
  after meaningful travel. Dust originates near the closest boundary, groups
  share a cooldown, and distance/quality/reduced-effects checks limit emission.
  Existing movement, collisions, timing and gameplay RNG are not changed.
- **Scenic lighting:** a small authored selection in TNT02, TNT03A1, TNT03A2,
  TNT03B and TNTLE. Existing ceiling lights receive restrained warm or cool
  accents and soft shafts; lava-edge accents vary slowly by four percent.
  Shafts use depth-tested sprites and disappear at low quality or reduced
  effects. The original sector lighting is retained.

No production map geometry is rewritten. Surface aliases explicitly retain
the original floor terrain, including footsteps and terrain behavior. Map
scripts that replace a bound texture take precedence; those surfaces detach.

## Technical limits

Exposure is sampled per surface grid, usually around 64 map units, with a cap
on cells per face. Shelter transitions therefore have that spatial resolution;
this is not per-pixel ray tracing. Large or newly visited surfaces may take time
to settle. The default maximum is 40 surface visits per tic, including nearby
priority visits; adjacent equal canvas values are batched.

Caustic region discovery uses authored water-control heights and excludes dark
or deep beds. Moving water-control heights and complex stacked water volumes
are not dynamically re-meshed. Footprints simulate a depression visually;
snow geometry is not displaced. Highly sloped/unsupported footprint positions
are rejected. Mechanisms driven through computed ACS tags or polyobjects are
not guaranteed discovery. The light shafts approximate illuminated dust;
they are not volumetric shadow maps.

## Lava heat prototype

Run:

```
python tools/test_environment_fx.py --case prototype --renderer 1
python tools/test_environment_fx.py --case prototype --renderer 0
```

The fixture contains lava, nearby walls, an overhang, floor and wall heat-source
positions, and an occluded source. The test addon alone defines
UTNT_localheatprototype. A projected region genuinely refracts the scene before
the HUD; center visibility can suppress an entirely hidden source.

The prototype does **not** establish production-quality localized refraction:
a partially visible source can still distort foreground pixels because the
postprocessing shader has no per-pixel scene-depth mask. Its projection also
assumes the fixture's fixed field of view/aspect. It is deliberately absent from
the normal gameplay package and menu. Further production work needs an engine
depth/mask integration or a depth-tested refractive rendering path.

## Generation and checks

```
python tools/build_environment_fx.py
python tools/build_environment_fx.py --check
python tools/test_environment_fx.py --case compile
python tools/test_environment_fx.py --renderer 0
python tools/test_environment_fx.py --renderer 1
```

The generator reads the map WADs without modifying them and writes the bindings,
metadata textures, combined material shaders and manifest. The normal package
build rejects stale geometry, rain-marker or movement-tag fingerprints. Regenerate after map or material-authoring changes.

Automated runtime checks cover rain exposure, roofs, solid 3D floors, terrain
preservation, real camera submersion, footprint emission/budget, moving-platform
reaction and save/load restoration. OpenGL and Vulkan fixtures pass. Targeted
campaign checks cover the five maps with lighting; these are not a campaign
playthrough or a network synchronization/performance certification.

Local screenshots and runtime logs are in
`tutnt/.codex/validation/environment-fx/`; test packages are in
`tutnt/.codex/builds/`. Temporary authoring work is in
`tutnt/.codex/work/environment-fx/`.
