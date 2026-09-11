# TNT04CN — The Source

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
  a 2.5-second luminance fade before the original destination transition. Living
  health, collision, random calls, spawn sites and attack delays remain.

ACS adds three attack notifications, the TNT04CN-specific finale ending in
`source/tutnt.acs`, and a shield-impact notification in TNT04CN script 120. The map's TEXTMAP and
nodes are byte-identical. TNT04C retains its original visuals and map bytes.

## Implementation and limits

`UTNT_Source.zc` adds presentation bases to the existing Source and Guardian
classes. Saved boss fields describe attack, shield and defeat state. Seventy-two
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

- 0-1 s: the helix holds still and a faint central filament remains.
- 1-2 s: the seal fractures and a black core forms inside its luminous rim.
- 2-4.5 s: detached native runes and light trails spiral inward faster and
  faster. The beam contracts toward the seal and the scene bends toward it.
- At tic 158 (4.514 s): the core collapses into a white-gold point, accompanied
  by one light break and an expanding, thin refraction ring.
- 4.5-7 s: the ring fades and the remaining embers return to the empty centre;
  overhead stone settles and the energetic sound decays into cavern echoes.
- 7-9.5 s: the objective notice appears while the empty room fades to black.
  Shadows disappear first and highlights linger; the original map-99 transition
  waits until tic 333, four tics after full black at tic 329.

Eight horizontal stone segments fit inside the existing shaft, with its own
QROCK3 stone and the established QRUNT63 rune atlas. They light sequentially
during attack preparation and shield opening. Shield opening also sends a
descending light wave over the hall walls. No map geometry is changed.

Presentation uses a bounded pool of 72 local visual layers, eight client-side
stone actors and nine light anchors, plus one temporary subtractive light during
the black-hole phase. Quality zero disables dynamic lights and
embers; reduced FX attenuates flashes and lightning, limits embers and removes
the added oscillation. Neither setting changes the shared clock or ending.
All client presentation reconstructs from the surviving actor after load.
The seven-second Near/Far implosion mix seeks to the restored age; its
collapse is aligned with defeat tic 158, after 100 ms of silence. The camera remains
under player control; the collapse light adds no blast damage,
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

The initial three outward bursts were replaced by the visible implosion on
2026-09-10. Twenty-four bounded layers now carry twelve detached native runes
and twelve light trails. Their accelerating angular motion and shrinking orbits
lead into a black core, with an oblique amber accretion ring. Four additional
layers render the core, accretion ring, collapse point and outgoing light ring.
The old seal shrinks behind the core, so the endpoint reads as energy being
consumed. No moving physical objects or damage are added.

Before collapse, the camera-local scene pass bends light radially inward with
a restrained twist. At collapse it releases one expanding refraction front.
It follows the actual projected seal, fades near the screen edge and at distance,
and respects occlusion. The HUD is untouched. Reduced effects, quality zero and
the shader-overlay switch disable refraction; reduced effects also attenuate
lightning, flashes and orbiting particles. The saved defeat clock reconstructs
all phases after loading; idle frames, load and unload clear the scene shader.

## Visible implosion and Near/Far sound - 2026-09-10

The sound combines Klerrp's **Implosion Near** (Freesound 121942) and
**Implosion Far** (121941), both released under CC0. Near supplies the sharper
energy component and Far the low-frequency body. Reversed portions build the
suction before a 100 ms gap; both forward impacts begin at 158/35 seconds.
The final mix is mono PCM, 44.1 kHz, seven seconds, with headroom and a fading
cavern tail. It uses the existing sound channel and saved playback
seek, with no extra sound actors or repeated one-shot triggers.

The authenticated original downloads were not used. Reproducible source WAVs
were decoded from Freesound's publicly available high-quality MP3 previews;
`tools/audio/utnt-source/sources.json` records the URLs, hashes, conversion gains
and CC0 provenance. `tools/build_source_audio.py` needs NumPy and builds fully
offline from those checked-in WAVs. Distribution credits accompany finale.wav
in `sounds/utnt-source/README.txt`.

