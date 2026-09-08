# TNT04A shared chapter intro

TNT04A now uses UTNTChapterState and UTNTChapterUI, the same saved reader as INTERMAP.
The reader wraps both existing localized narration passages (UTNT_VOICE_038/039),
uses the shared UI scale/cache, and displays the original TNTE4_1/TNTE4_2 images.
The authored ACS timeline retains voice clips, music, map setup and the normal ending.
Enter reveals text, advances pages and can finish; Left revisits the preceding page.
A fresh Use press skips immediately for the host. Holding Use on map entry does not skip.
Cooperative readers have independent pages; only the network arbitrator can end the intro.
The common completion path clears the chapter overlay and releases blocking lines,
actors, notarget/freeze and the hidden HUD exactly once. The map briefing waits for
that completion signal, including after skipping. Chapter progress survives saves.

Only SCRIPTS and BEHAVIOR change in tnt04a.wad; geometry and sky setup are preserved.
The existing skip implementation supplies the common finish and voice replacement.

## Verification

UZDoom 5.0.1: seven runtime cases, 312 assertions, including natural completion,
both authored voice segments, immediate skip, held Use, saving/loading mid-reader,
post-intro saves, two real cooperative peers and existing INTERMAP regressions.
English 1280x720 and German 640x480 at 150% UI scale were visually inspected.
Tests run with audio disabled; narration timing and selected clips are asserted.
Evidence: tools/validation/intro-chapter-2026-09-09.
Set UTNT_ENGINE and UTNT_IWAD, then run tools/test_intro_chapter.py --case
compile|early|saved|held|normal and tools/test_intro_chapter_coop.py.
