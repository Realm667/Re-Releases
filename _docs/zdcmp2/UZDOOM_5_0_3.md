# ZDCMP2 on UZDoom 5.0.3

## Editable source and release package

`zdcmp2/` is the editable production tree. `tools/build_zdcmp2.py` verifies that
ACC 1.60 reproduces `zdcmp2/acs/zdcmp2.o` before packaging the tree into a
deterministic PK3. The default test output is
`tutnt/.codex/builds/zdcmp2-release.pk3`. The local `zdcmp2.pk3` at the repository
root is an ignored, published package; it is built from the same source after
the checks pass. Do not commit the package or temporary test output.

```text
python -B tools/build_zdcmp2.py --acc /path/to/acc
python -B tools/test_zdcmp2.py --engine /path/to/uzdoom --iwad /path/to/doom2.wad --acc /path/to/acc --renderer 1
python -B tools/test_zdcmp2.py --engine /path/to/uzdoom --iwad /path/to/doom2.wad --acc /path/to/acc --renderer 0
```

The GitHub Actions workflow pins the UZDoom 5.0.3 Linux release and checks
both renderers. Its smoke test covers parsing, a map start, representative
actors and weapons, save/load, and the ACS-to-ZScript message queue. It is not
a full playthrough or a 64-player network test.

## Runtime boundaries

- ACS still owns the objective/log globals consumed by SBARINFO. A short lived
  ZScript dispatcher starts each ACS message consumer with the corresponding
  player pawn, avoiding the old eight-player AAPTR selector limit.
- Motion blur updates in `WorldTick` and sets shader uniforms in `UiTick`. It
  no longer sends a network event each UI frame.
- The custom shader handler scans only the local player's inventory instead
  of all shader-control thinkers. Effect-giver lists remove stale entries and
  iterate backwards when deleting.
- The terrain table includes only flat names available to the shipped package;
  mappings for external texture packs are not bundled by default.
- The controls menu extends UZDoom's native menu so new engine controls and
  controller bindings remain available. SBARINFO popup coordinates and ACS HUD
  messages retain their virtual resolutions to preserve their layout.
