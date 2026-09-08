# UI refinement validation

UZDoom 5.0.1, OpenGL and Vulkan. 25 focused runtime cases completed with
1727 passing assertions. Seven build-safety unit tests and
all 14 ACS bytecode comparisons passed. `results.json` records the exact source
hashes and base commit of the isolated review tree. Logs use portable path labels.

Coverage: combined boss/objectives/notices/subtitles, safe screen bands, English and
German, 640×480/1920×1080/2560×1080, actual held Use input, chapter reveal/back/pagination,
save/load, two network peers with separate reading positions and host-only travel,
all eleven destination branches and the complete original ending timelines, native
door/key checks, all nine objective layouts, objective controls/fades, heat behavior
and subtitle persistence. Geometry and panorama source contracts also pass.

The notice cache reused its layout for 1,000 unchanged preparations; each subsequent
text/width change caused one rebuild. Chapter wrapping was reused over 100 unchanged
preparations. Profiler output is retained in the heat logs; no general FPS gain is
claimed from these focused measurements.

The review tree contains the recorded master baseline plus the listed UI changes.
Concurrent uncommitted effect work in the shared checkout was excluded from this
validation tree. One full working-copy build was correctly rejected by the engine
check because that unrelated work was temporarily uncompilable; the old PK3 was
preserved. Final package verification is recorded separately after committing.

These focused regressions do not constitute a complete campaign playthrough or
certification of arbitrary third-party addons. Old saves inside the former ACS-only
INTERMAP are outside the migration target; saves made with the new state were tested.
