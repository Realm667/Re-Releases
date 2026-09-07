# Fire smoke and central glow, 2026-09-08

Approved scope: preserve the current organic fire fragments; replace repeating smoke and add the larger central glow for all torch colors and sizes and burning barrels.

Four distinct density textures now alternate without immediate repetition. Independent aspect ratios, opacity, mirroring, roll and the existing directional breeze vary each wisp. A subtle material warp and five-sample filter soften the fine strands even with texture filtering disabled. Smoke births and lifetimes retain their previous budgets; green remains faint and blue retains its smokeless profile.

One persistent client-side additive halo per emitter supplies a broad soft falloff and brighter center. Gold/amber, lime/green and cyan/blue materials match the fire color. Small torches and barrels scale the halo to the source; small independent pulses keep it alive. It follows the source and respects freezing, distance, quality-off, source removal and save/load recreation. No gameplay actors are added.

Validation: full ACS build and package engine check, followed by OpenGL and Vulkan runs with 60 passing assertions each. Tests cover source ownership, exactly one glow per emitter, valid smoke variants, finite fragments, rotation, all quality modes, reduced effects, distance culling, removal, save/load, aliases and 54-source stress. Rendered pixel checks confirm orange/green/blue and animation. The approved flame-fragment class was checked byte-for-byte after newline normalization against HEAD. Screenshots include all colors, barrels and two motion frames. No multiplayer network session was run.

Asset: `tutnt/graphics/utnt-fire/smoke-atlas.png`, generated with built-in Imagegen and copied unchanged. Native TEXTURES crops the 1254-square atlas into four 627-square tiles; the shader converts black to transparency. Full generation prompt is in `smoke-prompt.txt`. Glow is analytic shader code and needs no generated bitmap. See manifest for exact tested source and package hashes.
