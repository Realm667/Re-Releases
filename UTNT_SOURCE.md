# TNT04CN — The Source

The final boss now uses the approved three-state presentation: an intact runic
shield, six separated rune arcs around the exposed heart, and a damaged seal
with staged comet charging. The original horned demon sigil stays at the centre.

The five lit signs in the original RUNE1/3/5/7/9 switch patches supply the rune
alphabet. TEXTURES assembles them with their unlit partners; material chroma
separates each red sign from its grey stone backing and lights it in Source gold.
SOURA0 and all original rune patch files are unchanged. No new raster artwork is
required for these effects. Approved AI mockups and their prompts are retained
under `tools/artwork/source/`; they are concepts, not runtime screenshots.

## Battle feedback

- The narrow central beam and continuous world-space spiral use the existing
  wall geometry, including its translated upper room. The map topology is intact.
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
- Death collapses the local seal and extinguishes the beam. Original boss exit,
  music, health, collision, random calls, spawn sites and attack delays remain.

The only ACS changes are three visual attack notifications in `source/tutnt.acs`
and a shield-impact notification in TNT04CN script 120. The map's TEXTMAP and
nodes are byte-identical. TNT04C retains its original visuals and map bytes.

## Implementation and limits

`UTNT_Source.zc` adds presentation bases to the existing Source and Guardian
classes. Saved boss fields describe attack and shield state. Eleven bounded
VisualThinkers and one light anchor live only on each local client and rebuild
after loading. Essential target/shield/attack indications remain with FX quality
zero. Reduced effects disable ornamental roll and pulse motion where specified;
dynamic lighting follows local effect quality. No gameplay random stream is used.

The materials target UZDoom 5.0.1 OpenGL/Vulkan. A software renderer cannot show
the procedural ring masks, glyph isolation or state materials. The existing
polygonal beam wall silhouette is retained; it is not a new high-poly cylinder.
The continuous spiral follows that silhouette rather than altering collision or
stacked portal geometry. Old-save compatibility and WAN multiplayer are not
claimed by the local tests.

## Reproduce

1. Run `python tools/build_source_materials.py` after editing the three
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
