# UTNT brightmaps

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

## Native-pixel additions (14 September 2026)

The approved four-pixel Nami Dark Imp example is now extended to the reviewed
custom enemies, missing compatible enemy phases, items and high/medium-priority
map surfaces. The original sprite/texture art, actor states, existing BRIGHT
flags, lights and imported masks are preserved. No image resampling is used.

`gldefs/GLDEFS.brightmaps-custom` adds 510 bindings (496 sprite, five flat and
nine texture bindings), backed by 478 new grayscale mask PNGs. Identical masks
share files, including matching images in the existing banks. Sixteen reference
bindings in the candidate families remain their sole owners; 332 examined
frames/states have no additional emissive pixels.

| Group | Selective details |
| --- | --- |
| NamiDarkImp | Yellow eyes in visible rotations and blue attack energy; A1 retains exactly the approved four mask pixels. |
| Arachnophyte | Eyes, thrusters and attack cores; G–J death explosions include hot cores and progressively cooling rings. |
| SoulHarvester / HarvesterGhost | Eyes and yellow attack fire; inherited sprites share the same masks. |
| HellWarrior | Shield eye and yellow flame hand, including its cooling death phases. |
| TorturedSoul / PlasmaElemental | Green eye, energy and applicable glowing mouth pixels. |
| RailArachnotron / SourceGuardians | Eyes and visible charged details, without illuminating armor or machinery. |
| Shadow / HellsFury / Devil | Eyes and applicable red magical energy; no glowing blood or dead bodies. |
| TNTSpider / TNTMiniSpider | Restrained green markings and K/M fire bursts; separate MNTS gib frames remain dark. |
| EnhancedCacodemon | Missing B–F eye/mouth/attack views; compatible A views retain the reference masks. |
| RocketGuy / HellGuard | Rechecked: all five/eight muzzle-flash views already have reference masks. Ordinary clothing, armor and corpses do not need extra masks. |
| SourceLifeSeed / PortalCoreHeart | Red seed interior and heart energy; sprite frames and the active heart voxel representation are covered. |

High-priority surfaces: IKLITF01, IKLITF07, TLITE6_1, TLITE6_5, QRUNT62,
QRUNT63 and TELETOP. The two rune textures reuse their exact existing ritual
masks through native GLDEFS; the redundant material-shader bindings are removed. Medium-priority COMPBLUE/COMPRED use weaker emission than
lamps. COMPBLUE's actual expanded XA40TEX/XB40TEX variants are included.
SW2NEW1 lights only the skull eyes; SW2NEW3 covers its red and blue indicators.
The corresponding SW1NEW1/SW1NEW3 off states stay unlit. CRT materials and
existing ritual effects retain their owners. Decorations and the separately
listed optional QCOMP/QTECH surfaces were outside the approved rollout.

### Preserving the custom spider sprite sequence

UZDoom's legacy Minotaur compatibility path renames MNTR F–K to U–Z when no
Z resource exists. For this custom spider sequence that hid the authored K
explosion and replaced its U view. A generated, fully transparent, unused
1×1 `sprites/monsters/MNTRZ0.png` marker prevents that automatic rename.
The original sprites, their offsets and actor state definitions remain intact;
the K explosion and its brightmap can now use their intended names.

### Portal heart voxel material

UZDoom normally creates an anonymous 16×16 palette skin for native voxels, which
cannot receive a named GLDEFS brightmap. `modeldef/MODELDEF.brightmaps-custom`
therefore binds the **same four UVPHRT*.kvx files** to a named skin generated from
the active PLAYPAL. Native scale, pivot, angle and uniform lighting are retained;
no geometry is converted, duplicated or recolored. Only its red palette cells
receive a mask. VOXELDEF remains available to the software renderer. Hardware
rendering uses the explicit KVX model binding (controlled by model rendering,
rather than the native voxel toggle); sprite brightmaps cover the sprite fallback.

An isolated native-engine comparison found **zero changed screen pixels** between
the previous voxel rendering and this binding with a black brightmap. Enabling
the mask changed 132 pixels within the heart region in that fixed view.

### Explosive barrel lighting (16 September 2026)

The barrel's `BARREL` dynamic light uses `DontLightSelf 1`: it still lights its
surroundings, but not the barrel owning it. Lights from other actors remain valid.
Both original idle KVXs (`CVBAR1A/B`) use a named PLAYPAL skin with a selective
brightmap for the yellow-green nukage ramp (indices 112–123). The darker green
indices 124–127 also occur on the metal and remain unlit, as do all metal bands.
The two idle models retain the original scale, pivot and orientation (native
VOXELDEF 270° plus its internal 90° equals MODELDEF 0°). Explosion states, models,
lights and radius damage are unchanged. Existing reference sprite masks remain
available for the sprite fallback.

An isolated UZDoom 5.0.1 OpenGL comparison found zero changed pixels between
the original voxel and the new binding with emission disabled. Enabling the
brightmap changed 1,150 pixels, all within the nukage at the top, and none on
the metal. Dynamic-light on/off comparisons still illuminated the floor. The
existing actor-default, save/load and barrel radius-damage checks passed
(11 assertions).

### Generation and checks

- `python -B tools/build_custom_brightmaps.py` regenerates only these outputs.
  Rules follow inspected source colors and bounded emissive regions. The recorded
  palette, source and output hashes expose subsequent artwork changes.
- `python -B tools/check_custom_brightmaps.py` reproduces outputs and checks
  source dimensions, transparent borders, grayscale masks, include ownership,
  reference/auto/material conflicts, off states, requested fire phases and the
  exact approved Nami mask.
- `python -B tools/check_brightmaps.py` independently verifies the untouched
  four-release reference import.
- `python -B tools/test_custom_brightmaps.py --mode on` and `--mode off` render
  thirteen native-engine galleries of original sprite frames, explosions and
  surfaces. Test-only actors freeze the images for deterministic comparisons;
  their fixtures and black overrides never ship.

The regular `tools/build_utnt.py` build regenerates the additions after voxel and
material generation. Source-pixel contact sheets are local in
`tutnt/.codex/work/brightmap-rollout/`; native screenshots and reports are in
`.codex/validation/brightmap-rollout/`, and logs in `.codex/logs/brightmap-rollout/`.
The sprite sheets review every candidate image, while native galleries validate
representative rendering; they do not claim every angle in every campaign room.

Final UZDoom 5.0.1 / Vulkan validation used shared build `0acf5ccce3a5`:
all 13 galleries passed at 960×540, with 37 emissive sample regions responding
to the masks and both off-switch controls remaining pixel-identical. Every
expected test actor was present; compilation and runtime logs were clean.
The final fixed-camera heart comparison again found zero pixel differences
between native voxel rendering and the named material with a black mask;
enabling its brightmap changed 100 pixels. All 482 generated package outputs
match the manifest. The reference import and definition-table checks passed.
