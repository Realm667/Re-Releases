# UTNT Remaster — What's New

**Updated: 12 September 2026.** Current implemented features and improvements; unfinished local work is listed separately. Technical details and validation are available through the links.

## Interface, accessibility and presentation

- **Status bar and HUD:** customizable statistics, remaining counts, time, complete ammo/weapon displays, smooth health/armor values, translucent and floating layouts, and matching screen borders. [Details](UTNT_STATUSBAR.md)
- **Boss displays:** original portraits, names, health bars and percentages, plus clear shielded/vulnerable indicators for The Source. [Details](UTNT_BOSS_HUD.md)
- **Mission objectives:** 21 goals with brief summaries, hold-to-read descriptions, completion notices and saved progress. [Details](UTNT_OBJECTIVES.md)
- **Notifications and pickups:** prioritized, deduplicated hints; secret-discovery counters; actual health, armor and ammo gains; weapon, key and power-up cards. [Notices](UTNT_NOTICES.md), [Pickups](UTNT_USABILITY.md)
- **Readable layouts:** shared UI scaling, responsive text wrapping and coordinated placement of objectives, pickups, abilities, boss bars and subtitles. [Layout](UTNT_UI_REFINEMENT.md), [HUD](UTNT_HUD_STACKING.md)
- **Automap and navigation:** coordinated colors, map information, statistics and key legend; discovered lock markers and light/sound cues at selected newly opened passages. [Automap](UTNT_EXPLORATION_UI.md), [Access cues](UTNT_USABILITY.md)
- **Reforged menu logo:** pixel-art Quake lettering, amber rune bands and a central seal, with native and double-resolution transparent menu artwork. [Details](UTNT_MENU_LOGO.md)
- **Menus and class selection:** illustrated class cards, organized Remaster options in both native menus with restored ability/environment controls, three visual presets, bronze-and-parchment colors with gold selection, and a matching menu cursor. [Details](UTNT_USABILITY.md)
- **Chapter reader:** self-paced pages, image crossfades, original voice recordings, saved reading progress and independent cooperative reading; shared, skippable TNT04A intro. [Chapters](UTNT_UI_REFINEMENT.md), [Intro](UTNT_INTRO_CHAPTER.md)
- **Intermission statistics:** adaptive rows and corrected number formatting keep kills, items, secrets and long times readable. [Details](UTNT_INTERMISSION.md)
- **Cinematic credits:** compact animated bronze cards, Remaster contributor credits, an AI-assistance acknowledgement and personal dedications, smoother pacing, camera transitions and an uninterrupted final flight. [Details](UTNT_CREDITS.md)
- **Ending atmosphere:** “Ash & Ember” color treatment, grain and stable depth of field; storm sky, glowing crater fracture and an amber lightning-and-spark finale. [Credits](UTNT_CREDITS.md), [Sky](UTNT_ENDMAP_SKY.md)
- **Four languages:** complete English, German, Spanish and French text, with matching glyphs added to the original fonts. [Details](LOCALIZATION.md)
- **Clearer voiceovers:** louder dialogue and chapter narration, with protected peaks and unchanged playback timing. [Details](UTNT_VOICE_AUDIO.md)
- **Subtitles and comfort:** scalable subtitles with optional speaker labels/background; separate controls for injury overlays, heartbeat, smoke, heat and motion effects. [Details](UTNT_UI_REFINEMENT.md)

## Abilities and gameplay feel

- **Six class abilities:** Commando — Overdrive (firing speed) and Bollwerk (protection); Marine — Rage (damage) and Regeneration (healing); Scout — Weak Spot (critical hits) and Cloak (invisibility). [Details](UTNT_ABILITIES.md)
- **Ability feedback:** remappable controls, duration/cooldown cards, distinct screen effects and activation/expiry sounds. [Details](UTNT_ABILITIES.md)
- **Smoother recoil:** camera recoil reduced by 75% and interpolated, including BFG charging. [Details](UTNT_RECOIL.md)
- **Surface footsteps:** distance-based terrain sounds with adjustable volume. [Implementation](../../tutnt/zscript/UTNT_Classes.zc)

