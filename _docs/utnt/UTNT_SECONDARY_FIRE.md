# UTNT secondary fire

Eight weapons gain alternate attacks through the engine's existing **Secondary Fire** (`+altattack`) control. Existing bindings are preserved. Fist, Chainsaw, Chaingun and Minigun retain their primary attack only. Both modes share the existing ammunition pool; the HUD continues to show that pool once.

| Weapon | Secondary behavior | Cost |
| --- | --- | --- |
| Pistol | Three rapid bullets followed by recovery; sustained cadence equals primary, including Overdrive. Partial bursts use remaining ammo. | One bullet per shot |
| Shotgun | Seven pellets with the original horizontal spread rotated into the vertical axis; unchanged damage and pump timing. | One shell |
| Flamethrower | Forward pressure cone pushes ordinary hostile monsters and redirects small hostile monster missiles, with a short world-projected refraction shader and local dust ring. | Eight gas |
| PyroCannon | Slow orb passes through actors, damages and ignites nearby visible enemies, and explodes against level geometry. | Forty-eight gas |
| Super Shotgun | Ten pellets from one barrel. The second barrel remains available after releasing fire, changing weapons, saving or loading. Firing primary with one barrel remaining fires that barrel; both empty barrels then use the existing reload animation. | One shell per barrel |
| Rocket launcher | Ballistic, bouncing grenade with enemy-contact detonation and an 88-tic (approximately 2.5-second) fuse. Explosion can hurt the shooter. | One rocket |
| Plasma rifle | Five times the projectile damage, five times the sustained primary firing intervals, 150% sprite and collision dimensions, and gentle homing in a narrow forward cone. | Five cells |
| BFG9000 | One homing projectile visits up to twelve distinct enemies in sequence, with no BFG spray and no repeat hit on the same actor. | Forty cells |

## Balance and targeting

Heavy plasma preserves the primary weapon's sustained three-shot timing pattern, scaling intervals from 3/3/1 to 15/15/5 simulation tics. Projectile base damage increases from 5 to 25 with the original damage randomization; speed stays at 25. Visual scale is 0.675 versus 0.45, radius 19.5 versus 13, and height 12 versus 8. Homing searches within 1024 map units and a 20-degree half-angle, then turns at most two degrees every two tics. The aim assistance stops after five seconds.

The BFG chain deals 260 base damage per visited target: 3120 for a complete twelve-target chain, close to the original ball plus fully connected spray's theoretical mean of 3150. This comparison assumes all original spray rays hit; actual primary BFG damage varies with distance, aim and target distribution. The chain's initial search is within 1024 units / 35 degrees; subsequent hops can turn in any direction within 768 units. It ends when no further visible eligible target is reachable, upon world impact, after two seconds without a hit, or after ten seconds total. Sparse groups receive less total damage; unused damage is not concentrated into one boss.

Target acquisition uses nearby blockmap actors, checks line of sight and excludes the shooter, players, friendly monsters, dead/dormant/invulnerable actors and already visited targets. Actual damage still passes through normal damage factors, custom shield handling, class abilities and boss protections. One saved projectile identity owns the complete BFG chain, retaining target history and critical-roll identity through save/load.

