# Final rock rollout validation

Main package build 984a11229aa5 passed compilation of all 14 ACS units and the
engine compilation check. Package/resource hashes are in package-validation.json.
All nine modified maps passed Vulkan size/mapping assertions before and after
save/load: 1731 new tier mappings total. The final TNT04B package also passed
OpenGL. Before integration, OpenGL separately passed TNT04B, TNT04CN, TNTLE
and TNT04A, covering all four material variants. The original 23-section pilot
passed its separate final-package Vulkan regression and save/load checks.

Six focused Python regressions passed (true lengths, branches, vertical
separation, closed corner cuts, scoped patching, ACS movement exclusions).
Independent static scope and UV checks are in tools/artwork/rock-rollout.
TNT01 was replanned against its newer subdivided wall geometry before final
integration. TNT04B was patched on the current skybox map, with all existing
geometry, sectors, actors, BSP nodes and non-TEXTMAP data preserved.

comparison.html shows representative unretouched game captures for all four
materials. Before captures use the frozen baseline; final captures use the
integrated package and the same cameras/settings. Animations may differ.
Tile wrap reviews additionally checked broad seams and original feature size.
Individual generated edge contours and deliberate group/corner cuts are not
claimed mathematically seamless. QROCK4's dark material still has local strata.

The known portal warnings for TNT04B lines 12940/14104 also occur in the
original baseline. No full campaign playthrough or FPS benchmark was run.
