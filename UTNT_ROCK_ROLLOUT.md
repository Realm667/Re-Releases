# Large rock surface rollout

QROCK1, QROCK3, QROCK4 and QROCK5 now have expanded variants used on selected
large static walls. Original material names remain intact. Three new generated
images join the previously approved QROCK3X8 asset. Each expanded tile covers
1024x1024 map units, preserving the intended local rock feature scale.

| Map | New wall sections | Groups |
| --- | ---: | ---: |
| TNT01 | 88 | 9 |
| TNT02 | 226 | 17 |
| TNT03A1 | 40 | 1 |
| TNT03A2 | 60 | 4 |
| TNT04A | 33 | 3 |
| TNT04B | 435 | 32 |
| TNT04C | 46 | 9 |
| TNT04CN | 337 | 85 |
| TNTLE | 466 | 27 |

Total: 1731 additional sections in 187 groups. QROCK3 accounts for 1622,
QROCK1 for 78, QROCK5 for 28 and QROCK4 for 3. The existing TNT04B pilot's
23 sections remain untouched. No changes were selected for TNT03B.

## Selection and alignment

The authored-area inventory is followed by stricter surface checks. Groups
need at least 262144 square map units and either 1024 units of wall length or
a wall section at least 512 units high. Visible upper/lower heights are clipped
to the front sector; two-sky uppers and masked middles are excluded.

Movement specials and literal ACS movement targets exclude affected sectors.
Unknown ACS movement arguments exclude tagged sectors conservatively. Slopes,
custom scales/skew, special/addressable linedefs and small areas stay unchanged.
This is a conservative static filter, not an exhaustive gameplay analysis.

Unambiguous adjoining faces with vertical overlap follow their actual line
lengths around bends. Local tier offsets establish a shared vertical reference
and preserve peg flags and global offsets. Branches form separate groups.
Fourteen closed groups place their phase cut at the sharpest corner (at least
45 degrees); smooth closed groups remain unchanged. Material transitions,
branch boundaries and these deliberate closing cuts are not claimed seamless.
There are 1433 aligned inner joins, with maximum error below 1e-9 map units.

The original patch style, feature density and dark palette were checked against
the generated assets. Repeating-background reviews check wrap appearance;
individual contours at image edges are not guaranteed to match mathematically.
QROCK4's mean luminance rises about 2.2 on a 0-255 scale, while QROCK1 rises
about 1.1 and QROCK5 about 0.2. PNGs are unretouched image-generation outputs.

## Preserving concurrent map work

Installation replays only recorded per-tier texture/offset changes onto the
CURRENT map after verifying line, sector-plane and mapping context. It never
replaces the current map with the frozen preview WAD. Every current vertex,
linedef, sector, thing and all non-TEXTMAP lumps are compared before/after.
The new TNT04B skybox, including all 19502 vertices at integration, is preserved.
See tools/artwork/rock-rollout/skybox-preservation.json for source/result hashes.

## Reproduction

`tools/expand_rock_walls.py --root tutnt --actions
tools/artwork/rock-rollout/action-names.json --output candidate` writes separate
candidate maps and a manifest. It never writes the source tree. Its `replay`
function applies the recorded delta only while original mapping context and
per-field preconditions still match; it also accepts already-applied fields.
The action-name table is derived from the project's ACC zspecial.acs.

Run `tools/test_rock_alignment.py` for focused algorithm regressions, and
`tools/test_rock_rollout.py --engine ... --iwad ... --work-dir ...` against the
built main package. Renderer 1 is Vulkan, renderer 0 OpenGL. Test cameras and
handlers live outside tutnt and never ship with the game.

Tools/artwork/rock-rollout records the source patches, generation prompts,
scope manifest and independent static validation. Runtime evidence and visual
comparisons are stored under tools/validation/rock-rollout-2026-09-09.
These checks cover mapping, rendering and save/load; no full campaign
playthrough or performance benchmark is claimed.
