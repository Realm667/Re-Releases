# ZDCMP1 remaster follow-up

## Player-facing changes

The full and simplified engine menus each have one **ZDCMP1 Options** entry.
Display & Accessibility, HUD & Statistics, Audio, Gameplay Comfort, Hints & Logbook, Automap, Shared
Effects (Host), Gore (Host), and Hint Logbook live below that entry. The mod no
longer replaces the engine's simplified options menu. Existing user values
are retained; Max remains the default and no global audio/video preferences
are changed.

The main menu uses a 179 x 57 M_DOOM base patch and its exact 3x HiRes image, so UZDoom no longer stretches the 537 x 171 logo against Doom II's 125 x 60 patch. A silver two-frame M_SKULL selector matches the logo. The skill menu draws localized UZDoom skill names in BIGFONT instead of the original label patches; the five skill gameplay properties, default skill and Nightmare confirmation are preserved.

The logbook remembers only messages actually delivered by MAP01's supply,
pump, gear, main-door, surface-teleport and damaged-lift scripts. Personal
messages remain personal; broadcast messages go to connected players. Hints
are deduplicated, survive new-version saves and coop respawns, and reset with
the map. Hiding the logbook does not erase its history. A key can be assigned
under Hints & Logbook; no existing key binding is overwritten. This is not
a quest compass and does not reveal undiscovered secrets or hard-skill hints.
The automap adds markers only for received observations and explicit gear/pump
objectives; it never enables map cheats or changes the discovery of geometry.

Camera previews automatically hide the mod HUD and motion blur, then restore
them on return. The boss finale does the same without asking players to edit
their settings. USE can skip the finale once it begins; in coop only the
engine's current network arbitrator (host) can do so. This is edge-triggered, respects the host's skip
option, stops finale producers, restores camera/control and uses the normal
level exit. Ordinary puzzle previews retain their original timing and actions.

Freezer screen-flash strength is a per-player slider. Nuke camera shake is a
host-controlled switch because the quake is a synchronized world effect.
Both default to their full original values. Neither changes damage, ammo,
projectile density, weapon timing or explosion actors. They are not a blanket
photosensitivity mode: map flicker and other effects remain present.

## Skybox remaster

MAP01 retains its outdoor and Hell SkyViewpoints, the Hell SkyPickers
(viewpoint ID 47), and all playable geometry. The two isolated camera
rooms are square 312-unit cubes centered on their original viewpoints.
Outdoor sector 740 spans 152..464; Hell sector 2635 spans 0..312.
Both cameras stand 156 map units above their floors. Both sectors use
GZDoom's Skybox Sector special 90 for skybox surface rendering. MAP01
also sets `disableskyboxao` in MAPINFO, preventing SSAO in camera portals
while leaving ambient occlusion active in the playable map. Wall sides
disable fake contrast and anchor their textures at the ceiling.

Editable source panoramas live in `zdcmp1/source/art/skybox/`; the
reproducible projection is `tools/generate_zdcmp1_skycube.py`. It samples
the same spherical direction for every shared cube edge, generating
1024-pixel top/bottom faces and two exact 512-pixel halves per side.
The landscape base sits at eye level; the raised ridges remain visible above
MAP01's perimeter walls from normal player height. The four landscape faces
never animate. Ceiling/floor projection follows GZDoom's actual UV direction
and covers the full 320-unit sector bounds, including the four-unit apron
behind the 312-unit wall ring. This prevents the former square ceiling seam
without hiding cloud detail. The Hell wall ring faces inward, like the outdoor
ring. Only these isolated camera-room vertices were corrected; gameplay
geometry, SkyPickers, ACS and the serialized day/night/storm clock are unchanged.

The outdoor panorama grades its nearest mountain chains toward warm brown
`#64523E`, the farthest toward cool grey `#424449`, with intermediate ridges
and haze preserving depth. The editable Imagegen source and exact edit prompt
are stored in `zdcmp1/source/art/skybox/outdoor-source.png` and
`outdoor-depth-color.txt`. The hex values describe base material colours;
lighting and atmospheric haze vary individual pixels.

Both sky viewpoints have bounded translational parallax, managed by
`ZDCMP1SkyParallax`, a nonserialized client-side thinker. Each client reads its
own current camera, including a spectated player, and offsets only the two
noninteractive native SkyViewpoints. No player position, geometry, sector
colour, portal assignment, random stream or shared weather clock is changed.
The horizontal response starts at 1/384 of world motion and smoothly saturates
at a 24-unit radius; vertical response starts at 1/768 and saturates at 8 units.
Authored origins and fixed world anchors prevent save/load drift. Teleports
and viewer changes clear interpolation; ordinary movement interpolates.
The same camera path works for hardware and software rendering.

