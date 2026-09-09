# TNT04C alternate sky validation

- OpenGL and Vulkan: 20 assertions each, including initial load, save/load,
  TNT04CN isolation and return to TNT04C. No missing SkyViewpoint warnings.
- Complete candidate package: engine-accepted, 14 ACS modules compiled unchanged;
  six runtime assertions and visual beam alignment check.
- Map bytes unchanged; tag-88 cylinder endpoint verified as (962,13570,-992).
- Five closed elliptical paths and ordered finite-distance parallax checked.
- 12304 matching cube-boundary samples, maximum channel difference zero;
  downward face completely black.

Initial full-source attempts caught transient compiler failures in concurrently
edited Source/Credits files. Lifecycle checks therefore use the previously built
package plus precisely the sky files; final package checks use the full rebuilt
current source tree (candidate build 80c0a4d9ec83).

Run tools/test_alternate_sky.py with --engine, --iwad, --work and --renderer 0/1.
The exported static cubemap cannot animate or react to camera translation;
hardware materials provide those effects. No engine source or AO code changed.
