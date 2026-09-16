# UTNT secondary fire

Four weapons gain alternate attacks through the engine's existing **Secondary Fire** (`+altattack`) control. Existing bindings are preserved. The remaining eight weapons retain their primary attack only. Both modes share the existing ammunition pool; the HUD continues to show that pool once.

| Weapon | Secondary behavior | Cost |
| --- | --- | --- |
| Super Shotgun | Ten pellets from one barrel. The second barrel remains available after releasing fire, changing weapons, saving or loading. Firing primary with one barrel remaining fires that barrel; both empty barrels then use the existing reload animation. | One shell per barrel |
| Rocket launcher | Ballistic, bouncing grenade with enemy-contact detonation and an 88-tic (approximately 2.5-second) fuse. Explosion can hurt the shooter. | One rocket |
| Plasma rifle | Five times the projectile damage, five times the sustained primary firing intervals, 150% sprite and collision dimensions, and gentle homing in a narrow forward cone. | Five cells |
| BFG9000 | One homing projectile visits up to twelve distinct enemies in sequence, with no BFG spray and no repeat hit on the same actor. | Forty cells |

## Balance and targeting

Heavy plasma preserves the primary weapon's sustained three-shot timing pattern, scaling intervals from 3/3/1 to 15/15/5 simulation tics. Projectile base damage increases from 5 to 25 with the original damage randomization; speed stays at 25. Visual scale is 0.675 versus 0.45, radius 19.5 versus 13, and height 12 versus 8. Homing searches within 1024 map units and a 20-degree half-angle, then turns at most two degrees every two tics. The aim assistance stops after five seconds.

The BFG chain deals 260 base damage per visited target: 3120 for a complete twelve-target chain, close to the original ball plus fully connected spray's theoretical mean of 3150. This comparison assumes all original spray rays hit; actual primary BFG damage varies with distance, aim and target distribution. The chain's initial search is within 1024 units / 35 degrees; subsequent hops can turn in any direction within 768 units. It ends when no further visible eligible target is reachable, upon world impact, after two seconds without a hit, or after ten seconds total. Sparse groups receive less total damage; unused damage is not concentrated into one boss.

Target acquisition uses nearby blockmap actors, checks line of sight and excludes the shooter, players, friendly monsters, dead/dormant/invulnerable actors and already visited targets. Actual damage still passes through normal damage factors, custom shield handling, class abilities and boss protections. One saved projectile identity owns the complete BFG chain, retaining target history and critical-roll identity through save/load.

The grenade follows [Quake's original weapon behavior](https://github.com/id-Software/Quake/blob/master/qw-qc/weapons.qc): forward launch plus upward impulse, gravity, bouncing, enemy-contact explosion and a 2.5-second fuse. Its speed is 600/35 units per tic, upward launch impulse 200/35, gravity factor 800/(35*35), blast damage 120 and radius 160. Collision response uses UZDoom's persistent bouncing rather than porting Quake physics. It reuses the existing rocket-ammo capsule sprite, shell impact sound and rocket explosion artwork; no Quake assets are imported.

## Validation

Target engine: UZDoom 5.0.1. Run `python -B tools/test_secondary_fire.py` with `--mode logic`, `--mode chain`, and `--mode rate --class Commando`. Set `UTNT_ENGINE` and `UTNT_IWAD`, or use `--engine` and `--iwad` to select the installation. Optional `--mod` and `--compile-only` select the package and compile check. `python -B tools/test_secondary_fire_coop.py` runs two local network peers and compares their damage checksums. During development, `--overlay` tests changed weapon sources over a previous integration package; omit it once that package already includes the module.

Fixtures live under `tools/fixtures/secondary-fire/`; generated test packages go to `tutnt/.codex/builds/`, logs/screenshots/saves to `tutnt/.codex/logs/secondary-fire/`, and result summaries to `tutnt/.codex/validation/secondary-fire/`. The tests exercise firing input, ammo costs, barrel persistence, last-shell behavior, grenade bounces/fuse/contact damage, plasma size/damage/gentle steering, targeting through geometry, chain target uniqueness and damage budget, shields, Rage, Scout boss critical protection, and Overdrive cadence.

Validated on 16 September 2026 with UZDoom 5.0.1: 24 state/damage checks, 11 chain checks and 19 cadence/ammo checks passed. Two real local peers passed three checks each with identical target-health checksums, unchanged teammate health and separate ammo ownership. The final integration package passed engine loading plus integrated logic, chain and cooperative checks. Four in-game views cover the weapon/projectile presentation. The regular build also validated generated definitions, localization, font coverage and ACS; a final launch-sound-only package refresh used the same verified snapshot builder and engine check.

These are focused regressions, not a full campaign balance playthrough or WAN multiplayer test. The work-layout checker still reports 15 pre-existing map editor/autosave/backup files; this task did not create or move them.

## HUD concept

The requested mockup proposes small bronze I / II badges next to current weapon ammo. I is always shown; II appears only for weapons with alternate fire and briefly lights amber when used. The mockup is a local design artifact; this indicator has not been implemented.
