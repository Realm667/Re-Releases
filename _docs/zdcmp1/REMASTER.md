# ZDCMP1 remaster follow-up

## Player-facing changes

The full and simplified engine menus each have one **ZDCMP1 Options** entry.
Display & Accessibility, HUD & Statistics, Audio, Gameplay Comfort, Shared
Effects (Host), Gore (Host), and Hint Logbook live below that entry. The mod no
longer replaces the engine's simplified options menu. Existing user values
are retained; Max remains the default and no global audio/video preferences
are changed.

The logbook remembers only messages actually delivered by MAP01's supply,
pump, gear, main-door, surface-teleport and damaged-lift scripts. Personal
messages remain personal; broadcast messages go to connected players. Hints
are deduplicated, survive new-version saves and coop respawns, and reset with
the map. Hiding the logbook does not erase its history. A key can be assigned
under Gameplay Comfort; no existing key binding is overwritten. This is not
a quest compass and does not reveal undiscovered secrets or hard-skill hints.

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
