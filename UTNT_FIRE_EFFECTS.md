# Organic torch and burning-barrel fire

The approved September 2026 redesign replaces the single pixel-grid flame with
many short-lived, independently moving flame sheets. A non-rendering local
emitter maintains a compact fuel bed, rising tongues, departing wisps, visible
gold embers and larger warm-gray smoke. The orange, green and blue tall/short
map replacements, all six explicit ZScript aliases, and burning barrels use
the same system. Existing decoration bodies, native parents, gameplay and
map-facing identities are preserved.

## Appearance and motion

Four distinct texture fragments form the fire. Base fragments live 10 tics;
other sheets live 18–26 tics, rise, accelerate slightly, stretch, narrow and
fade independently. A shared changing drift is varied per sheet, so the
outline is continually rebuilt. The shader supplies small internal flow and
color; it no longer imposes an artificial coarse pixel grid or animates one
complete flame. Soft birth edges connect the fire to the fuel bed.

Barrels emit across a disk over their opening and use a broader base. Blue
flames are narrower with slower internal shader motion and no smoke. Green
flames wind more strongly and emit occasional faint smoke. Orange smoke
starts at 20 world units wide on tall torches and 27 on barrels, expands to
2.25 times that width, and fades over 48–65 tics. Ember images are 2.8–4.5
world units wide, with varying elongation, drift and 28–46-tic lifetimes.
Short torches scale these elements down together.

## Runtime and quality

- UZDoom 5.0.1 hardware rendering, OpenGL and Vulkan, with material shaders.
- Quality 0 and the existing distance limit remove all local fire visuals.
  Quality 1/reduced effects retain multiple flame fragments and a renewed
  base. Quality 2 adds embers and smoke; quality 3 increases the density.
  Beyond 640 world units the emitter uses the low-detail profile.
- Every birth shares the existing ambient emission budget; combat has its
  separate pool. Low quality reduces barrel births and jitters emission
  intervals. Denied births retry, avoiding permanently synchronized gaps.
- Emitters and particles are client-side thinkers and use `utntcosmetic`
  randomness. No gameplay projectile or saved gameplay pointer is introduced.
  Owner removal, distance/quality changes and save/load rebuild or retire the
  visuals locally. Frozen owners suspend the effect. Body lights retain the
  existing modest fluctuations.

## Art provenance

`tutnt/graphics/utnt-fire/fragment-atlas.png` is a 1254 × 1254 RGB atlas created
with the built-in Imagegen tool using the approved mockup as a style reference.
The generated pixels are copied unchanged. `TEXTURES.fire` defines the four
native sprite crops and their origins; the material converts the black
background into translucent edges and supplies the three colors. The old
`UFFRA0`, `UFFGA0` and `UFFBA0` whole-flame images are removed.

Smoke reuses the project's `X037A0` alpha texture and embers reuse `EMBRA0`,
with separate material bindings so their original users are unaffected.

Final atlas generation prompt:

> Generate actual game VFX fire-fragment texture atlas, four pieces in a STRICT equal 2x2 grid on a PURE BLACK square background. Reproduce the luminous smooth golden-yellow, amber and orange flame material in the reference. Four small individual torn FLAME SHEETS to be layered as moving particles. Do NOT draw complete flames or physical objects. Each tile contains one short ragged luminous sheet of fluid hot gas with gold-yellow inner body, creamy inner fold, translucent amber edges that fade into black. Photographic fire texture with soft low-frequency fluid swirls and broad smooth inner gradients. Absolutely NO lattice, cracks, veins, wire mesh, lava, pixel grid, granular dots or fine lace patterns. Top left: small squat rounded flame sheet with ragged upward tips; top right: short upright curved flame tongue wider at bottom; bottom left: irregular oblique wisp; bottom right: thin short forked tip. Fragments must have different profiles, but none taller than 1.7 times its width. Fine frayed borders, dense smooth interior. All tiles have at least 15 percent pure black margin. All tile bottom extents aligned to 85 percent tile height, centered horizontally. Background completely RGB 0,0,0 for a game shader to extract transparency. No labels, no smoke, no sparks, no props, no scenery, no glow halo on background.

## Verification and delivery

`tools/test_fire.py` loads the dedicated add-on map and checks all torch
replacements and aliases, barrels, finite owned particle populations, at
least three independent fragments per active source, removal/recovery,
quality levels and reduced effects, range culling, save/load and 54-source
stress. Screenshots check actual colors and changing fire pixels. Camera
positions are asserted before color captures; isolated input settings keep
desktop interaction from moving the test camera. Eight successive engine
frames provide a visual record of the moving sheets.

Both the full local package and an isolated master-based package containing
only this fire change passed the renderer/lifecycle checks. The final isolated
suite passed 46 assertions per renderer plus rendered-color/motion checks.
An additional 54-source high/medium/low-quality run passed nine assertions per
renderer. All 14 ACS modules compiled with unchanged bytecode.

Exact source and package hashes, build results, engine logs and unedited
screenshots are in `tools/validation/organic-fire-2026-09-07/manifest.json` and
the adjacent files. Profiler samples measure client thinker CPU time, not
whole-frame GPU performance. Full campaign completion and new multiplayer
testing are not claimed by this focused cosmetic change. The earlier
`tools/validation/fire-2026-09-07/` directory records the superseded design.

Reproduce with the configured `UTNT_ENGINE` and `UTNT_IWAD`:

```bat
python tools/test_fire.py --mod tutnt.pk3 --renderer both
```

Restart the game with the rebuilt `tutnt.pk3` to load the replacement art and
classes. Existing running user sessions were not stopped.
