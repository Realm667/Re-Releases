# UTNT definition layout

The nine engine entrypoints stay in `tutnt/`. Modules live in these directories:

| Root entrypoint | Module directory | Loading |
| --- | --- | --- |
| GLDEFS.txt | gldefs/ | Native #include |
| TEXTURES.txt | textures/definitions/ | Generated table; TEXTURES.base defines source include order |
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
remain relative to the package root. TEXTURES.base retains the original texture definitions and source include order;
build_definition_tables.py expands it into the checked-in TEXTURES.txt because
UDB does not implement TEXTURES includes. Other native formats retain their includes.
Definition files under textures/definitions are source modules. UZDoom also scans this directory as a texture-image
namespace. To avoid an invalid-image warning, the packager checks the already generated
TEXTURES.txt against its modules and omits textures/definitions/ from the PK3. All image assets
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

## Runtime-only textures in UDB (15 September 2026)

The table generator appends `TEXTURES.environment-generated` (EV wet-surface aliases)
and `TEXTURES.sky-edges` (SG terrain geometry materials) after authored definitions,
with `//$GZDB_SKIP` immediately before those two modules. UZDoom sees a comment;
UDB stops there, avoiding thousands of redundant large composite previews.
Both families are generated runtime bindings, not manually painted map textures.
Source modules remain intact; regression tests protect ordering and preservation.
The generated root table exposes the same authored definitions to UDB for both
source-directory and PK3 resources.

Invalid seven-character effect sprite names become `USRIA0` (formerly USRIPA0)
and `URDSA0` (formerly URDSTA0), consistently in definitions and consumers.
The installed r4327 parser accepts the isolated follow-up's table without errors:
1,279 authored textures, zero EV aliases, approximately 0.6 seconds. The old table
failed after 4,192 textures including 3,179 EV aliases. This verifies parsing and
namespace reduction, not the complete editor's map-opening wall-clock time.

## UDB generated class parsing (16 September 2026)

The installed UDB r4327 creates a fresh `ZScriptTokenizer` for every actor during
`ZScriptParser.Finalize`. The tokenizer constructor scans its entire input stream
to rebuild line positions. The former 11,432-class, 1.54 MB sky-edge source thus
caused repeated complete scans even when opening an unrelated campaign map.

`build_sky_edges.actor_sources` now generates source files of at most 128 classes
under `zscript/sky-edges-generated/`, included by the original entrypoint. All
class declarations, order, defaults, states and MODELDEF bindings are preserved.
The generated-file inventory tracks the chunks and removes obsolete chunks when
regenerating. Splitting is preferable to hiding these ZScript classes: hiding
also leaves MODELDEF references unresolved and floods the editor with warnings.

An isolated copy of installed UDB r4327 loaded a copy of TNT03A2 with the live
source directory, DOOM2.WAD and gzdoom.pk3. Detailed timing reduced the ZScript
phase from 350.234 to 22.543 seconds. A final run using only timestamps on normal
log messages completed from `Opening map` to `Map loading done` in 13.828 seconds.
These are local measurements, not a promise of an identical cold-load time on
another machine. The earlier detailed baseline reached the editing mode after
about six minutes but hit UDB's `-delaywindow` AutoSaver initialization bug;
the final successful run uses the normal startup sequence and an explicit ACS
configuration. The baseline is therefore evidence for the parser phase, not a
successful full-map-open benchmark. Existing UDBScript/Esprima and KVX preview
warnings remain separate; the former appeared after map loading completed.

The local UDB Common.cfg excludes `.codex` from the resource index for all 51
installed configurations. That exclusion alone did not solve the actor parser
stall. It is a local installation setting and may need restoring after updates.
Do not copy `.codex` into editor resources or release packages. The built PK3
remains suitable as an editor resource, and source-folder loading now also
benefits from the class-file split.

Validation: ordered class/include round-trip and chunk-bound tests, definition
and localization gates, full editor load, and the normal game-package engine
check. Local phase logs and the original-version source excerpts are retained
under `tutnt/.codex/work/udb-open-profile/`.

## TNT03A2 editor resource errors (16 September 2026)

UDB r4327 silently skips TEXTURES #include directives. Source-folder loading
therefore lacked UCAVROCK/UCAVFALL and other modular composites even though the
packaged game resolved them. TEXTURES.base now owns the source include order,
and build_definition_tables.py emits a checked-in, fully expanded TEXTURES.txt.
All original nonblank runtime definition lines and their order are preserved;
EV/SG aliases remain after the editor stop marker. Packaging validates and keeps
the final table byte-for-byte. Edit the modules and regenerate; --check rejects
stale tables. The existing material bindings and shaders are unchanged.

TNT03A2 explicitly declares SKY1, matching its previous Doom default. Placed
skybox viewpoints still control the actual map sky. This supplies the fallback
required by UDB without changing the cavern's sky-room construction.

The local UDBScript ScanComments exception came from System.Memory.dll existing
both beside Builder.exe and directly in Plugins/. The plugin loader loaded the
extra copy as a plugin, producing two assembly loads and incompatible type
identities despite identical version numbers and bytes. The duplicate was moved
to tutnt/.codex/backups/udb-errors-tnt03a2/. The root DLL remains installed;
a complete editor restart is required for the repair to take effect.

Remaining compatibility notices are intentional: r4327 rejects the four native
KVX MODELDEF heart frames supported by UZDoom, and warns about the twelve native
Doom locks whose map colors are deliberately overridden. Their game definitions
are retained; clearing native locks or removing the heart material would change
runtime behavior merely to silence editor warnings.

Texture-alignment startup counters (AREAALIGN and shared-surface constraints)
are now silent during ordinary play. `netevent areaalign` explicitly reports
AREAALIGN_STATUS and AREAALIGN_SHARED_CONSTRAINTS; the alignment verifier reads
that requested status. Actual stale/rejected binding warnings remain visible.

Validation: thirteen definition tests, a real UDB load of both UCAV images and all
102 cavern models, parsing all 21 UDBScript examples, and a clean diagnostic editor
shutdown. A real TNT03A2 engine run confirms silent startup and an explicit status
of 2786 applied / 0 rejected / 2786 expected. Test evidence is local under
.codex/work/udb-errors-tnt03a2 and .codex/validation/udb-console-errors.
