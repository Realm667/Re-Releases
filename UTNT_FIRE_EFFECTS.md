# UTNT torch and burning-barrel effects

The approved pixel-fire design is implemented for all six map-facing torch
replacements, the six ZScript torch aliases and `UTNT_Barrel`. Each source has
one anchored client VisualThinker with separate animation timing. Tall torches,
short torches and barrels have distinct dimensions and attachment heights;
barrels have a broader flame base. Native decoration parents, body sprites,
collision properties and map/editor IDs are retained.

The flame uses alpha blending to retain dark red edges and open spaces between
the tongues. A material shader animates pixel-sized bends, moving breaks at the
tips and the orange/green/blue palettes. Blue flames are narrower and calmer.
Sparse rising embers and a faint orange-fire smoke wisp are optional detail.
Body-attached lights fluctuate within a small range; the previous large flare
is no longer spawned. Historical flare classes remain available with reduced
intensity for compatibility callers.

## Runtime and quality

- UZDoom 5.0.1, hardware renderer (OpenGL and Vulkan).
- Quality 0/distance culling removes the local flame; 1 retains the animated
  silhouette; 2 adds sparse embers; 3 adds faint smoke for orange fire.
  Reduced effects use the quality-1 detail profile. Existing environmental
  lights remain enabled as before when cosmetic emission is disabled.
- Extra particles share the existing ambient budget, separate from combat.
- Registration is spread over 16 tics; no client reference is stored on a
  gameplay actor. Save/load and quality/range changes rebuild visuals locally.
- Shader registration uses preloaded sprite names and `SPF_ALLOWSHADERS`.
  Software rendering and hardware shaders disabled are outside this art target;
  the PNG fallback is orange.

## Verification

`tools/test_fire.py` loads `tools/fire-tests` in isolated engine configs and
saves. It checks all default replacements, direct ZScript aliases, removal of
an owning source, quality 0/1/2/3, reduced effects, distance removal/recovery,
save/load, and a 54-source scene including repeated disable/re-enable. It also
checks actual screenshot pixels for all three flame colors and motion. The
test map is an add-on, not part of the distributed game package.

Validation results and exact tested-package hashes are recorded alongside this
report's delivery in `tools/validation/fire-2026-09-07/`. Individual CPU profiler
samples are not an FPS benchmark. Full campaign completion and new network
testing are not claimed by this focused visual change.

To reproduce with the configured local environment:

```bat
call tools\utnt-env.cmd
"%UTNT_PYTHON%" tools\test_fire.py --mod tutnt.pk3
```

## Art provenance

The source flame was generated with the built-in Imagegen tool for this task,
then given a PNG `grAb` sprite-origin chunk. RGBA image pixels were not resampled
or edited. `tutnt/sprites/sfx/utnt-fire/UFFRA0.png`, `UFFGA0.png`, and `UFFBA0.png`
contain the same base art with separate material bindings. All color conversion
and motion happen in `tutnt/shaders/fire.fp`. The generated art is 971 × 1619;
shader sampling uses a 48 × 80 grid to match the game's pixel density.

Final generation prompt (built-in tool, no API/CLI fallback):

> Asset: one isolated animated-game VFX base sprite texture, transparent PNG, no scene, no text, no props. Authentic Doom-style LOW RESOLUTION PIXEL ART flame for a gothic torch.
> A single upright orange fire silhouette, 2 to 3 asymmetric curling tapered flame tongues separated by deep transparent gaps in the upper half. Main tongue leans gently right, a shorter tongue left. All tongues connect into one compact broad hot flame base. Orange and gold inner strands, dark red angular outside clusters, small pale yellow hot core in bottom quarter with just a FEW cream pixels, no large white areas. Sharp jagged chunky pixels, artwork looks drawn on a 48 by 80 pixel grid then enlarged with nearest neighbor. Use discrete coherent pixel clusters with limited palette rather than tiny stippled pixels. No black outlines.
> Centered on a transparent portrait canvas with generous transparent padding on all sides (about 15 percent on left/right and 10 percent top/bottom). The flame is roughly twice as high as wide. Flat base softly scalloped; tongues organically curled like a classic Doom fire sprite, not a symmetric flame icon or wavy ribbons. Visible hollows and separation, nuanced red-orange outer lobes. Transparent background must be real alpha, absolutely no checkerboard, black rectangle, floor, brazier, stick, barrel, smoke, glow halo, detached sparks, letters, borders or shadows. Only the connected flame itself. Colors remain saturated with cream confined to about 3 percent of flame area. This texture will be used as an actual in-game sprite with separately animated distortion, embers and light.

Implementation references: the project's checked-out UZDoom
`wadsrc/static/zscript/visualthinker.zs`, `src/rendering/hwrenderer/scene/hw_sprites.cpp`
and `src/r_data/gldefs.cpp`, plus the official
[GLDEFS shader documentation](https://zdoom.org/w/index.php?title=GLDEFS).

## Final delivery � 2026-09-07

The full built package passed 39 lifecycle assertions per renderer (78 total), plus actual rendered-color and motion checks in both OpenGL and Vulkan. All 14 ACS modules compiled byte-identically without changes. The isolated fire package also passed the same checks before the concurrently edited weather source became buildable.

Tested package: 8834 entries, 85564732 bytes, SHA-256 `ddd2e7831f4bd2018974dc72a3a3211dd1b0d9b9f96f7c336914501afbe2365b`. The exact fire production sources and the SFX fire block were compared byte-for-byte against this tested package.

Existing running UZDoom processes were left in place. Restart with the rebuilt `tutnt.pk3` to load the new resources. Save/load was checked with saves made from this version.