Build materials with `tools/build_source_materials.py`. Runtime regression:
`tools/test_source_implosion.py` verifies inward motion, black-core visibility,
save/restore, the single collapse and empty centre on OpenGL and Vulkan.
`tools/test_source_impact.py` checks scene-shader toggles, reduced effects,
quality zero, looking away and map cleanup. `tools/test_source_finale.py` retains
the actual nine-second ending and saved finale; `tools/test_source_coop.py`
checks opposing client settings against the same authoritative encounter.
Local evidence: `tutnt/.codex/logs/source-implosion/`. Screenshots there are
unaltered engine captures. The shared tutnt.pk3 is built from the complete live
integration tree with `tools/build_utnt.py`, preserving other local work.

## Vulkan performance correction - 2026-09-11

A reported fall to roughly 5 FPS during the implosion prompted a material and
frame-time audit. The previous presentation registered 87 beam shaders and 25
sprite shaders. Advancing the defeat clock selected new materials, and first
use of those materials coincided with visible frame-time spikes.

Beam phases now share two shader programs; all 25 sprite roles share one more.
A one-texel state image supplies the phase or sprite role instead of compiling
that value into a separate program. Beam carriers are 1x1 pixels, with their
original logical wall dimensions. Procedural sprite carriers are 2x2 pixels,
with the same 512x512 logical size and centred offsets. SOURA0, QRUNT63 and
QROCK3 remain the original artwork. The builder removes only its obsolete
per-role/per-phase shader outputs. The 72-layer pool and all trajectories,
colours, audio and saved timing remain unchanged.

The spent beam loses its middle texture at the collapse, eliminating invisible
wall-material rendering. Dormant layers skip geometry and texture work. Empty
regions of large ceiling/arc quads exit before atlas sampling. Refraction skips
pixels outside its influence and is enabled only while displacement is nonzero.
The nine broad defeat lights retain their placement, colour and radius, but do
not request shadow maps; living encounter lighting keeps its prior flags.

`tools/profile_source.py` measures untrimmed render-to-render intervals at the
same fixed camera, without a frame cap. Compare the same immutable full PK3
sequentially, using `--baseline-ref 430c0823d` for the original Source materials
and omitting it for the optimized version. The script records raw samples and
phase statistics, including first-use stalls. These measurements are local
hardware results, not a minimum-FPS guarantee for every Vulkan device.

`tools/test_source_implosion.py` additionally verifies physical carrier sizes,
unchanged logical dimensions and removal of the spent beam. The living battle,
OpenGL/Vulkan finale, saved reconstruction, FX switches and real ending remain
covered by the existing tests. Local evidence is under
`tutnt/.codex/logs/source-performance/` and `.codex/validation/source-performance/`.

Measured on Ryzen 9 7950X / RTX 4080, Vulkan with shadow maps enabled, in a
sequential A-B-B-A comparison of the same complete package: average finale frame
time decreased from 5.26 ms to 4.48 ms (about 15%). Worst frames per run decreased
from 36.67/46.17 ms to 11.63/22.09 ms. The user's reported 5-FPS drop was not
reproduced on this test setup; the result demonstrates reduced work and shorter
stalls here rather than guaranteeing an identical gain on other hardware.

## Amber opening glare - 2026-09-11

The defeat sequence opens with one continuous orange/amber exposure swell:
13 tics of rise, a hold through tic 49, then a smooth fade through tic 140
(four seconds total). The centre clears as the dark singularity becomes dominant. The existing centre halo widens and brightens;
no actors, particles, lights or material programs are added. Reduced effects
retain only a quiet world halo and suppress the screen glare.

The existing Source postprocess supplies a broad amber veil and a warmer bright
centre, strongest when looking directly at the visible seal. Distance, camera
angle, occlusion, shader-overlay and FX-quality gates remain in force. HUD and
camera orientation are unchanged. The opening path samples the scene once;
from tic 70 the glow overlays the existing gravitational refraction, clearing
the central void while the surrounding amber illumination fades. Timing
comes from the saved defeat clock, so loading does not restart the swell.
`tools/test_source_glare.py` covers the opening, saved reconstruction, looking
away and effect switches; actual captures are reviewed on OpenGL and Vulkan.

## Textured energy and ring clearance - 2026-09-11

