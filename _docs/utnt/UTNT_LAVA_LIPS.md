# Rounded lava spill edges

QLAVA, QLAVA2 and QLAVASB floors now flow into LAVA/LAVAHR lower walls through
a small rounded render mesh. The normal build detects every qualifying edge:
the opposite lava floor must be higher than the sector viewing the lower wall.
Upper walls, middle textures, rock walls, water and equal-height boundaries do
not qualify. The current maps produce 127 candidates: TNT02 (9), TNTLE (118).
TNT02's startup script equalizes sectors 109/113; that lip correctly stays
hidden while the drop is zero. Eight are initially visible there, 118 in TNTLE.

The lip is a shallow liquid meniscus, at most four map units above/outside the
old corner, with twelve segments through the curved nose. Short lines and
small drops reduce its size; connected segments share a radius and mitered
endpoints. The source WADs, original texture IDs, collision, sector tags,
damage, triggers and terrain are preserved. This is visible geometry, not
vertex displacement or a change to the player's collision surface.

The generated material evaluates the current surface and fall shaders and
blends albedo, brightmap and normals across the lip. Its two ends feather into
the original surfaces. Source assets still use PLAYPAL. The existing horizon
material remains unchanged; its closing-strip coordinate reconstruction is
not applied to lip models. A transparent sprite hides the helper if its model
cannot be rendered. OpenGL and Vulkan are the validated rendering paths.

`tools/build_utnt.py` regenerates models, material variants and map registration
before taking its immutable source snapshot. `--check-only` rejects stale
assets. The generator validates the shader entry point, writes files atomically
and removes only previously inventoried obsolete model/registration files.
It does not rewrite maps. Rebuild after editing map boundaries or materials.
The dedicated generator can also be run with `python tools/build_lava_lips.py`.

At load time, the handler validates edge coordinates, side/sector identity,
floor slope against its generated registration. Stale entries are rejected,
leaving the original surface visible. Each nonblocking actor follows vertical
motion of its upper sector, including movement before installation. Switching
between the three lava floors and two falls updates its material. A non-lava
texture, insufficient drop or changed slope hides its lip; restoring valid
conditions restores it. Save/load serializes these actors and their handler without
duplicating them. New topology and newly qualifying edges require a rebuild;
arbitrary runtime topology/slope changes do not regenerate a model.

Validation: `tools/test_lava_lips_structure.py` checks the material rule,
reversed linedefs, all six material pairs, nonmatches, small drops, slope
endpoints, connected geometry and containment of the old sharp silhouette.
`tools/test_lava_lips.py` creates an isolated angled two-segment fixture and
checks nonblocking actors, visible instances, changed floor height, invalid
texture fallback/restoration and save/load. It can also inspect TNTLE/TNT02.
Renderer 0 is OpenGL, renderer 1 is Vulkan. Runtime records and selected direct
screenshots are under `tools/validation/lava-lips-2026-09-09/`.

No full campaign playthrough or general performance improvement is claimed.