The grenade follows [Quake's original weapon behavior](https://github.com/id-Software/Quake/blob/master/qw-qc/weapons.qc): forward launch plus upward impulse, gravity, bouncing, enemy-contact explosion and a 2.5-second fuse. Its speed is 600/35 units per tic, upward launch impulse 200/35, gravity factor 800/(35*35), blast damage 120 and radius 160. Collision response uses UZDoom's persistent bouncing rather than porting Quake physics. It uses an authored native KVX grenade based on the user-provided Quake reference: a dark, faceted metal body, pointed cap and red upper/lower bands. The shell impact sound and rocket explosion artwork remain in use; no Quake model is imported.

The 16 x 16 x 40 voxel model renders at 0.4 scale (6.4 x 6.4 x 16 map units), with a central pivot and a dedicated indexed fallback sprite. Its editable profile and colors live in `tutnt/voxels/source/grenade.json`; `tools/grenade_voxel.py` and the explicit `tools/build_voxels.py` authoring command reproduce both committed runtime assets. The palette remains UTNT PLAYPAL. Native `UseActorPitch` / `UseActorRoll` enable all three axes in the hardware renderer.

While airborne and moving, the grenade turns 1.4 / 2.2 / 1.8 degrees per tic in yaw / pitch / roll, with angle interpolation. The changes affect orientation only, preserving velocity, bounce response, hitbox, fuse and damage. Orientation and age are saved with the projectile. The smoke consists of small 2.4-unit puffs, growing to less than four units, at 18% opacity and a 21-tic lifetime. One puff every three tics (six at low effects quality) uses the existing local cosmetic budget, distance limits and cosmetic random stream; no smoke is emitted once the missile explodes. Smoke respects world lighting.

## Additional weapon modes

The pistol fires its burst at four-tic intervals within a 39-tic repeating cycle, matching three primary 13-tic cycles. The longer recovery cannot be skipped by releasing secondary fire. Each bullet consumes one round, including a final partial burst. The existing Overdrive weapon-tick acceleration affects the entire burst and recovery; measured over 390 tics, primary/secondary both fire 30 bullets normally and 45 with Overdrive. Damage per bullet remains unchanged.

The Shotgun switches `5.6 / 0` horizontal/vertical spread to `0 / 5.6`. Both modes retain seven damage-5 pellets, one shell, the existing recoil and the full pump sequence.

The Flamethrower pressure blast uses a 160-unit range and a 35-degree half-cone around the aimed direction, with line-of-sight checks. It deals no direct damage. Mass reduces the push; bosses, friendly actors, players, dormant/invulnerable enemies and actors that forbid thrust are protected. Small ordinary monster missiles (radius at most 8, height at most 16, speed at most 35) are redirected away from the player and attributed to the firing player. Player/friendly/boss projectiles are excluded. The one-shot actor scan includes missiles with `NOBLOCKMAP`. The refraction front lasts 14 tics, stays attached to a saved world anchor, checks occlusion, and leaves HUD/weapon pixels untouched. Existing reduced-effects, shader and quality controls suppress the shader; bounded local dust remains the lighter visual cue. No view shake is added.

The Pyro orb travels at speed 8 instead of the primary's 30. Every seven tics it applies 40 fire damage to eligible enemies within 112 units and line of sight. A successful hit refreshes two seconds of afterburn, dealing 6 fire damage every seven tics; burns do not stack. Both effects honor normal damage factors, shields and class abilities, and use the existing charred-corpse presentation on kills. The orb passes through players, monsters and other actors; world impact causes a 192-damage/128-radius explosion, which retains normal self-damage rules. An orb that never reaches geometry disappears silently after 14 seconds. Local flame fragments keep the slow projectile readable without piling up the primary's large trail. Orb and burn state survive saves; existing cooperative friendly-fire rules still apply to the final explosion.

## Validation

Target engine: UZDoom 5.0.1. Run `python -B tools/test_secondary_fire.py` with `--mode logic`, `--mode chain`, and `--mode rate --class Commando`. Set `UTNT_ENGINE` and `UTNT_IWAD`, or use `--engine` and `--iwad` to select the installation. Optional `--mod` and `--compile-only` select the package and compile check. `python -B tools/test_secondary_fire_coop.py` runs two local network peers and compares their damage checksums. During development, `--overlay` tests changed weapon/voxel resources over a previous integration package; omit it to validate the package itself.

Fixtures live under `tools/fixtures/secondary-fire/`; generated test packages go to `tutnt/.codex/builds/`, logs/screenshots/saves to `tutnt/.codex/logs/secondary-fire/`, and result summaries to `tutnt/.codex/validation/secondary-fire/`. The tests exercise firing input, ammo costs, barrel persistence, last-shell behavior, grenade bounces/fuse/contact damage, plasma size/damage/gentle steering, targeting through geometry, chain target uniqueness and damage budget, shields, Rage, Scout boss critical protection, and Overdrive cadence.

Validated on 16 September 2026 with UZDoom 5.0.1: 24 state/damage checks, 11 chain checks and 19 cadence/ammo checks passed. Two real local peers passed three checks each with identical target-health checksums, unchanged teammate health and separate ammo ownership. The final integration package passed engine loading plus integrated logic, chain and cooperative checks. Four in-game views cover the weapon/projectile presentation. The regular build also validated generated definitions, localization, font coverage and ACS; a final launch-sound-only package refresh used the same verified snapshot builder and engine check.

The grenade-voxel follow-up passed 15 targeted runtime checks for the dedicated sprite, three-axis orientation, unchanged horizontal flight, save/load continuity and tiny local smoke particles, plus the 24 weapon logic checks. Native engine captures verify upright, angled and airborne views; the enlarged gallery uses 1.5 scale only for inspection, while normal projectiles remain at 0.4. All 74 previous KVX models remain byte-identical. `--mode grenade` reproduces this focused check.

The four additional modes passed 32 Marine checks and 35 Commando checks, including equal primary/burst cadence with and without Overdrive, last-round behavior, save/load, rotated pellet spread, pressure mass scaling and projectile ownership, geometry occlusion, orb penetration, afterburn expiry and charred deaths. Two actual local peers each passed seven further checks with identical gameplay checksums while using different local effects quality. Reproduce with `--mode extended`, `--mode extended --class Commando`, and `tools/test_secondary_fire_coop.py --extended`; development source overlays use `--overlay`. The shared integration package also passed all 32 extended checks without overlays. OpenGL is selectable with `--renderer 0` for independent presentation checks.

These are focused regressions, not a full campaign balance playthrough or WAN multiplayer test. The work-layout checker still reports 15 pre-existing map editor/autosave/backup files; this task did not create or move them.

## HUD concept

The requested mockup proposes small bronze I / II badges next to current weapon ammo. I is always shown; II appears only for weapons with alternate fire and briefly lights amber when used. The mockup is a local design artifact; this indicator has not been implemented.