The focused multiplayer test `tools/test_zdcmp1_sky_parallax.py` launches two
real peers. It checks independent positions in both skies, one player moving
while the other remains still, spectator camera swaps and matching world
clocks, with 20 assertions per peer. It writes local evidence under `.codex`.
The revision was also checked in UZDoom 5.0.3 on Vulkan, OpenGL and software,
with day/night/storm screenshots. Save/load and MAP01 -> MAP02 -> MAP01
retain exactly one local camera controller and reproduce the same offsets.
Software retains its existing palette/lighting limitations.

Each cap has eight ANIMDEFS frames. A separately generated, tileable
cloud mask shifts by at most 16 pixels across those frames and modulates
only the cap interior. Each frame lasts 20 tics. The layer moves gently;
the surrounding mountains and wall clouds remain fixed, and the cap
perimeter does not change. The old ACS ceiling scrollers on tags 32 and
113, including the storm acceleration, are removed because they moved
the complete ceiling image through its seam. No custom shader is needed.
The same authored frames run on Vulkan, OpenGL and the software scene
renderer. Software uses explicit 320-unit flat scale and world offsets to
match the special-90 hardware projection. Its palette and lighting remain
less smooth than the hardware renderers. No custom shader is required.

Validation: 15 integrity tests plus three image-space tests cover inward
wall winding, sector bounds, matching wall corners, wall/cap intersections,
static animation edges and changing cloud interiors. UZDoom 5.0.3 was checked
with Vulkan and OpenGL (SSAO enabled), and the software scene renderer, from
the start courtyard, outdoor arena and Hell arena in four directions plus
the zenith. Day, dusk, night, dawn, storm and save/load were exercised. The
49 packaged sky/map/definition files match their editable production sources.
Start MAP01 afresh after this geometry update: older saves retain old map data.

A map-local ZDCMP1SkyCycle EventHandler restores the original 75-second
descent into night and 75-second return to day. Its serialized clock
synchronizes the outdoor skybox, exposed F_SKY1 sectors, and directly adjacent
neutral roofed sectors. Hell sky sectors and their red ambience stay outside
this cycle. Existing authored green/red fades are not overwritten. Night
tints neutral exterior light slightly blue-gray and lowers it without hiding
navigation. The original arena scripts still trigger the thunder timing,
music, and fight; their light fades/flashes now call the
serialized handler so storm, night, and roofed sectors cannot fight over the
same light level. A flash illuminates only the existing tagged arena sectors.
No lightning bolt, lens flare, sun, or unoccluded screen overlay is introduced.

For repeatable inspection on MAP01, the host may use
`netevent zdc_skytime 0|1|2|3|4|5` (day, dusk, night, dawn, resume, status)
and `netevent zdc_skystorm 0|1|2|3` (clear, storm, held test flash, status).
The debug values and the weather clock are saved with the map; normal ACS
events resume their established sequence after loading. MAP01 is the only
ZDCMP1 map, so these sky resources do not alter another map.

## Engine integration

UZDoom 5.0.1 is the tested minimum. The large copied PlayerThink implementation
now delegates normal lifecycle, movement and prediction to the engine. Small
CheckPitch/CalcHeight overrides preserve climbing descent and stationary
camera behavior. The existing specialized CheckJump remains unchanged.
The intended custom intermission class now matches MAPINFO.

MAP01's authoritative ACS source is `zdcmp1/source/maps/map01.acs`. Its initial
extraction compiled byte-for-byte against the previous embedded BEHAVIOR with
ACC 1.60. Editing it requires:

```sh
python -B tools/sync_zdcmp1_map.py --acc /path/to/acc --write
python -B tools/build_zdcmp1.py --acc /path/to/acc
```

The synchronizer changes only SCRIPTS and BEHAVIOR. Geometry, things, node data,
enemy placement and original encounter parameters are untouched. The build
rejects stale bytecode, and integrity tests pin geometry/node hashes.

## Save compatibility and acceptance

Start a new game for this revision. Existing saves embed old ACS execution
state and cannot acquire a reliable history of messages already delivered.
They are not migrated or claimed compatible. Saves created with this revision
are covered by the new tests.

