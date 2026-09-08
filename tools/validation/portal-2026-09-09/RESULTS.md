# Portal visual revision — 2026-09-09

Replaced the regular procedural vortex with authored asymmetric infernal folds,
a ragged black chasm, red veins, independent deformation of three depth layers,
and normals derived from those same folds. The local particle, light, audio and
activation code from the first implementation is unchanged.

## Final package

- `tutnt-portals-v2.pk3`, build `b606c6565b56`, 8994 entries, 165970687 bytes.
- SHA256: `cfe551fee7f0fd460c4249e3f6062c2fc2ffd50d1adae1f59eace673708f801a`.
- Full current worktree snapshot at `b534f049be2d0929f859bd5b2a3281e531017fc3`
  plus local changes, including ongoing work by other tasks.
- All 14 ACS modules compiled with unchanged bytecode; archive integrity and
  engine load passed. No map bytecode changed for this portal revision.
- Final packaged TNT03B runtime passed in OpenGL and Vulkan on UZDoom 5.0.1,
  NVIDIA RTX 4080. Both reached `UTNT_TEST_END`, exit 0, without VM errors.
  Tests verified that packaged shader, material binding, authored texture and
  portal actor source exactly match the installed files before launching.
- `hell-package-0/1` images show actual gameplay rendering without bloom,
  including later animation frames and a second camera position. A fixture
  activates the portal and positions the camera; it does not override materials.

## Material and functional checks

- Fixed shader time, identical camera and a controlled light, three renders:
  normal material, flat normal, and no camera-dependent depth displacement.
  All passed. Mean absolute RGB pixel differences (0–255 scale): normal relief
  0.26218; depth displacement 1.03503. These establish an observable contribution,
  not a performance or perceptual-quality guarantee.
- Both 128/192 widths: 206 assertions passed in Vulkan covering activation,
  independent deactivation, effect quality, reduced effects, save/load, bounded
  particles, texture fitting and preserved floor material. This check preceded
  the final shader-only edge fade; actor logic was unchanged afterward.
- TNT04B, a different portal orientation, also passed with the new material.
  Its included image precedes the last edge-fade correction. The final package
  tests cover that correction from two camera positions in TNT03B.
- Earlier GL/Vulkan lifecycle and two-peer coop evidence remains separately in
  `../portal-2026-09-08/`; no new coop claim is made for this material-only change.

The main `tutnt.pk3` was not replaced. Load the full v2 package as the UTNT mod,
not on top of another UTNT package. The shader requires the hardware renderer;
the existing static software/editor fallback remains unchanged. This is not a
full campaign, WAN multiplayer or minimum-hardware performance acceptance test.
