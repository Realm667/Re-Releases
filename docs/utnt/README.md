# UTNT documentation

Current feature and maintenance documentation is collected here. Commands and inline source paths are relative to the repository root unless explicitly stated otherwise.

## Build and checks

Run `tutnt_build.bat` from the repository root. Local configuration is in the ignored `tools/utnt-env.cmd` (`UTNT_PYTHON`, `UTNT_ACC`, `UTNT_ENGINE`, `UTNT_IWAD`). Keep the shared `tutnt.pk3` at the root; temporary packages belong under `tutnt/.codex/builds/`. Run `python -B tools/check_work_layout.py` before finishing a task.

## Features and maintenance

- [UTNT_ABILITIES.md](UTNT_ABILITIES.md)
- [UTNT_ALTERNATE_SKY.md](UTNT_ALTERNATE_SKY.md)
- [UTNT_AREA_TEXTURES.md](UTNT_AREA_TEXTURES.md)
- [UTNT_ASH_SKY.md](UTNT_ASH_SKY.md)
- [UTNT_BOSS_HUD.md](UTNT_BOSS_HUD.md)
- [UTNT_CALDERA.md](UTNT_CALDERA.md)
- [UTNT_CREDITS.md](UTNT_CREDITS.md)
- [UTNT_CURSED_SKY.md](UTNT_CURSED_SKY.md)
- [UTNT_ENDMAP_SKY.md](UTNT_ENDMAP_SKY.md)
- [UTNT_EXPLORATION_UI.md](UTNT_EXPLORATION_UI.md)
- [UTNT_FIRE_EFFECTS.md](UTNT_FIRE_EFFECTS.md)
- [UTNT_HEAT_FIX.md](UTNT_HEAT_FIX.md)
- [UTNT_HUD_STACKING.md](UTNT_HUD_STACKING.md)
- [UTNT_INDUSTRIAL_FX.md](UTNT_INDUSTRIAL_FX.md)
- [UTNT_INTERMISSION.md](UTNT_INTERMISSION.md)
- [UTNT_INTRO_CHAPTER.md](UTNT_INTRO_CHAPTER.md)
- [UTNT_LAVA.md](UTNT_LAVA.md)
- [UTNT_LAVA_LIPS.md](UTNT_LAVA_LIPS.md)
- [UTNT_LIQUIDS.md](UTNT_LIQUIDS.md)
- [UTNT_NOTICES.md](UTNT_NOTICES.md)
- [UTNT_OBJECTIVES.md](UTNT_OBJECTIVES.md)
- [UTNT_PALETTE.md](UTNT_PALETTE.md)
- [UTNT_PORTALS.md](UTNT_PORTALS.md)
- [UTNT_RECOIL.md](UTNT_RECOIL.md)
- [UTNT_RIFT_SKY.md](UTNT_RIFT_SKY.md)
- [UTNT_RITUALS.md](UTNT_RITUALS.md)
- [UTNT_ROCK_EXPANSION.md](UTNT_ROCK_EXPANSION.md)
- [UTNT_ROCK_ROLLOUT.md](UTNT_ROCK_ROLLOUT.md)
- [UTNT_SOURCE.md](UTNT_SOURCE.md)
- [UTNT_STATUSBAR.md](UTNT_STATUSBAR.md)
- [UTNT_STEAM.md](UTNT_STEAM.md)
- [UTNT_STORM.md](UTNT_STORM.md)
- [UTNT_THUNDER.md](UTNT_THUNDER.md)
- [UTNT_TNT01_LANDSCAPE.md](UTNT_TNT01_LANDSCAPE.md)
- [UTNT_TNTLE_SKY.md](UTNT_TNTLE_SKY.md)
- [UTNT_TNTLE_SKY_FIXES.md](UTNT_TNTLE_SKY_FIXES.md)
- [UTNT_UI_REFINEMENT.md](UTNT_UI_REFINEMENT.md)
- [UTNT_USABILITY.md](UTNT_USABILITY.md)
- [UTNT_WAR_SKY.md](UTNT_WAR_SKY.md)
- [UTNT_WEATHER.md](UTNT_WEATHER.md)
- [UTNT_WEATHER_VISOR.md](UTNT_WEATHER_VISOR.md)

## Historical reports and concepts

The editable local archive is `tutnt/.codex/notes/README.md`. These fixed Git-history links remain available on GitHub:

- [TNT04B_SKY_CONCEPT.md](https://github.com/Realm667/Re-Releases/blob/aea25d019f137f47a7772a895d9f4733f62a6898/TNT04B_SKY_CONCEPT.md) — Approved initial concept; implementation: UTNT_ASH_SKY.md.
- [UTNT_MODERNIZATION.md](https://github.com/Realm667/Re-Releases/blob/aea25d019f137f47a7772a895d9f4733f62a6898/UTNT_MODERNIZATION.md) — Historical first modernization report.
- [UTNT_SECOND_PASS.md](https://github.com/Realm667/Re-Releases/blob/aea25d019f137f47a7772a895d9f4733f62a6898/UTNT_SECOND_PASS.md) — Dated second-pass implementation and acceptance report.
- [UTNT_PACKAGE_AUDIT.md](https://github.com/Realm667/Re-Releases/blob/aea25d019f137f47a7772a895d9f4733f62a6898/UTNT_PACKAGE_AUDIT.md) — Historical package-loss investigation; permanent rules are in AGENTS.md.
- [UTNT_TNT01_ORGANIC.md](https://github.com/Realm667/Re-Releases/blob/aea25d019f137f47a7772a895d9f4733f62a6898/UTNT_TNT01_ORGANIC.md) — Superseded first terrain revision; current: UTNT_TNT01_LANDSCAPE.md.

Screenshots formerly tracked in `tools/validation/` link to their preserved Git revisions. Local originals remain under `tutnt/.codex/validation/`. Runtime source files and build commands retain their existing locations.
