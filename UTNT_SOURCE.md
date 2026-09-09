# TNT04CN â€” The Source

The final boss now uses the approved three-state presentation: an intact runic
shield, six separated rune arcs around the exposed heart, and a damaged seal
with staged comet charging. The original horned demon sigil stays at the centre.

The rune alphabet now comes from QRUNT63, the same four glyphs used by the
campaign's teleporters and portals. The material samples their native red ink
at texel centres and explicitly interpolates it. It no longer selects the
incorrect RUNE1/3/5/7/9 switch sequence, which included unlit stone switches.
SOURA0 and the original rune assets are unchanged by this correction. No new
raster artwork is required. Approved AI paintovers are retained under
`tools/artwork/source/`; they are design targets, not runtime screenshots.
The first implementation's functional checks did not establish a visual match.

## Battle feedback

- The narrow central beam and continuous world-space spiral use the existing
  wall geometry as carriers. Ray/cylinder intersections draw the helix and shield
  on round surfaces inside those carriers. Both stacked-room centres are taken
  from the actual map geometry. The map topology and collision are intact.
- The shield uses an emissive SetupMaterial pass, so dark sector lighting no
  longer hides the membrane and glyphs. The beam has a local soft halo; the seal
  retains finer lines and its light reaches the surrounding arena.
- Actual line 99 collision determines the shield state. The shield middle
  material is removed while open, even while the original ACS fade changes alpha.
  The seal opens in six arcs; its compact heart pulses and the beam becomes
  transparent around the target. The arcs draw together before closure.
- Shield impacts produce a short ripple. For player-activated hits its position
  is estimated from the firing ray against the shield cylinder; non-player
  activators use a fixed shield-front fallback. It is cosmetic, not a hit test.
- Guardian activation/death sends a brief energy connection and travelling
  ripple towards the seal. The original death special opens the shield.
- The three existing attack scripts notify the presentation at their original
  start: rising rock signs, three sequentially charging comet nodes, and a
  contracting fiery heart. Below half health, the seal cracks and some runes dim.
- Death breaks the seal through a saved seven-second lightning sequence and
  two seconds of stillness before the original destination transition. Living
  health, collision, random calls, spawn sites and attack delays remain.

ACS adds three attack notifications, the TNT04CN-specific finale ending in
`source/tutnt.acs`, and a shield-impact notification in TNT04CN script 120. The map's TEXTMAP and
nodes are byte-identical. TNT04C retains its original visuals and map bytes.

## Implementation and limits

`UTNT_Source.zc` adds presentation bases to the existing Source and Guardian
classes. Saved boss fields describe attack, shield and defeat state. Forty-four
bounded VisualThinkers, eight stone actors and nine light anchors live locally and rebuild
after loading. Essential target/shield/attack indications remain with FX quality
zero. Reduced effects disable ornamental roll and pulse motion where specified;
dynamic lighting follows local effect quality. No gameplay random stream is used.

The materials target UZDoom 5.0.1 OpenGL/Vulkan. A software renderer cannot show
the procedural ring masks, glyph isolation or state materials. The round surfaces are visual projections inside the original polygonal carriers;
the shield's blocking lines and the original boss position/hitbox are unchanged.
The appearance approaches the paintover, but a pixel-identical reproduction of
AI artwork is not claimed. Camera pitch, exposure, bloom and viewport affect the
comparison. Old-save compatibility and WAN multiplayer are not
claimed by the local tests.

## Reproduce

1. Run `python tools/build_source_materials.py` after editing the four
   `tools/source-*.glsl` sources. Commit their generated material files too.
2. Build through `tools/build_utnt.py` with the configured ACC and engine.
3. Run `tools/test_source_structure.py --baseline-ref 5c8091aff` to compare the
   combat contracts and original assets against the pre-Source implementation.
4. Run `tools/test_source.py --work <output> --renderer 0` and `--renderer 1`,
   providing `--engine`, `--iwad` and optionally `--mod <pk3>`.
5. Run `tools/test_source_coop.py --work <output>` with the same engine/IWAD/mod
   arguments for two local peers with opposing effect settings.

The test fixture is separate from the game package. Validation records are under
`tools/validation/source-2026-09-09/`; runtime images in that directory are actual
engine captures. The checks cover guardian-driven opening, real ACS attacks,
save/load during the open window, three viewpoints, reduced/zero FX, collapse,
and map isolation. They do not constitute a complete manual campaign playthrough.

## Visual correction — 2026-09-09

The user correctly identified the difference between the approved paintover and
the first runtime result. Corrected the native rune selection, rounded the helix
and shield, enabled shield emission, and adjusted beam halo and sigil lighting.
Procedural sprite/shield carriers are opaque independently of SOURA0's artwork.
The functional contract remains unchanged. Evidence for this correction is in
`tools/validation/source-visual-correction-2026-09-09/`. Those PNGs are direct
engine captures, without image generation or retouching. The reference view uses
the same arena position with a higher camera pitch to include the full seal;
the original front/side/wide views remain in the test sequence.