Functional test coverage is recorded in the release checks and local logs:
real MAP01 hints, camera preview and return across save/load; finale entry,
save/load and skip; consolidated menus; coop hint ownership and respawn;
sustained Freezer/Nuke fire at both comfort extremes. The weapon runner also
accepts an immutable previous package with `--compare` for deterministic
walking/jumping/strafe trace comparison. These traces are not exhaustive
movement or campaign coverage.

The complete intended Doom II playthrough remains unverified without its IWAD.
Freedoom tests validate code paths, not Doom II artwork or combat balance.
No new benchmark-based speedup or universal hardware compatibility is claimed.
The previous 30-minute endurance evidence predates these feature changes;
it must not be presented as a new 30-minute run of this revision.

## Previous remaster verification

Both Linux renderer jobs passed every release check for commit `7865619`:
[GitHub Actions run 36330464323](https://github.com/Realm667/Re-Releases/actions/runs/36330464323).
This includes coop, all five skill starts, remaster behavior, sustained weapons,
and the short stress/save-load regression. Later documentation-only changes
do not change the tested package.

Native UZDoom 5.0.1 on Apple M3/macOS, using Freedoom 0.13.0, passed:

- Nine integrity tests, reproducible ACS checks, and unchanged map geometry/node hashes.
- Effect lifecycle and portal/floor/camera suites with both OpenGL and Vulkan.
- MAP01 startup and save/load on all five skills with both renderers.
- Real hint/camera tests (21 assertions), finale/save/load/skip guards (8),
  actual USE during credits (3), and six menu checks with both renderers.
- Sustained Freezer and Nuke fire at both comfort extremes with both renderers;
  peak actor counts and remaining ammunition matched between settings.
- Six deterministic walking, jumping and strafing samples matched the previous
  package exactly under Vulkan, including position, velocity and view height.
- The full unskipped finale and credits reached the normal exit under Vulkan
  with manual skipping disabled (approximately 291 seconds).
- Two-peer native OpenGL coop passed all 14 assertions per peer. Native Vulkan
  coop timed out after connection and is not counted as a pass; Linux Vulkan
  coop passed in release checks. This remains a native-runtime test limitation.

The local release package SHA-256 is
`6abf5f2a3d346279731881a2df2c79ef4742722638fc22f7e1dc9f4ed7a5efd1`.

## Field-terminal design

### Shared SBAR Skin and Automap

The journal, notifications and full automap use native crops of the original
`Graphics/sbar/stbar.png`. The bottom rail mirrors the top metal rail; it never
crops the baked AMMO/HEALTH lettering. The red display uses 88% solid oxblood
blending and 12% original texture. The same treatment applies to the SBAR,
including its ammunition panel, without touching metal, lettering or portrait.
The source PNG is unchanged. `tools/build_zdcmp1_sbar.py` (Pillow) derives exact
red-only rectangle masks and generates the native TEXTURES composition.

**ZDCMP1 Options > Automap** contains the engine's existing mod-color
preference and host-controlled marker/completed-marker switches. Active markers
default on; completed markers default off. Marker
actors are invisible, nonblocking and do not affect combat or item counts.
Native rendering handles rotation, zoom, pan and the overlay map. The automap
uses no additional frame, header or legend. Steel-rimmed red enamel marker
backgrounds match the HUD; objective markers get an amber rim. Map colors
preserve key-lock colors and discovery.

`!` marks explicit gear/pump objectives, `?` marks reported hints/obstacles,
and `+` marks confirmed endpoints when enabled. The gear target moves to the
known broken switch after pickup, then advances through repair, power and
drainage. Door hints retire on activation/unlocking. When the main gate or
teleporter door is reported blocked, an additional `!` marks the actual switch
or console while `?` remains at the obstacle. Reading a log entry never
advances this state. These are script-derived observations, not a new quest
system or secret detector.

**ZDCMP1 Options > HUD > HUD route pointer** defaults on for each player.
The continuously rotating compass needle above the status bar points to the first visible portal on
a route to the next actionable known goal, never merely toward its coordinates.
The live sector graph accounts for floor height, passage width, clearance, blocked lines,
usable/key doors and actor-backed teleport destinations. It is recalculated
every twelve tics. Unreachable routes and stacked 3D-floor sectors yield no
arrow rather than a direction through a wall. A report about a broken switch
or lift is not treated as a walkable destination. Menus, automap, death and
cutscenes suppress the pointer. This is conservative guidance, not a full
navmesh for all geometry or a new hint/quest progression system.

UZDoom 5.0.1's native MapMarker renderer has no per-player filter. To avoid
leaking private observations or desynchronizing the game, coop markers require
the intersection of all connected players' received hints. A completed event
from any player retires obsolete objectives, including after that player leaves.
Hint history is bounded to thirteen entries; at most two additional objective
markers are spawned for the switch and console.
No existing bindings, map geometry, skill gates or Max effect defaults change.

### Journal and Notifications

The journal now implements the UAC field-terminal concept: a dark, two-column
surface, the original SBAR metal frame artwork, a low-texture oxblood header,
readable pale text, amber hint markers, and green checks for confirmed events.
The left list contains only received hints. The right pane shows the selected
hint, its full text and source. Five rows fit per page, with keyboard, controller,
mouse-wheel and mouse-click navigation. Reading selects an entry and removes
its NEW marker; it never completes an objective or reveals an unreceived hint.
Hints remain a history of observations, not an inferred quest-state tracker.

Read acknowledgments are validated against the sending player's received mask
and survive new-version save/load. Confirmed states come only from existing
map events (pickup, repair, power, drainage, door activation). Existing hint
ownership, skill gates, geometry, enemies and gameplay timing are unchanged.

New in-game notices use the same dark surface, amber/green accent and icon.
They fade in over seven UI ticks without flashing, appear one at a time in
delivery order, and last six seconds by default. Duplicate received hints do
not create repeat entries or notices. Notices wait during menus, camera previews,
death, the automap and the finale. Turning notifications off clears their queue, not history.
The old central print/chat calls for these hints are replaced; unrelated map
dialogue remains. The optional local signal uses the existing chat sound at
30% volume and does not modify global sound settings.

All controls are personal and consolidated under **ZDCMP1 Options > Hints &
Logbook**: journal visibility, assigned key, in-game notices, three text sizes,
3-15-second duration, automatic/left/right position, and signal sound. A notice
moves to the opposite top corner if its chosen corner contains the mod's stats.
English is the fallback; German texts follow the engine's selected language.
Both text wrapping and input coordinates share an aspect-preserving layout.
No existing binding or Max effect default is changed.

Start a new game after updating, as described above: old saves contain their
old ACS display calls. Current acceptance remains code-path and UI testing with
Freedoom, not a complete Doom II playthrough or universal hardware guarantee.

Native verification of the field-terminal package passed on UZDoom 5.0.1:
32 field-terminal assertions plus nine real viewport assertions on each of
OpenGL and Vulkan; actual MAP01 remaster tests and seven menu checks on both;
16 assertions per peer in native OpenGL coop; ten integrity tests and ACC 1.60
bytecode verification. Screenshots were inspected at 1280x720, 960x720 and
1680x720, including large German text. The native Vulkan coop limitation noted
above is unchanged. The unrelated UTNT generated-table check cannot run in
this local sparse checkout because `tutnt/cvarinfo` is absent; no UTNT definition
tables were changed.

Field-terminal package SHA-256:
`a4a52f253f58700d1bc12893f3088b4c8edb69ee654d87b9042342545d60661b`.

## MAP01 completion report

After the boss sequence, MAP01 now shows its own report before the original
credits. USE advances to the credits; in co-op only the host can advance. The
existing finale-skip option advances to this report first, then can skip the
credits. MAP01 suppresses the engine's normal intermission at level exit.

The report freezes elapsed time, kills, items and secrets at completion. Health
lost, distance, ammunition and hit/miss counts are tracked per player across
respawns and saves. Distance is horizontal movement divided by 64 map units
per metre; teleport jumps are excluded. A hit is a ranged trigger that damages
at least one monster, so shotgun pellets and blast damage do not inflate hits.
Melee attacks do not consume ammunition and are not included in accuracy.

The score is capped at 10,000 points, with only the agreed eight factors:
enemies 2,400, secrets 1,600, items 800, health lost 1,300, time 900,
distance 500, ammunition efficiency 900, and hit ratio 1,600. Full time
points are awarded at 45 minutes or faster, full distance points at 2,500 m,
and ammunition efficiency compares rounds spent to three rounds per defeated
enemy. The letter thresholds are D < 4,000, C >= 4,000, B >= 6,000,
A >= 7,500 and S >= 9,000. Each factor is capped independently; deaths,
cheats and `nomonsters` have no special score rule. Map-wide kills, items and
secrets are shared in co-op; the other four tracked factors are personal.
