# Integrated rock validation, 2026-09-09

The main tutnt.pk3 (build ed9fbb26a24b) was built with all 14 ACS units and
passed the engine compilation check. OpenGL and Vulkan each passed four
assertions: texture size 1024x1024 and all 23 actual tier mappings, before
and after save/load. The shipped resources contain no test camera/handler.
package-validation.json identifies the exact tested package and resources.

Concurrent work added sky geometry to the live TNT04B map after the approved
rock pilot was installed. The selected rock mappings remained identical.
The integrated overview shows black pointed silhouettes and exposed-looking
background surfaces around the sky. This is a separate unresolved visual
issue in the concurrently edited map, not a passed full-scene visual review.
The approved rock surface itself is retained. The isolated pilot had no
geometry changes; its scope proof is in tools/artwork/rock-expansion.

The two portal warnings on lines 12940 and 14104 also occurred in the original
pilot baseline. No full campaign playthrough or performance benchmark was run.
texture-coverage.json is a read-only authored-area inventory, not a visibility
measurement; it was collected before the concurrent sky extension.
