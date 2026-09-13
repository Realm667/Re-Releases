# UTNT voxel pickups and decorations

Updated: 14 September 2026.

Forty-one selected actor types use sixty-seven native KVX models, including all original
animation frames. The mapping changes world rendering only: actor classes,
collision, pickup amounts, weapon behavior, map placements and existing fire/light
systems remain in place. Weapon HUD sprites are not voxelized.

## Sources and palette

The imported models are by **Cheello**, Daniel Peterson, from Voxel Doom 2.4
(April 2024). The spelling is verified against its supplied readme. The source
permission allows reuse with credit; a copy is kept in
`tools/artwork/voxels/CHEELLO-README.txt`, and the shipped package includes
`voxels/CREDITS.txt`. No Voxel Doom actor replacements or monster systems are
imported. Cheello has a dedicated, localized voxel-graphics credit in the ENDMAP
Remaster chapter, before the director and the personal dedications.

Cheello's embedded palettes use a reordered index table. The importer first maps
every voxel in every MIP level back to the original Doom palette index, using
exact six-bit color matches where available. Every VOXELDEF mapping then sets
`OverridePalette`, which discards the embedded KVX palette at runtime and reads
UTNT's active `PLAYPAL.pal`. There is no additional runtime palette replacement.

The UTNT-specific models use the original indexed **low-resolution** `.lmp`
sprites. The original Minigun source was restored as an artwork input from
`75f81f1fc^:tutnt/sprites/MNGNA0.lmp` and is kept at
`tools/artwork/voxels/sources/MNGNA0.lmp`. Its Hires replacement is not used to
build geometry or textures. The manifest records exact source hashes.

## Motion and scope

`Spin = 0` means stationary; `Spin = 20` is a slow 18-second revolution;
`Spin = 70` gives skull keys a roughly 5.14-second revolution. The same setting
applies to placed and dropped pickups. No actor tick or network state is needed
for native renderer rotation.

| Actor | Origin | Rotation |
| --- | --- | --- |
| Clip | Cheello | 0 deg/s |
| Backpack | Cheello | 0 deg/s |
| ClipBox | Cheello | 0 deg/s |
| RocketBox | Cheello | 0 deg/s |
| Cell | Cheello | 0 deg/s |
| CellPack | Cheello | 0 deg/s |
| RocketAmmo | Cheello | 0 deg/s |
| FloatingSkull | Cheello | 0 deg/s |
| BlueArmor | Cheello | 20 deg/s |
| GreenArmor | Cheello | 20 deg/s |
| Medikit | Cheello | 0 deg/s |
| Stimpack | Cheello | 0 deg/s |
| Candelabra | Cheello | 0 deg/s |
| Candlestick | Cheello | 0 deg/s |
| Berserk | Cheello | 0 deg/s |
| Infrared | Cheello | 0 deg/s |
| RadSuit | Cheello | 0 deg/s |
| Allmap | Cheello | 0 deg/s |
| Shell | Cheello | 0 deg/s |
| BlueSkull | Cheello | 70 deg/s |
| YellowSkull | Cheello | 70 deg/s |
| RedSkull | Cheello | 70 deg/s |
| ArmorBonus | Cheello | 20 deg/s |
| HealthBonus | Cheello | 20 deg/s |
| UTNTBFG9000 | Cheello | 20 deg/s |
| UTNTChaingun | Cheello | 20 deg/s |
| UTNTChainsaw | Cheello | 20 deg/s |
| UTNTPistol | Cheello | 20 deg/s |
| UTNTPlasmaRifle | Cheello | 20 deg/s |
| UTNTRocketLauncher | Cheello | 20 deg/s |
| UTNTShotgun | Cheello | 20 deg/s |
| UTNTSuperShotgun | Cheello | 20 deg/s |
| ExplosiveBarrel | Cheello | 0 deg/s |
| Gas | UTNT lowres | 0 deg/s |
| BigGas | UTNT lowres | 0 deg/s |
| UTNTFlamer | UTNT lowres | 20 deg/s |
| UTNTPyroCannon | UTNT lowres | 20 deg/s |
| UTNTMinigun | UTNT lowres | 0 deg/s |
| PortalCoreHeart | UTNT lowres | 0 deg/s |
| UTNT_Barrel | UTNT lowres | 0 deg/s |
| CandelabraNew | UTNT lowres | 0 deg/s |

