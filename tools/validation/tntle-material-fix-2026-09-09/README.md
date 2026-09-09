# TNTLE material correction and package audit — 2026-09-09

Tested UZDoom 5.0.1 on the complete PK3 recorded in `tested-package.json`.
OpenGL and Vulkan: trilinear/16x filtering, SSAO 0 versus 3, frozen sky portal
views, isolated longitude seam and moving gameplay lava. Sky AO deltas are
at most 1/255; the corrected seam views were also reviewed visually.
`structure.json` proves that only sky sectors 2984 and 2985 gain special 90.
Gameplay geometry, ACS, nodes and other WAD lumps are unchanged by this fix.

`lava-results.json` records surface animation, downward lavafall displacement,
continuity across different texture mappings, a static control wall and
material visibility after save/load on both renderers. QLAVA2 and QLAVASB are
also exercised. The original 65-second OpenGL fixture budget expired during
startup twice; the passing rerun uses the same 130-second budget as the TNTLE
material test and explicit background rendering. These timeouts are not
reported as passing tests. The direct-folder diagnostic also timed out;
the package tests are the runtime evidence delivered here.

`confirmed-package-regressions.json` compares the previous integrated package
with the later committed-only package; `audit-details.json` verifies every
confirmed missing resource in the tested correction and retains newer Source
and Portal code. Text comparisons normalize CRLF/CRCRLF; formatting, reordered
includes and backup files are not treated as lost features. See
`UTNT_PACKAGE_AUDIT.md` for the cause, complete scope and publication rule.
These checks are targeted rendering and resource comparisons, not a full
campaign playthrough or a cross-GPU performance claim.
