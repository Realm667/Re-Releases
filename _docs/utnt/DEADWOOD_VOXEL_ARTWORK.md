# Deadwood voxel artwork

Eighteen indexed, native-grid sculptures. `xyz` in each NPZ contains integer x/right, y/back, z/down coordinates; `colors` contains original low-resolution sprite palette indices. No RGB texture or high-resolution replacement is used. `plans.json` stores per-design branch depth guides, trunk ranges and hollow-stump wells. `sources.json` binds source patch and artwork hashes. Active runtime PLAYPAL changes still apply to these indices.

The two `approved_reference` grids are authoritative, reviewed artwork: weathered tree B and hollow stump B. Their source-facing projection and approved KVX output must remain unchanged unless intentionally reviewed. Normal authoring runs preserve these grids.

The other sixteen grids can be regenerated with:

```
python -m pip install -r tools/requirements-deadwood-artwork.txt
python -B tools/author_deadwood_voxels.py
python -B tools/build_voxels.py
python -B tools/build_voxels.py --check
```

Use `--names` to regenerate selected designs. The authoring tool needs NumPy, SciPy and scikit-image. Normal builds need only NumPy, already used by the voxel build tools. Review four cardinal and four diagonal views in the engine after geometry or material changes. The native grid is artwork and can also be refined directly, with an intentional manifest update and the same review checks.

The exporter reverses the stored Y columns to match the engine's source-facing orientation. All 24 bindings independently decode and check their actual KVX front: native source pixels for the 18 original views, cell-center resampled source pixels for the six existing frozen size variants. Runtime scale is one; authored actor scales remain intact.

Connectivity follows the source silhouette. Tiny disconnected pixels deliberately present in a source patch remain present; each source-connected branch/root mass is connected using 26-neighbor grid connectivity. No new projected pixels are added merely to join original detached source pixels.