The duplicate SamNMax_Zeitung request is treated once. All eight Sam & Max props
(Ants, Box, Letters, Sandwich, Stuhl, Telef, Zeitung and TV) were explicitly
excluded after visual review; they retain their existing sprites and have no
voxel bindings or generated assets. The earlier keycard experiment also remains
separate; this integration imports only the requested skull keys from Cheello.

The explosive barrel includes both idle frames (BAR1 A/B) and all five explosion
frames (BEXP A–E), with native scale, no rotation and the source angle offset.
Its original actor, health and radius damage remain unchanged.

## World scale

One native KVX cell is one map unit on every axis. VOXELDEF uses the engine's
unit-scale default, and all forty-one selected actors use `Scale = (1,1)`. No model
is normalized to a common display size. Doom's normal pixel aspect applies to
the scene and does not change these map-unit measurements.

The Stimpack is **14 × 10 × 15** map units (width × depth × height), matching
its original **14 × 15** sprite-pixel width and height. The Medikit is
**28 × 14 × 12** map units: twice the Stimpack's width, with a flatter body;
its original 28 × 19 sprite also depicts the top surface in perspective.
The custom Minigun remains 52 source pixels / map units wide.

The earlier review gallery enlarged small objects independently for inspection
(the Stimpack by 3.6667), which misrepresented their relative sizes. That fixture
scaling has been removed. Current gallery screenshots use untouched actor scales
and a shared camera, with explicit unit-scale and save/load assertions.

## Custom geometry

- **Gas / BigGas:** revolved metal canisters with rounded caps, body rings and
  colored lower bands; BigGas keeps two distinct cylinders.
- **Flamethrower / Pyrocannon:** fuel cylinders, barrel assemblies, grips, rails
  and connecting hoses use different thicknesses. Both rotate slowly.
- **Minigun:** original lowres receiver, stock, ammunition belt and a rounded
  barrel assembly with axial muzzle openings; stationary as requested.
- **PortalCoreHeart:** shaped metallic core with tapered depth, original animated
  surface details and small detached sparks. The flat red sprite outline is not
  extruded into a solid red wall; the existing actor light and float-bob remain.
- **Burning barrel:** cylindrical body, reinforced rings and open-looking rim;
  the existing UTNT fire emitter remains active at its original world scale.
- **CandelabraNew:** separate candles, branching metal supports, narrow stem and
  a wider solid base, retaining the actor's existing light.

Only geometry needed for each object is generated; output remains at the source
pixel density. Source-projecting shapes retain their authored surface colors.

## Definitions and tools

`VOXELDEF.txt` is an additional native engine entrypoint in `tutnt/`. Unlike the
nine older definition formats, this parser does not support module includes;
`tools/build_voxels.py` generates its complete explicit mapping from the selected
source list. Models live only in `tutnt/voxels/`. The regular UTNT build invokes
the voxel generator/checker before taking its immutable package snapshot.

- `python -B tools/build_voxels.py --source <unpacked Voxel Doom> --iwad <DOOM2.WAD>`
  imports the selected resources and normalizes all palette indices.
- `python -B tools/build_voxels.py` rebuilds custom models using committed sources.
- `python -B tools/build_voxels.py --check` validates native KVX tables, slabs,
  MIPs, hashes, deterministic custom output and mappings.
- `python -B tools/test_voxels.py --mod tutnt.pk3` opens the isolated VXLAB fixture
  and exercises all forty-one actual actors, multiple viewing directions and save/load.
  Screenshots and logs stay in `.codex`. The fixture preserves every actor at
  `Scale = (1,1)` and asserts that scale before and after save/load.

## Validation

Validated with UZDoom 5.0.1. The final forty-actor gallery passed 93 runtime
assertions for native scale, three viewing directions and save/load. The English and German
ENDMAP credit runs passed 145 and 147 assertions respectively; all four language
catalogues and original-font coverage passed. The import matches the supplied
Voxel Doom sources, and a fresh Windows checkout reproduces all sixty-seven models.

The added explosive barrel passed eight further assertions from the final package,
covering native scale, actor defaults, save/load, its death transition and original
radius damage. Both idle frames and all five explosion models are included.

The shared integration package passed its engine build check. Package validation
confirms exact model hashes, active PLAYPAL bindings, all four credit translations
and absence of Sam & Max voxel resources. A further gallery run from the actual
package covers armor, weapons and all eight custom actors. Local proof lives under
`tutnt/.codex/validation/` and `tutnt/.codex/work/voxel-integration/`.
