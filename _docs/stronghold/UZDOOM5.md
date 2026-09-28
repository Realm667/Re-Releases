# Stronghold on UZDoom 5.0.3

The editable game sources are in `stronghold/` on `master`. The runtime archive is built from those files without changing them. The compiled ACS object `stronghold/acs/strnghld.o` is versioned alongside `stronghold/acs_src/strnghld.acs`.

## Build and automated checks

From `stronghold/`, run:

```powershell
python -B tools/build_stronghold.py --acc 'F:\DoomDev\Tools\UltimateDoombuilder\Compilers\ZDoom\acc.exe' --build --repro-check --smoke --net-smoke --engine 'F:\DoomDev\uzdoom.exe' --iwad 'F:\DoomDev\DOOM2.WAD' --seconds 11
```

The command recompiles ACS and compares its SHA-256 hash with the versioned object, checks the reviewed clientside actor manifest, builds the PK3 twice and compares hashes, verifies the archive resource list and CRC, loads STR01, STR21 and STR33 with UZDoom, and starts a local two-player host/client session in STR01. An ACC source change requires an explicit `--update-acs` run followed by review of the binary diff.

The local test archive is `tutnt/.codex/builds/stronghold-uzdoom503.pk3`; logs are in `tutnt/.codex/logs/stronghold/`. These paths are local build output and are not Git content. The build selects the runtime resources from the production tree; `acs_src/`, `tools/` and project notes are not packaged. No map or source mutation occurs during packaging. `SCRIPT00.lmp` and `acs/sthldcmn.o` are existing versioned runtime objects without a compiler step in this workflow; the builder verifies and includes them. Thus the source-backed reproducibility check applies to `strnghld.o`, and the byte-for-byte PK3 check applies to the current production tree.

## Changes covered by the checks

- ACS player-indexed state uses the 64-player engine limit. Shop item and player indexes are checked before table access. Map rewards stop at the table limit. End bonuses use a bounded, independent queue for each player.
- The former `CLIENTSIDEONLY` flags are recorded class by class in `stronghold/tools/clientside_manifest.json`. Fourteen visual effects use the supported `CLIENTSIDE` flag. Actors with collision, spawning, damage or other world effects remain in world simulation. `tools/check_clientside.py` rejects reintroduced legacy flags and drift from these decisions.
- Overlay rendering visits the local player's inventory directly and handles an absent player pawn. The motion blur network update is limited to one per game tic while its shader uniforms still update in the UI frame loop.

The automated game checks establish that the mod parses, the selected maps start, and a two-player session connects. They do not prove the result of every wave, shop transaction, save/load cycle, actor attack or visual shader. For a release playthrough, inspect those interactions in game, including a buy with insufficient funds, simultaneous player bonuses, wave completion, saving and loading STR01, and underwater and motion blur effects. Keep any screenshots, saves and logs under the central `tutnt/.codex/` workspace.
