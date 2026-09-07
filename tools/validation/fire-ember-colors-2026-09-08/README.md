# Source-matched ember colors

The old ember material hardcoded gold. Dedicated orange, green and blue
material registrations now select the spark palette from the emitter color.
Particle tint is neutral so each fullbright material supplies its final color.
The same ownership test also exposed a shadowed Smoke parameter: self.Smoke
now stores the flag, enabling smoke-specific growth, fading and signed spin.
The new halo sizes use the established source anchor to distinguish barrels
and short torches without altering the approved flame-fragment behavior.

The integrated smoke/glow package passes engine loading and 60 lifecycle and
ownership assertions per OpenGL/Vulkan backend. Each live ember is checked
against its owner's expected texture. Additional isolated render probes use
the three exact ember materials with fire disabled: pixel checks require
orange, green and blue channel dominance separately, excluding flame and halo
colors. Screenshots and results are included; source/package hashes identify
the final tested package containing both smoke/glow and this correction.

The final package overlays only the fire files on the last engine-accepted
package. Concurrent uncommitted UTNT_Intermission.zc work failed compilation
in the test engine and was not modified or bundled into this installation.
The package was separately engine-loaded before running both renderers.
