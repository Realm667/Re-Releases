# Campaign-wide portal coverage — 2026-09-09

The source audit reads all 14 map WADs, including binary Hexen maps and UDMF
with editor comments. It found 117 visible portal middle-wall surfaces:

| Map | Surfaces |
| --- | ---: |
| ENDMAP01 | 30 |
| TNT03B | 5 |
| TNT04A | 5 |
| TNT04B | 15 |
| TNT04C | 32 |
| TNT04CN | 30 |

This is a sidedef count, not a count of physically distinct portals. Several
openings have both faces, multiple depth planes or five adjacent arch segments.
The eighteen formerly skipped four-unit strips now share the same texture
coordinates as their surrounding arch. Group fitting accounts for segment
height and lower unpegging without changing any line flags or map geometry.

Each affected map passed the expected material count, absence of remaining old
portal middle textures, automatic-source presence/absence and save/load UV
alignment checks. TNT03A1, TNT03A2 and TNTLE passed negative coverage checks
for their different teleporter types. Seven assertions per map, nine maps.
The source audit also identifies five hidden upper-wall texture assignments;
their sectors have no visible upper gap on those sides. They and floor/ceiling
teleport textures remain unchanged.

Automatic decorations in TNT04CN were checked under Vulkan and OpenGL for
working local lights and particles, effect quality 0 cleanup, and recreation
after save/load. Completion requires the post-load assertions, not just a
successful process exit. Scripted credits/chapter overlays can cover the test
camera; those images are evidence of the actual runtime, not retouched previews.

The shader artwork itself is the approved v2 material; its earlier final-package
and fixed-time normal/parallax evidence remains in `../portal-2026-09-09/`.
This revision changes mapping and local source placement, not the artwork.

Both placed decoration sizes passed the existing 206-assertion Vulkan lifecycle
suite again after the grouping/source changes. Two local network peers in
TNT04CN, with effect quality 3 and 0, passed three automatic-emitter assertions
each; toggling quality affected only the respective client, with no reported
consistency failure or VM abort. WAN multiplayer was not tested.

All 14 ACS modules compiled with unchanged bytecode in an isolated committed
baseline plus this task's changes, and that PK3 passed engine load. The visual
and lifecycle runs used the same portal runtime. Final formatting removes only
extra blank lines at EOF. No other task's staged changes belong to this commit.
