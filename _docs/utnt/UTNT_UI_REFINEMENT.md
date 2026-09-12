# UTNT UI refinement

Implements UI recommendations 1, 2, 3, 6 and 7. Requires the existing UZDoom 5.0.1 target.

## Shared layout and readable text

`UTNTUILayout` supplies a shared user scale (`UTNT_uiscale`, 0.75–1.5), screen margins,
gaps, a bottom HUD reserve and a top reserve for the original boss plaque. Notice,
secret, objective and subtitle panels use these metrics. The approved boss artwork
and its native dimensions remain unchanged. Compact objectives and completion
headings wrap at readable SmallFont size instead of shrinking long translations.
Notices are placed below visible corner objectives and above subtitles. The manual
objective plaque uses a compact text layout if its artwork would force body text
below native pixel size. The UI-scale slider is under UTNT HUD options; subtitle
scale remains independently adjustable.

## Notice delivery

Priority is interaction failure (missing key), then discoveries/checkpoints, then
ordinary hints. A higher-priority message interrupts the current one; an unexpired
interrupted message returns to the queue. Equal priorities retain FIFO order. Counts
and repeated keys still coalesce using the existing IDs and groups.

Pending lock failures expire after 105 world tics; ordinary hints after 700 tics.
Discoveries and checkpoints have no expiry while queued. Only ordinary hints are
subject to the 32-entry cap. Once visible, a message receives its text-dependent
reading time, 105–350 UI tics plus the existing fades. While hidden behind menus,
the automap or manual objectives, obsolete active hints are also discarded.
Pausing the world does not age deadlines. The queue intentionally remains transient:
loading a save or changing maps clears it, as before; saved objective progress is separate.

## Chapter transitions

The real `INTERMAP` now uses `UTNTChapterState` and `UTNTChapterUI`. Its embedded ACS
initializes the saved state once through an OPEN adapter. Existing LANGUAGE story
fragments are concatenated, their authored paragraphs retained, and old fixed-width
line breaks reflowed. All ten headings and control hints are localized in English
and German. Existing untranslated story fragments continue to use their original
English fallback; this change does not invent replacement narration.

The original paired images retain their aspect ratio and crossfade on their original
change schedule. Original voice recordings remain at their original start offsets.
Each reader has a saved page, reveal state and page-start time. **Use**, **Enter**,
**Space** and **Right** reveal the current page first, then advance. **Left** returns
to the previous page. Holding Use produces one action, not repeated skips. Menus,
console and pause do not accept chapter navigation. The first text starts after
110 tics; leaving the chapter cannot occur before the original 210-tic skip threshold.
Text now waits for the reader instead of automatically disappearing on a timer.
Resolution, UI scale and language changes reflow the pages; the saved page number
is clamped to the resulting page count.

In cooperative play, each player reads independently. Only the engine's network
arbitrator can advance the campaign; the authority lookup follows the current
arbitrator and falls back to the first active player. Requests cross the normal
network-event boundary and are checked in saved simulation state. UI code never
teleports players. Duplicate final requests are ignored after the transition starts.

Campaign destinations are unchanged: 1→2, 2→3, 3/4→5, 5→6, 6→7, 7→8 or secret 9,
8/9→88. Chapter 10 retains its standalone Lost Episode ending. Existing panorama
scripts 251 and 254, their timings, the 70-tic travel fade and all map geometry are
preserved. Chapters 8/9 and 10 enter their authored ending sequences when the reader
continues from the last page. The Lost Episode's ending music begins with that
sequence. Old saves made inside the former ACS-driven INTERMAP are not a supported
migration target; save/load of the new chapter state is covered by the runtime suite.

## Targeted performance work

Notice line wrapping, shadow strings and line widths are cached until text or width
changes. Chapter story assembly and wrapping are cached until heading/language or
layout changes. Subtitle wrapping retains its existing cache. The live regression
fixture counts actual cache rebuilds over 1,000 repeated notice preparations and
100 repeated chapter preparations, and checks invalidation on text and width changes.

Heat-source handler lookup now runs with the existing five-tic heat update rather
than on all 35 tics per second. Status-bar cutscene visibility still synchronizes
every tic. Healthy/dead-player heartbeat polling is reduced from 35 to 7 checks per
second. Active low-health pulse intervals and volume formulas remain unchanged;
entering the low-health state can be noticed at most four tics later (about 114 ms).
These are reductions in work performed, not an asserted FPS increase.

## Immutable package builds

`tutnt_build.bat` continues to call `tools/build_utnt.py`. The builder acquires an
OS-held lock for the output PK3, hashes/copies its source inputs into a temporary
snapshot, and compiles ACS only there. No live map or common ACS bytecode is changed
by an ordinary package build. `--check-only` checks the snapshot against the supplied
bytecode and fails on stale modules without rewriting the project.

After compression and the engine check, source hashes and Git provenance are checked
again. A concurrent source change, second build, compiler/engine failure or locked
output prevents replacement of the previous package. The lock file can remain on
disk safely; the OS releases ownership when its process exits, including a crash.

`UTNTBLD` in the archive records the source fingerprint, full Git commit, whether
local changes were present and hashes of the shipped inputs. Its 12-character build
ID incorporates the compiled payload and provenance. `LANGUAGE.zzbuild` exposes
**Build ID / commit**, with `+local` for working-copy changes, in the UTNT HUD menu.
Unpackaged sources explicitly display a development-source label. Logs record the
published PK3 hash and build ID. Repeated builds of identical inputs are deterministic.

## Running the checks

Configure `UTNT_ENGINE`, `UTNT_IWAD` and `UTNT_ACC`, then run:

```text
python tools/test_ui_suite.py --mod path/to/tutnt.pk3
python tools/test_ui_suite.py --quick --mod path/to/frozen/tutnt
python tools/test_ui_regression.py --mode build --mod path/to/tutnt.pk3
```

The suite covers combined boss/objective/notice/subtitle display, secret messages,
automap, menus, death, save/load, English/German, 4:3/16:9/ultrawide and OpenGL/Vulkan.
It exercises native lock failures, independent two-peer chapter reading, host-only
travel, all chapter destinations and both complete finale timelines. Test fixtures
and logs are outside the shipped mod. `test_build_snapshot.py` separately checks
determinism, manifest hashes, snapshot isolation, cross-process locks and preservation
of the old archive when sources change or the engine rejects the candidate.

Recorded results and selected screenshots are in `tools/validation/ui-refinement-2026-09-08/`.
The evidence reports the exact build/source snapshot and coverage; it is not a claim
that every campaign interaction or third-party addon combination has been played.
