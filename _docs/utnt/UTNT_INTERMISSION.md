# Unified UTNT transitions

The campaign uses one ZScript chapter reader for narration, illustrations and
results. Gameplay maps suppress the engine statistics screen and normal exits
enter INTERMAP. Authored map teleports, the Cursed Peak hub, secret-route scripts,
TNT04A intro, original panorama endings and ENDMAP01 remain in place.

## Sequence and controls

`UTNTTransitionDefinition` in `tutnt/zscript/UTNT_Chapter.zc` is the shared table
for destinations, original story fragment ranges, image pairs, narration sounds
and image/voice timings. INTERMAP ACS obtains its travel destination from that
same table. Its geometry, panorama scripts and 70-tic travel fade are unchanged.

The sequence is story -> chapter results -> campaign results -> travel or
original finale. Use/Enter/Space/Right first reveal text, then advance. Left goes
back through pages and results. Host Backspace explicitly skips the transition;
menus, console and pause do not generate reader actions. TNT04A retains its
existing shared-intro controls and does not insert an intermediate result page.

In cooperative games each client reads independently, with every recorded player
shown simultaneously in the comparison table. Gold marks the highest kills,
items and secrets and the lowest deaths; all tied leaders are marked. Zero kills,
items or secrets do not produce a leader highlight. A plus marks a ready player.
Names are captured with results; the local row is highlighted. The campaign view
also retains participants from earlier chapters. Large rosters use parallel tables.
Players signal readiness on the campaign page. The network arbitrator continues
once everyone currently connected is ready, or uses the explicit skip action.
A departing player ceases to block readiness; a joining player must become ready.
Input is checked in saved simulation state, and transition requests are idempotent.

All labels and hints are maintained in English, German, Spanish and French.
Narration uses the original continuous recordings and original start offsets;
pagination and translation do not restart audio. UZDoom serializes active sound
channels and their playback positions along with the saved chapter state.

## Result presentation and black transitions

Single-player uses three large bronze plaques for kills, items and secrets, each
with an absolute count, map maximum and completion bar. Active time, completed
objectives and deaths form a quieter second row. Empty categories have no
percentage or progress fill. The heading names the chapter just completed;
campaign results summarize the journey so far. Single-player navigation advances
directly and does not ask the player to declare readiness.

Cooperative results use one aligned table for up to eight participants; larger
rosters adapt into parallel panels to keep everyone visible. The local player has
a bronze row accent, leading values are gold (including ties), and team totals
remain separate from personal credit. Category icons use the ability HUD's 17-pixel
raised glyph style: crossed blades, flask, eye, skull, hourglass and checked scroll.
Both layouts use the existing mission plaque textures and original localized font.
The result area measures its own height and attaches navigation beneath it.

Normal chapter exits now fade to black before loading INTERMAP. The saved
`UTNTStatsHandler` holds the world and every player for 35 tics, takes the final
statistics sample before the hold, then releases only the freezes it owns and
performs the original destination/position/flag transfer. Duplicate exits cannot
restart it. TNT01/TNT02 walk-over exits use a line-activation adapter; ACS exits use
`BeginChapterTravel`. Cursed Peak's intra-hub travel stays immediate. Existing
Source victory staging and INTERMAP's authored 70-tic departure remain intact.

`UTNTTransitionFade` controls the outgoing overlay and a 21-tic black arrival fade
on each client. A one-shot engine crossfade replaces the melt across INTERMAP
loads in single-player, without writing `wipetype`. Network games receive the
same black overlays even though the engine disables its native wipes there.
Loading a save resumes the saved departure; it does not start an unrelated
arrival effect. This adds a short black load boundary, not asynchronous loading.
The final black layer is drawn by `UTNTTransitionFadeOverlay`, a late map-local
handler: engine static handlers always draw before map-local handlers, regardless
of their order. Ability cards and edge shaders also explicitly suppress themselves
throughout departure, INTERMAP, credits and the arrival fade. Releasing a player's
freeze immediately before travel can no longer reveal their cards over black.

## Extended result pages

Up/Down cycles between the overview, combat/resources, two weapon pages and
abilities within either chapter or campaign results. Each player's selection is
independent and saved. Enter/Right and Left retain chapter/campaign/story controls;
viewing details does not toggle readiness or delay a ready team's departure.
Single-player details use six plaques. Cooperative details keep every recorded
player visible in aligned columns, adapting into panels for large rosters.