## Effects and environment

- **Selective glow:** adjustable, color-matched projectile and explosion halos with smooth fadeout. [Details](UTNT_EFFECT_GLOW.md)
- **Organic fire:** animated flame fragments, embers, smoke and matching light for orange, green and blue torches, burning barrels and floor fires. [Details](UTNT_FIRE_EFFECTS.md)
- **Combat and teleport effects:** directed sparks, impact dust, electrical pulses and returning teleport fragments; corrected BFG ring sizes and restored classic rocket effects with full-size smoke. [Details](UTNT_INDUSTRIAL_FX.md), [Particle sizes](UTNT_PARTICLE_SIZES.md)
- **Lost Souls:** continuous ember trails anchored behind the skull. [Implementation](../../tutnt/zscript/UTNT_Fire.zc)
- **Smoke, steam and water:** softer ambient smoke, turbulent pressure steam, improved fountains and animated impact/landing splashes. [Steam](UTNT_STEAM.md), [Water](../../tutnt/zscript/UTNT_Splash.zc)
- **Layered liquids:** flowing water, slime and blood with surface relief; depth-layered void and star fields, retaining authored map scrolling. [Details](UTNT_LIQUIDS.md)
- **Lava:** glowing depth, crust and drifting cooled rafts; rounded spill edges in TNT02/TNTLE, restored original-size lava embers and improved emissive visibility through fog. [Lava](UTNT_LAVA.md), [Embers](UTNT_PARTICLE_SIZES.md), [Edges](UTNT_LAVA_LIPS.md), [Fog](ENVIRONMENT_FOG_GUIDES.md)
- **Portals and teleporters:** unified amber energy, original runes, rotating seals, depth effects, proximity distortion and particle suction from both sides. [Details](UTNT_RITUALS.md)
- **Dynamic weather:** escalating rain/snow cycles, gusts, splashes, snow veils and responsive ambience, with shelter and skybox coverage. [Details](UTNT_WEATHER.md)
- **Weather on the visor:** refracting rain droplets and trails, accumulating frost and gradual clearing under shelter. [Details](UTNT_WEATHER_VISOR.md)
- **Wet surfaces:** gradual rain exposure and drying, subtle darkening and real reflections in irregular wet patches on eligible TNT02 floors. [Details](ENVIRONMENT_EFFECTS.md)
- **Underwater atmosphere:** liquid-specific tint, general and distance-dependent blur, alongside separately adjustable distortion. [Details](ENVIRONMENT_EFFECTS.md)
- **Footprints:** fading snow and wet sole marks, including moving-floor support. [Details](ENVIRONMENT_EFFECTS.md)
- **Moving mechanisms:** dust along rubbing edges, improved smoke clearance/fading, and distance-attenuated camera shake scaled to connected moving surfaces. [Details](ENVIRONMENT_CONTACT_DUST.md)
- **Heat shimmer:** repaired original heat effects plus localized lava distortion, amber haze and glow across nine maps, including visible lava walls and 3D floors. [Heat](UTNT_HEAT_FIX.md), [Environment](ENVIRONMENT_EFFECTS.md)

## Skies and materials

