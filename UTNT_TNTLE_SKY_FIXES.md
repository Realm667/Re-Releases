# TNTLE sky seams and restored lava (2026-09-09)

The dark sky lines also appeared with SSAO disabled. The manual bilinear filter
used implicit texture LOD after wrapping and quantizing its tap coordinates.
Their discontinuous derivatives selected unrelated mip levels, producing dark
lines with mipmapped texture filtering. Explicit LOD zero at the four texel-center
taps removes that dependency. Both material shaders and their generator source
use the corrected sampling. The approved artwork and animation are unchanged.

The two new sky rooms also receive sector special 90 (`GLSector_Skybox`). It
enables clamped skybox surfaces and a single rectangular floor/ceiling draw;
it is not an SSAO-disable special. `DisableSkyboxAO` is set explicitly for TNTLE
in MAPINFO, retaining AO in the playable map. The UZDoom source implements these
separately in `hw_flats.cpp`, `hw_walls.cpp`, `hw_drawinfo.cpp` and `g_mapinfo.cpp`.
No map topology, gameplay sectors, ACS, sky-camera assignments or area-alignment
bindings change in this correction. Only the two appended sectors gain special 90.

The installed package at diagnosis identified itself as build `83f6cc30babc`,
commit `ee303644993885c77188a49907dc8eec1518882e`, with `local_changes=false`.
It lacked `GLDEFS.lava`, both lava shaders and the crust-height resource; its
GLDEFS had no lava include. The approved lava work still existed only as local
working-tree/untracked resources. A subsequent build from committed sources
therefore reverted to the original QLAVA appearance.

The existing approved lava resources, their GLDEFS binding and replacement of
the three superseded ANIMDEFS warps are now included in this correction's commit.
The surface shader and crust artwork are restored byte-for-byte from the existing
working project. No new lava design is introduced. See `UTNT_LAVA.md`.

`tools/test_tntle_materials.py` reproduces gameplay sky views and the longitude
seam with trilinear filtering, 16x anisotropy and SSAO 0/3. Frozen sky comparisons
check that gameplay sky portals do not acquire AO; separate lava samples verify
motion. When testing a PK3 it also requires the lava resources and include.
`tools/test_lava.py` is the existing floor/fall/mapping/save-load regression.
Exact logs and review captures are under `tools/validation/tntle-material-fix-2026-09-09`.
