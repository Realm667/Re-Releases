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

## Generator consistency for release checks

The 25 September release audit found that build_utnt.py --check-only could stop
before ACS compilation: a Windows checkout had converted the generated TNT04B
heat table to CRLF, and the organic-material and custom-brightmap manifests
still recorded texture inputs from before later texture-module additions. The
local-heat files and manifest now have LF checkout rules in .gitattributes.
The two manifests were refreshed through their respective generators; their
runtime material, mask, model and shader outputs remained byte-identical.

After editing texture definitions, run tools/build_definition_tables.py, then
tools/build_organic_materials.py and tools/build_custom_brightmaps.py with
the configured IWAD. Review their diffs before a release build. If a map edit
changes lava geometry, refresh tools/build_local_heat.py and inspect the
resulting heat-volume rows. Run tools/build_utnt.py --check-only to verify
that generated inputs and checked-in ACS bytecode agree before packaging.
The 25 September package/source hash comparison covered 30,845 eligible source
files and 30,814 packaged runtime files. Every included source file matched
byte-for-byte except MAPINFO.txt, where packaging adds model precache lists.
The 31 omitted source files are all TEXTURES definition modules; their
definitions are already expanded in the checked-in TEXTURES.txt. UTNTBLD and
LANGUAGE.zzbuild are the two package-only metadata files. All map WADs, ACS
bytecode, ZScript, artwork and other included assets matched their editable
production sources. These known transformations remain exceptions to a
byte-identical direct ZIP; they do not hide map edits.
