# UTNT definition layout

The nine engine entrypoints stay in `tutnt/`. Modules live in these directories:

| Root entrypoint | Module directory | Loading |
| --- | --- | --- |
| GLDEFS.txt | gldefs/ | Native #include |
| TEXTURES.txt | textures/definitions/ | Native #include |
| CVARINFO.txt | cvarinfo/ | Generated table |
| KEYCONF.txt | keyconf/ | Generated table |
| LANGUAGE.txt | language/ | Generated table |
| MAPINFO.txt | mapinfo/ | Native include |
| MENUDEF.txt | menudef/ | Generated table |
| MODELDEF.txt | modeldef/ | Native #include |
| SNDINFO.txt | sndinfo/ | Native $include |

Paths are relative to `tutnt/`. The original root payloads of CVARINFO and
MENUDEF are now `cvarinfo/CVARINFO.base` and `menudef/MENUDEF.base`.

UZDoom's CVARINFO, KEYCONF, LANGUAGE and MENUDEF parsers do not implement native
includes. Their checked-in root files therefore contain generated text, with
`// @include` comments identifying each source module. Edit the modules, then run:

```text
python -B tools/build_definition_tables.py
python -B tools/build_definition_tables.py --check
```

`tools/definition-layout.json` defines their explicit load order. Add new modules
to this manifest. Native formats use explicit includes in their root entrypoints;
add new modules there. Root-relative includes inside GLDEFS modules retain their
root-relative paths. SNDINFO includes are relative to the including file.

The migration preserves the previous alphabetic root-lump order and existing
nested include order, including repeated includes that existed before. This
preserves override precedence. Shader, texture-image, model and sound asset paths
remain relative to the package root. Definition files under textures/definitions
are explicitly included. UZDoom also scans this directory as a texture-image
namespace. To avoid an invalid-image warning, the packager expands these includes
into TEXTURES.txt and omits textures/definitions/ from the PK3. All image assets
remain unchanged. Direct source-directory loading works but produces this engine
warning; use the built PK3 for a warning-free definition load.

The regular build refreshes generated tables before taking its immutable source
snapshot; `--check-only` rejects stale tables. The definition checker also rejects
missing/unlisted modules, duplicate manifest entries, cyclic/missing native
includes and new definition fragments in the root. Generated tables are kept in
Git so loading the source directory directly still works. Localization validation
reads the authoritative language modules, while package validation reads the
assembled LANGUAGE.txt. No translation review is needed for a path-only move.

Current generators, regression tools and documentation use the new paths.
Historical migration reports and immutable Git snapshots retain their old paths;
consult the local migration map before running an old temporary script.

Definition scans filter files explicitly: on Windows, GLDEFS* and LANGUAGE*
also match the new lowercase directories. Generators and localization overlays
must not try to read or copy those directory entries as files.
