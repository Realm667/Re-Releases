# Cursed Peak horizon haze validation — 2026-09-09

The horizon haze now mixes up to 32% of the exact outdoor sector fade colour,
with its smooth vertical falloff extended from 0.45 to 0.65 radians. Both
hardware shaders and generated static fallback textures use this profile.
The slight cold-blue tint and the shared day/night transition are retained.

UZDoom 5.0.1: 44 runtime assertions passed under each of OpenGL and Vulkan,
covering TNT03A1/TNT03A2, day/dusk/night, tagged covered sectors, shared fade,
weather baseline and retired sky cameras. Vulkan captures are included here.
The cloud-motion check holds completed night to keep the fade constant; both
renderers show moving clouds and zero mean pixel change in the mountain crop.
See results.json for measured values. ACS compilation passed in both runs.