The legacy shield pulse (map script 701) and impact fade (121) wrote line alpha
after the Source actor's Tick, intermittently hiding the new membrane. They are
now stopped by the presentation controller, which explicitly selects additive
blending. The open-window script 122 remains untouched. RenderOverlay logging in
the test fixture verifies the final drawn alpha, not only pre-ACS actor state.

## Seal focus and central glow — 2026-09-09

The beam now fades smoothly around the seal even while the shield is closed.
At its centre the core retains 10% intensity and the helix retains 35%; the
original strength returns outside a 470-unit vertical distance. The transition
starts at 280 units. The open shield further reduces both to expose the target.

A twelfth local visual layer carries a soft, 1100-unit amber aura centred on the
sigil, extending beyond the 740–800-unit ring. Its edge fades away smoothly.
The compact heart is brighter when closed; its existing attack cues remain.
Reduced FX removes the subtle pulse, while the static glow remains visible.
The aura collapses with the other layers on death and reconstructs on save/load.
No map geometry, collision, damage, timing or additional dynamic lights change.
Actual engine evidence is in `tools/validation/source-focus-2026-09-09/`.

## Approved arena follow-up - 2026-09-09

The user approved the following arena extension for the next editing session.
Implemented with the Source defeat finale below:

- Place a monumental, broken rune seal beneath the boss chamber ceiling,
  high above the Source, using the established teleporter/portal rune language.
- Let floating segments illuminate sequentially during attack preparation.
- On shield break, send a light pulse from the ceiling across the hall walls,
  making the whole arena visibly respond to the boss.
- Preserve a clear view of the central sigil and readable combat cues.

The user subsequently approved the five-phase lightning defeat; see below.

## Source defeat finale - 2026-09-09

The approved arena follow-up and five-phase defeat are implemented together.
The original Source actor retains a saved DefeatAge clock instead of fading
away. Living attacks, health and collision stay unchanged. At death the boss
becomes nonblocking and stops its pending attack scripts. The new ending is
scoped to TNT04CN; the legacy BOSSHP branch remains available for other maps.

- 0-1 s: helix holds still and a faint central filament remains.
- 1-3 s: six full-size rune arcs separate, linked by branching lightning.
- 3-4.5 s: eight overhead slabs answer; two separated flashes illuminate the
  architecture while the demon becomes a dark silhouette.
- 4.5-5.5 s: connections break in sequence, glyphs extinguish, and a widening
  gap retracts the two beam halves away from the seal.
- 5.5-7 s: the afterimage and rising sparks fade; overhead stone settles.
- 7-9 s: the empty centre remains visible, the objective notice appears,
  and only then does the original map-99 transition proceed.

Eight horizontal stone segments fit inside the existing shaft, with its own
QROCK3 stone and the established QRUNT63 rune atlas. They light sequentially
during attack preparation and shield opening. Shield opening also sends a
descending light wave over the hall walls. No map geometry is changed.

Presentation uses a bounded pool of 68 local visual layers, eight client-side
stone actors and nine light anchors. Quality zero disables dynamic lights and
embers; reduced FX attenuates flashes and lightning, limits embers and removes
the added oscillation. Neither setting changes the shared clock or ending.
All client presentation reconstructs from the surviving actor after load.
The seven-second electrical score seeks to the restored age, with two major
arcs, smaller severance cracks, and a fading cavern tail. The camera remains
under player control; the additional light bursts below add no blast damage,
full-screen flash overlay or forced camera shake.

Build materials with tools/build_source_materials.py and audio with
tools/build_source_audio.py. Run tools/test_source_finale.py for both renderers,
plus the existing living-encounter, coop and structural checks. Evidence and
actual engine captures are in tools/validation/source-finale-2026-09-09/.

## Orange-red discharge and refraction - 2026-09-10

The nine existing light anchors now flicker between orange and red during the
electrical release, with staggered phases across the chamber. Their intensity
ramps in and dies away before the quiet ending; they add no new light actors.
Reduced effects use a steady, low amber envelope instead of rapid colour changes.

Three eight-ray light bursts leave the seal at defeat tics 105, 134 and 158.
The luminous streaks travel outward, slow, and fade within 23-29 tics. They reuse
the native heart material and a fixed 24-layer extension to the client pool.
Quality one halves the rays; reduced effects show two dim rays per burst;
quality zero removes the extra particles and dynamic lights entirely.

Each discharge also drives an 18-tic expanding refraction wave projected onto
the seal's actual screen position. The scene pass leaves HUD rendering
untouched. The wave fades near screen edges and at distance, is occluded by solid
geometry, and disappears when looking away. Reduced effects, quality zero and
the shader-overlay switch disable it. No camera angles or gameplay RNG change.
The saved defeat clock determines the pulse phase, including after loading;
the presentation handler clears the shader on load, unload and every idle frame.

Rebuild source materials with tools/build_source_materials.py. Regression:
tools/test_source_impact.py covers the three pulses, save/restore, shader toggle,
reduced effects, quality zero, looking away and cleanup in TNT04C. Existing
finale tests retain the real nine-second ending and empty-centre assertions.
Evidence: tools/validation/source-impact-2026-09-10/. Images are direct engine
captures. The shared tutnt.pk3 is built from the complete live integration tree
with tools/build_utnt.py, preserving other local improvements.
