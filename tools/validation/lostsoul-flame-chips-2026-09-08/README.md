# Lost Soul flame chips — revised effect

Supersedes the high, soft gold trail documented in lostsoul-sparks-2026-09-08.
The dedicated UTNTLostSoulEmber visual now clips three small flame fragments
directly from the original SKULA1/SKULB1 IWAD sprites through TEXTURES.fire.
Their red/orange/yellow palette indices, transparency and hard pixel edges
remain intact. No generated bitmap, torch material, shader or additive white
halo is used. Render with normal translucent blending and fullbright pixels.

Births are 0.55–0.85 radii behind the actor's facing direction, within half a
radius sideways and 0.48–0.68 of its height. For an ordinary Lost Soul this is
roughly 27–38 units above its origin, within the flame, instead of 56–66 units
above its origin. Rise speed drops to 0.16–0.38 units/tic and lifetime to 16–24
tics. Rearward drift sheds a short trail. Each chip retains 10% of flight
velocity, keeping moving emissions in world space. Normal births occur every
two tics; the existing quality, reduced-FX, distance and ambient budget apply.
Death stops births. Original monster states, AI and Terror exclusion remain.

Validation: full UZDoom 5.0.1 build; all 14 ACS modules current. The immutable
package identified in manifest.json passed 13 checks on each renderer:
four orientation checks with 16 actual births each, then idle, chase, charge,
save/load, disabled FX, reduced FX, LOD culling, re-enabling and death.
Live particles are checked for dedicated textures, shader exclusion and their
short lifetime. Front, side, rear and charge screenshots were inspected.
The front view naturally hides particles behind the skull; side/rear views
show the chips emerging from the flame. No full campaign/coop test is claimed.

Reproduce with `python tools/test_lostsouls.py --mod tutnt.pk3` and configured
UTNT_ENGINE/UTNT_IWAD. Source hashes identify this revision; unrelated local
work may also be present in the tested full project package.

Installation completed: the active tutnt.pk3 was subsequently refreshed by a
newer full project build. Both effect resources are byte-identical to the
tested revision, and the installed package passed a fresh engine compilation.
No overlay or rollback was needed. See installed.json for its hash and build
ID. candidate.json records the earlier, now-resolved installation blockage.
