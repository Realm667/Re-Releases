# Editable production sources

User rule, 16 September 2026: `tutnt/` is the authoritative, editable production
tree. All final runtime assets must reside there. `.codex/` is local agent work,
is excluded from packages, and must never be required to play the release.

Zip the **contents** of `tutnt/` at the archive root, not a containing `tutnt/`
directory. Exclude `.codex/`, editor state, backups, autosaves and authoring-only
artwork. Required generated images/models/definitions and compiled ACS must
already be present in their regular production paths. Refresh documented compiled
tables/ACS after changing their sources; normal packaging must not silently
replace hand-edited final maps or visual assets.

The standard builder remains `python -B tools/build_utnt.py`: it validates,
compiles and checks the engine, and excludes local work. New work must keep final
content in the source tree and document any explicit regeneration workflow.

## Current verified scope and remaining distinctions

TNT03A2's cavern map, meshes, placements and light/fog values are directly
editable. Its normal build step validates without regenerating them; there is
no package-only cavern map patch. A directly zipped candidate passed real-engine
OpenGL save/load and hub-return tests. See [cavern editing](UTNT_CAVERN.md).

A direct ZIP is not byte-identical to the standard package: the latter expands
TEXTURES modules (preventing the existing source-directory texture-loader
warning), appends native model precache lists, and adds build identity/labels.
Other existing generators still have documented source inputs and refresh their
production outputs. This task does not claim to have migrated every legacy
generator to manual asset authoring. Future work must preserve user edits,
identify authoritative inputs/outputs and report any remaining exception.