- **Damage dealt:** effective health damage against hostile monsters, attributed
  to the engine damage source (including projectile/explosion damage). Fatal hits
  are capped at remaining health; corpses, friendly monsters and invulnerable
  phases add nothing. Scout finishing damage is counted once, in event order.
- **Boss damage:** the subset hitting bosses, using the same authored encounter
  ranges, active boss HUD registration and boss flag as the critical-hit system.
- **Damage taken:** actual health damage after armor and other reductions,
  including environmental damage and self-damage. Armor absorbed is not added.
- **Weapon use:** active gameplay tics with each of UTNT's twelve weapons selected,
  displayed as time. This measures loadout preference, not shots, accuracy or
  damage credit. Dead players, paused play, cutscenes and transitions do not count.
- **Ability use:** successful activations of each of the six class abilities.
  Rejected attempts, cooldowns and continued active tics do not add activations.
- **Health and armor collected:** actual positive gains from physical pickups,
  respecting capacity limits. Starting equipment, script grants and regeneration
  are excluded. Capture runs for every peer even with pickup notifications disabled.

On the combat page gold marks highest outgoing/boss damage and lowest received
damage, including ties. Higher resource consumption, weapon time and ability
usage are deliberately not ranked as better performance. Existing saves retain
their old counters; new fields start at zero and cannot reconstruct past combat.

## Statistics and persistence

`UTNTCampaignStats` is a saved STAT_STATIC thinker. `UTNTStatsHandler` samples
engine counters during gameplay and once before unloading, before player counters
are reset. Its saved per-visit baselines prevent re-adding an earlier hub visit.
The persistent map ledger contains no actor pointers. Chapter and campaign result
objects are copied at INTERMAP entry, so rendering and skipping cannot add counts.

Per-player metrics are credited kills, counted items, credited secrets and deaths.
Team rows use the engine's map counters and maxima, rather than summing personal
secret credits. Objectives come from the existing authoritative campaign flags.
The Cursed Peak chapter combines TNT03A1 and TNT03A2. Campaign totals include only
maps actually visited; the Lost Episode can be played as its own run.

Active time counts world tics with at least one living, non-totally-frozen player
in a gameplay map. Time is shared elapsed time, not a sum of player times. Paused
gameplay, INTERMAP, credits and fully frozen cutscenes do not advance it. Counts
retain engine behavior for spawned/revived monsters and may exceed original
completion expectations; personal kills are not a unique-monster percentage.

Save/load restores the ledger, visit baselines, page/section, readiness and frozen
results. Loading an earlier save also rewinds deaths. New games reset the ledger.
This is run-local accounting, not persistent lifetime achievements. Existing saves
cannot reconstruct previously unrecorded campaign history; use a new playthrough
for complete results. Direct INTERMAP previews show an explicit no-data message.
Player attribution uses engine player slots, as do native multiplayer statistics;
a slot reused during a run retains that slot's accumulated contribution.

The original `UTNTIntermission` drawing class remains available as an engine
fallback, but the UTNT campaign no longer displays it before the chapter reader.
`tools/test_intermission.py` now runs the unified transition regression.

## Validation

Set UTNT_ENGINE and UTNT_IWAD, build an isolated package, then run:

```text
python -B tools/test_transitions.py --mod <package> --case metrics --language de
python -B tools/test_transitions_coop.py --mod <package> --metrics
python -B tools/test_transitions.py --mod <package> --case fade --language de
python -B tools/test_transitions.py --mod <package> --case acs
python -B tools/test_transitions.py --mod <package> --case flow
python -B tools/test_transitions.py --mod <package> --case hub
python -B tools/test_transitions.py --mod <package> --case empty --language fr
python -B tools/test_transitions_coop.py --mod <package>
python -B tools/test_chapter_routes.py --mod <package>
python -B tools/test_intro_chapter.py --mod <package> --case saved
python -B tools/test_ui_contracts.py
```

The fixtures exercise actual map exits, save rollback, frozen result pages,
reopened hubs, cumulative counts, deaths and four real peers with different
languages. Existing route tests run all ten chapter definitions, the secret branch
and the original endings. These are targeted regressions, not a full playthrough.
Local evidence: `tutnt/.codex/logs/transitions-*` and `chapter-route-*`.
