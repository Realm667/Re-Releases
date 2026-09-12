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

The sequence is story -> chapter comparison -> campaign comparison -> travel or
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
