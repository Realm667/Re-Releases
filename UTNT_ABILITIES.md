# UTNT class abilities

Every class has two activated abilities, each lasting **15 seconds**. Its own
**300-second cooldown begins when the effect ends**. Only one ability can be
active; both buttons are locked for three seconds after an effect ends. Presses
during an active effect or lock are discarded, never queued.

Default controls are **Q: offense** and **G: defense**. Existing user bindings
are preserved. Both controls can be remapped under UTNT Options or Customize
Controls; the HUD shows the actual binding. The control tooltips describe all
six effects in English and German.

| Class | Offense | Defense |
| --- | --- | --- |
| Commando | **Overdrive:** 150% weapon cadence, 80% of normal class movement speed. | **Bollwerk:** takes 25% enemy damage, moves at 50% of normal class speed. |
| Marine | **Rage:** double weapon damage; takes 150% enemy damage. | **Regeneration:** five health per second, 15 pulses, capped at normal maximum health. Existing bonus health is preserved. |
| Scout | **Weak Spot:** 20% critical chance per victim/attack; normal enemies die instantly. | **Cloak:** invisible to enemies, removes target acquisition and existing tracking, with wandering/searching enemies. Firing does not break Cloak. |

## Critical hits and Cloak

- A critical normal kill uses `Death.Extreme` (DECORATE XDeath) only when that
  state exists, otherwise normal Death. Death logic, kill counters, drops and
  specials execute once. The engine must first confirm positive damage: shields,
  zero damage factors, dormancy and invulnerability cannot be bypassed.
- Boss critical damage is at most 10% of that actor's maximum health, with one
  successful boss critical per second per Scout across all bosses. Multi-part
  encounters retain their individual actor health limits. Boss flags, the active
  boss HUD range and all six original maps' authored encounter ranges are recognized,
  including the delay between a boss spawn and ACS starting its health display.
- Hitscan pellets in one tic share one roll per victim/player. Projectiles retain
  their tested victims through direct hits, explosions and delayed spray, including
  interleaved projectiles and save/load. Critical randomness uses a dedicated,
  synchronized engine RNG stream.
- Cloak is true invisibility plus target suppression, rather than Doom's partial
  invisibility. Former pursuers wander and can acquire other visible cooperative
  players. Already flying projectiles, explosions and map hazards remain dangerous.
  Previously existing invisibility/notarget flags are preserved on restoration.
  The first-person weapon becomes translucent during Cloak.
- Environment, self-inflicted explosions and forced/scripted deaths are not
  reduced or amplified by defensive abilities/Rage vulnerability. Weapon damage
  enhancements do not enhance self damage. Damage multipliers use engine integer
  rounding, so very small hits can round down under Bollwerk.

## Persistence and presentation

The inventory holds saved timers and follows the player between maps. Death ends
the effect and starts its cooldown; respawning does not refill abilities. A new
game begins ready. Pausing the simulation pauses timers. Activation is blocked
during cutscenes, frozen controls and non-player camera views.

Overdrive advances only firing weapon/flash states at an average of 1.5 weapon
tics per game tic, including one-tic and Hold states. It does not tick movement,
inventory, healing or the world twice. Ammo usage per attack remains unchanged.

The two HUD plaques reuse UTNT's `UTOCBG` metal surface, bronze borders, rivets,
SmallFont and shared scaling. Six native pixel glyphs identify the effects.
They show ready, active countdown, cooldown and mutual lock states. Offense uses
warm amber while active; defense uses muted green. They sit above the outer
status-bar sections and disappear with the HUD, full-screen automap and cutscenes.
No generated or third-party artwork is added.

## Validation

Target engine: **UZDoom 5.0.1**. Test fixtures are outside `tutnt` and never ship
in the PK3. Set `UTNT_ENGINE` and `UTNT_IWAD` (or pass explicit paths).

```text
python tools/test_abilities.py --class Marine
python tools/test_abilities.py --class Scout
python tools/test_abilities.py --class Commando
python tools/test_abilities.py --class Commando --mode rate
python tools/test_abilities.py --class Marine --mode travel
python tools/test_abilities.py --class Scout --mode cloaktravel
python tools/test_abilities.py --class Scout --mode respawn
python tools/test_abilities.py --class Scout --mode boss --map TNT01
python tools/test_abilities.py --class Scout --mode hud --renderer 0
python tools/test_abilities.py --class Commando --mode hud --renderer 1
python tools/test_abilities_coop.py
```

`--mod` can select a built PK3 or source folder. Results are written beneath
`logs/class-abilities`. The cadence test measures all twelve UTNT weapons;
short observation windows allow two shots of boundary quantization, rather than
claiming identical measured shot ratios for slow weapons. Two separate local
network peers verify synchronized input, independent effects, target selection,
damage and respawn persistence. HUD review covers 640x480, 960x540, 1024x768,
1920x1080 and 2560x1080 with OpenGL/Vulkan coverage.

These checks are not a full campaign playthrough or a WAN multiplayer test.