- **TNT01:** animated blood-red storm, fixed mountain ridges and red haze; original gameplay geometry restored. [Sky](UTNT_STORM.md), [Terrain restoration](UTNT_TNT01_LANDSCAPE.md)
- **TNT02:** dark thunderclouds, distant mountains, coordinated outdoor lighting and distance-dependent lightning/thunder. [Details](UTNT_THUNDER.md)
- **Cursed Peak (TNT03A1/TNT03A2):** shared winter panorama, moving clouds, southern sunset, day/night transitions and snowfall-responsive haze. [Details](UTNT_CURSED_SKY.md)
- **TNT03B/TNT04A:** layered volcanic caldera, glowing valleys, ash clouds and rotating storm eye; distant burning comets in TNT04A. [Caldera](UTNT_CALDERA.md), [Comets](UTNT_WAR_SKY.md)
- **TNT04B:** ash-dark sky, basalt peaks, layered mountains, distant embers and comets. [Details](UTNT_ASH_SKY.md)
- **TNT04CN:** beam-aligned cloud opening, orbiting floating rocks, depth parallax and distant comets. [Details](UTNT_RIFT_SKY.md)
- **TNT04C:** restrained lava-lit clouds and floating scenery, corrected colors/lighting and platform placement, preserving the original height-dependent sky views. [Details](UTNT_ALTERNATE_SKY.md)
- **TNTLE:** basalt cavern with flowing lava falls and a separate ember-night sky; corrected filtering seams. [Details](UTNT_TNTLE_SKY.md)
- **Expanded textures:** 37 active material expansions and aligned large rock surfaces reduce repetition while preserving original scale and selected original materials. [Details](UTNT_AREA_TEXTURES.md)
- **Surface relief:** normal maps and parallax across rock, ground, grass, snow, ice, masonry, metal, rust, wood, crates and technical surfaces; source-traced doors, crates, shelves, vents and technical panels, refined snow and masonry, additional slotted floors, slab joints, wood variants, profiled panels, riveted plates and coordinated door families, aligned wall/floor relief and restrained material sheen. [Details](UTNT_ORGANIC_MATERIALS.md)
- **CRT monitors:** stronger convex glass relief, dedicated fullbright display maps, scanlines and phosphor glow, with enhanced soft view-dependent live room reflections and separate comfort/performance controls; camera-feed textures are excluded. [Details](UTNT_CRT.md)
- **Palette consistency:** restored global PLAYPAL support, corrected blue PNG assets and coordinated plasma projectile, trail, impact, glow and lighting colors. [Details](UTNT_PALETTE.md)

## Boss encounters, stability and tools

- **The Source in both endings:** shared runic shield, opening seal, exposed heart, impact/Guardian feedback and attack cues; flowing beam energy and a synchronized black-hole implosion with smoke, refraction, lighting, sound and final fade. [Details](UTNT_SOURCE.md)
- **Engine modernization:** UZDoom 5.0.1 support, saved presentation states, local cosmetic simulation and revised motion blur/postprocessing. [Implementation](../../tutnt/zscript/UTNT_Presentation.zc)
- **Performance controls:** quality levels, reduced effects, distance culling, separate effect budgets/random streams, bounded gore cleanup and reduced Source shader/lighting stalls. [Effects](../../tutnt/zscript/UTNT_Visuals.zc), [Source](UTNT_SOURCE.md)
- **Campaign and cooperative fixes:** corrected scripts/maps, shared checkpoints, safer simultaneous respawns, portal handling and cutscene recovery; local four-player regression coverage. [Campaign](../../tools/test_campaign.py), [Coop](../../tools/test_four_player.py)
- **Build and validation:** reproducible snapshot builds, ACS compilation and engine checks; regression tools for gameplay, save/load, UI, effects, translations and fonts, organized definition modules with validated entrypoints, plus a walkable gallery of all 320 relief variants. [Build](README.md), [Definition layout](DEFINITION_LAYOUT.md), [Material gallery](UTNT_ORGANIC_MATERIALS.md)

## Local work awaiting completion or commit

- **High-resolution artwork:** 34 title, chapter, frame and ending replacements at twice the image dimensions; locally staged with documented resource checks. [Artwork](../../tools/artwork/interms-hires/README.md)
- **Pending integration:** further Lost Soul/fire, palette, map, lava-spill, heat and boss-HUD corrections remain uncommitted; their completion status is not established here.

The experimental TNT01 terrain remodels, underwater caustics and extra scenic lighting were withdrawn and are excluded from the current feature set.

## Maintenance

Keep this list in English and update it with each relevant feature, improvement, fix or reversal before committing. Use one short entry per distinct feature, merge refinements into the current description, and leave tuning values, implementation history and test details in the linked documents. Keep the date and pending-work status current; do not list concepts as completed features.
