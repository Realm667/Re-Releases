# UTNT reference brightmaps

Implemented 13 September 2026. The following immutable release directories are
the artwork reference (their local names use an underscore after `released`):

- `tnte1.released_v20-20231224`
- `tnte2.released_v20-20240115`
- `tnte3.released_v20-20240129`
- `tntle.released_v20-20240306`

## Integration

`gldefs/GLDEFS.brightmaps` is included once by `tutnt/GLDEFS.txt`.
The import contains 1,506 explicit bindings: 1,336 sprite, 130 wall texture and
40 flat entries. Of these, 403 cover compatible custom enemy/attack sprites and
five cover the QMTLSW1–QMTLSW5 switch textures. The remaining 1,098 entries apply
to unreplaced Doom II enemies and surfaces. This includes 368 original mapless
`disablefullbright` entries; these are fullbright-state controls, not new images.

The 1,053 new PNGs under `materials/brightmaps/reference/` are byte-for-byte
release assets. Identical decoded images share one file, also reusing existing
UTNT masks where possible. The Arch-vile backslash frame uses an explicit
`sprite-vile/` image subdirectory; these are not automatic bindings.
The manifest records every binding, source file, SHA-256, retained mask and
exclusion: [brightmap-reference.json](../../tools/brightmap-reference.json).

The 106 existing applicable auto masks were already identical to the references
and remain unchanged. Six redundant Q2COMP8–Q2COMP13 auto masks were removed;
the existing dedicated CRT material brightmaps remain the sole owners. The CRT
shader, normal/parallax materials, textures and monster states are unchanged.

## Relevance and exclusions

All 650 unique release auto-mask names were examined. Repeated names across the
four releases have identical mask bytes. Besides the retained/imported entries,
130 auto masks were excluded: 93 incompatible dimensions, 12 missing names or
different rotation/frame layouts, and 25 incompatible enemy graphics.

In particular, UTNT's Hell Warrior and Blood Demon use different artwork.
Several Enhanced Cacodemon, rifle/plasma zombie and Soul Harvester attack frames
also differ. Their masks were not stretched or blindly assigned by name.
Dark Imp/Vile, three compatible Enhanced Cacodemon views and Afrit fire artwork
retain matching silhouettes; their recolored versions were visually checked.
The other imported custom sprites have identical decoded reference pixels.

Of the 1,328 unique vanilla declarations, 173 weapon/item/decorative entries are
outside this task, 18 refer to replaced UTNT resources, and 39 are absent from
the Doom II IWAD (including other-game textures). Original `iwad` and
`disablefullbright` flags are preserved. Custom bindings use `thiswad` so later
external sprite replacements do not inherit masks for the original artwork.
The original releases also contain unused mask images and commented-out
bindings; these are not treated as active reference features.

The native loading and flag semantics follow the
[GLDEFS documentation](https://zdoom.org/w/index.php?title=GLDEFS).

## Validation and maintenance

Run `python -B tools/check_brightmaps.py` for source hashes, original target
artwork, active include traversal, duplicate target ownership, CRT/auto overlap,
decoded-image deduplication and orphaned images. Run
`python -B tools/build_definition_tables.py --check` for definition layout.
The checker is read-only; intentional future artwork changes require a fresh
alignment review and a corresponding manifest update.

Local image comparisons and working scripts are under
`tutnt/.codex/work/brightmap-reference-audit/`; test packages, engine logs and
validation reports use the shared `.codex` artifact directories.

Validation completed with UZDoom 5.0.1, test build `41f72739c824`: ACS,
localization, fonts and engine loading passed. A dark-room comparison with
imported masks enabled versus black test overrides confirmed emissive enemy
details and surfaces while the CRT material remained unchanged. This verifies
representative rendering, not every sprite angle in every campaign room.
