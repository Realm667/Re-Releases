# TNT04CN floating mountain validation

UZDoom 5.0.1 passes 42 assertions across OpenGL and Vulkan, including save/load and TNT04A/B/C map transitions. Twelve views cover both portal rooms, different directions, the opening and the black nadir. Captures show the added mountain masses and debris; the beam endpoint remains visible.

The production material's rock alpha was rendered in an isolated diagnostic addon at a fixed camera twice, twenty seconds apart. Only the final output colour was replaced by alpha; geometry, projection and motion calculations remained identical. The central mountain silhouette moved approximately 2.65 pixels, with 1569 changed mask pixels, confirming slow GPU movement. The white alpha images are diagnostic captures, not production artwork. Bounds used for analysis: central 28–72% width, 20–72% height, avoiding the HUD.

All twelve static cube edges match exactly; the nadir remains black. All eighteen TNT04A/B/CN material faces retain the identical shared comet code. The TNT04CN map hash is unchanged. Existing cloud and rock source images are reused without edits.

The full package builds all fourteen ACS modules, passes an additional Vulkan smoke test (six assertions), and matches eighteen checked runtime resources byte-for-byte. The isolated commit tree is separately compile-checked before commit. Logs and verification.json record the checked build and results. Concurrent local project work is present in the complete working-copy PK3; only this task's files enter the commit.
