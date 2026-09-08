# TNT04B integration checks

UZDoom 5.0.1: full OpenGL source-directory run and full Vulkan main-package
run both pass 18 assertions (36 total). Both include save/load, original
lightning observation and a transition to TNT04A. The first final Vulkan
source-directory attempt stalled at engine startup while another engine
validation was running; the isolated final package rerun passed.

Runtime views and moving cloud pairs were visually inspected. All twelve
static cubemap edge pairs agree within one color-channel unit. Structure
checks preserve every original gameplay block, all ACS lumps and all five
secondary viewpoints, including the concurrently committed rock-front work.
The six TNT04A shaders are unchanged. The shared comet source appears verbatim
in every TNT04A and TNT04B face program.

Build 008b191c0550 contains the matching TNT04B map, all ash materials, texture
faces, source artwork and handler. It compiles all 14 ACS modules and passes
the engine package validation. Full campaign and multiplayer runs were not
performed for this isolated visual change.
