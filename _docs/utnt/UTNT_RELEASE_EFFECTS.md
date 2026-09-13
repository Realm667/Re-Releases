# Release enemy deaths and movement tilt

Implemented 14 September 2026. Brightmaps are documented separately in [UTNT_BRIGHTMAPS.md](UTNT_BRIGHTMAPS.md).

## Reference audit

The reference folders are `tnte1.released_v20-20231224`, `tnte2.released_v20-20240115`, `tnte3.released_v20-20240129` and `tntle.released_v20-20240306`. Their `sprites/altdeaths` sets contain 141 identical assets. The first three use `actors/nashdoom.txt`; the latest uses `zscript/TNTLE_XGore.zc`. UTNT previously contained the gore system but lacked these alternate enemy death states.

No movement-tilt implementation or TILT shader was found in these four references. Following clarification that TILT means camera inclination during movement, the remaster adds its own optional local effect.

## Alternate deaths

[alternate-deaths.txt](../../tutnt/actors/alternate-deaths.txt) adds the applicable variants for ZombieMan, ShotgunGuy, DoomImp, Demon, Spectre, HellKnight, BaronOfHell, Arachnotron and Fatso, including their eight existing stealth counterparts: 17 replacement classes and 36 alternate state sequences. Ordinary deaths retain the reference's 50% original / 50% alternate selection, distributed across the available variants. Demon/Spectre and Baron/Knight families also gain the reference's alternate extreme death.

The replacements inherit the corresponding UTNT combat classes, preserving health, attacks, drops, obituaries and stealth behavior. Custom descendants keep their own artwork and classes. A dedicated synchronized random stream selects animations. Raise restores the original sprite prefix before entering inherited resurrection states, including after save/load. Baron, Arachnotron and Fatso terminal states preserve boss-death callbacks. The import removes dangling reference Death4 jumps and substitutes the existing scream for an undefined Arachnotron sound alias.

The 126 referenced frames share 125 image files: 116 death images and nine demon-arm images. Identical ShotgunGuy frames L/M share one image. They retain original bytes and offsets, use free UD-prefixed sprite names, and are shared by ordinary/stealth and Demon/Spectre variants. Flying arms reuse the bounded local gore lifecycle and transfer render style/translation. Unused reference frames and a second gore implementation are excluded. [The manifest](../../tools/alternate-deaths.json) records source hashes and frame mappings. The source MIT notice is preserved in the actor file; the source credits the demon-arm sprites to NeoWorm.

## Movement tilt

[UTNT_ViewTilt.zc](../../tutnt/zscript/UTNT_ViewTilt.zc) and [view-tilt.fp](../../tutnt/shaders/view-tilt.fp) smoothly rotate the rendered scene according to sideways velocity. The default strength is 65%, with a maximum two-degree tilt at 100%. A small aspect-correct crop prevents exposed image corners. The HUD and menus remain fixed; player angles, aiming and movement are unchanged.

Remaster Options > Comfort provides an on/off switch and a 0-100% strength slider, translated into English, German, Spanish and French. The controls are local user CVARs `UTNT_viewtilt` (default true) and `UTNT_viewtiltstrength` (default 65). Reduced effects, pauses, death, cutscene flags and non-player cameras disable it. Camera/world changes and large position/time discontinuities reset smoothing.

## Validation

- `python -B tools/check_release_effects.py`: asset hashes, unique sprite names, live state references and optional comparison with all four local releases.
- `python -B tools/test_release_effects.py --renderer 1` and `--renderer 0`: UZDoom 5.0.1 compilation and 242 assertions per renderer. Covers replacement identity and inherited properties, all 36 alternate sequences, nonsolid settled corpses, kill counts, save/load, resurrection and original sprite restoration, custom-monster exclusion, tilt direction/smoothing, off/zero strength, stillness and reduced effects.
- The runtime fixture supplies a room with all variants and captures the scene with tilt off, right, left and the localized comfort menu. Screenshots confirm inclined scenery and fixed HUD/menu composition. Results remain local under `tutnt/.codex/validation/release-effects/`.
- Definition generation, localization and font coverage checks are required. Runtime tests exercise deterministic local single-player behavior; they do not constitute a new multiplayer campaign playthrough.