The beam and helix share the same two material programs and original wall
carriers. Upward-flowing noise, uneven edges and thinner hot filaments replace
the clean laser-like lines. Sparse native QRUNT63 runes and sparks travel up
both streams directly in the material; there are no new particle actors, light
anchors, spawn loops or gameplay random calls. Glyph sampling is confined to
small cells, and empty beam/helix regions return before noise or atlas work.
The existing near-boss attenuation, shield states and collapse remain intact.

The ceiling pieces explicitly discard pixels outside their stone silhouettes,
so empty rectangular carrier regions cannot write depth. Alpha stays just below
one, including after loading, avoiding the renderer's opaque flat-sprite path.
All eight segments turn half a sector (22.5 degrees), aligning their gaps with
the main arena viewing axes; lightning attachment points follow the new angles.
Actual stone still occludes objects behind it. No map geometry is changed.

The long opening glow holds until 1.4 seconds and fades over the following 2.6
seconds. Refraction and amber exposure overlap, but the growing black core is
kept clear. Reduced effects retain their quiet halo without the screen blend.
`tools/test_source_energy.py` captures the ring, restored ring, upper shaft,
energy motion, side view and extended glare, and checks the fixed effect pool.

A single sequential Vulkan pair in the same immutable full test package, looking
up the shaft, measured 17.86 -> 18.18 ms mean frame time with the beam alive and
17.92 -> 20.23 ms over the defeat interval. Neither run contained frames above
50 ms. This is a limited local sample: the richer presentation has measurable
render cost despite retaining the fixed actor and material budgets; it is not
a guarantee against stalls on every device or graphics configuration.

## Continuous plasma and the dark ending - 2026-09-11

The energy noise now uses an integer hash. This keeps shared noise-cell corners
identical and removes the hard rectangular steps seen on the textured helix and
core. The world-space cylinder, rough filaments, rising glyphs and actor budgets
remain unchanged. The correction is in both generated shared beam materials.

A single client-side `UTNTSourceGravityLight` follows the singularity from tic 35
to 157. Its subtractive, attenuated light affects geometry within 2800 map units,
without sprite lighting or a shadow map. A smooth saved-clock envelope rises
until tic 85, holds through tic 120, and fades back to normal illumination by
158. Reduced effects lower its peak alpha from 0.85 to 0.30; quality zero removes
it. Loading a save reconstructs the current envelope rather than restarting it.

The existing scene postprocess handles a separate quiet ending from tic 245.
Pixel luminance determines when each part of the image disappears: dark rock
fades first, while bright fire and energy remain longer. The 84-tic fade ends
at tic 329; the authoritative BOSSHP exit waits four more tics, for a total
transition of about 2.51 seconds. It applies across the room even when looking
away and remains enabled with reduced/disabled combat effects. It needs the
hardware renderer, as do the other Source materials; HUD rendering is separate.
No second postprocess pass, gameplay shake or new particle pool is added.
Map unload disables the shader and destroys the temporary light.

Validation: `test_source_darkness.py` checks the light count/flags and envelope,
quality toggles, save restoration, rendered black and cleanup on TNT04C.
`test_source_finale.py` checks the real ACS ending: TNT04CN still exists at tic
325 and subsequently transitions through the original exit. Vulkan and OpenGL
pass 38 darkness assertions and 97 finale assertions each. Near and upper-shaft
captures verify the continuous textured spiral. Fixed-clock comparisons isolate
the subtractive light and show shadows disappearing before bright portal/fire
pixels during the ending. Local evidence is under `.codex/logs/source-seams/`.

A sequential Vulkan comparison on the same full test PK3, using prior Source
resources from `6f532cf49`, observed mean finale frame intervals of 28.542 ms
before and 28.571 ms after, with no interval over 50 ms. This hidden-window
sample ran near 35 Hz in both cases and is only a stall check, not a reliable
measurement of small GPU costs or a guarantee for other systems. The only added
world light has a fixed radius and no shadow map; the final fade reuses the
existing postprocess and samples the scene once.

The gravity-light radius was doubled from 1400 to 2800 map units on 2026-09-11
to partially darken the shaft above the seal. The centre, fade envelope, peak
strength and single shadowless light actor remain unchanged.
