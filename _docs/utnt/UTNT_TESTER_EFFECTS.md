# Tester effects follow-up

Updated 15 September 2026. This continues [the original feedback checklist](UTNT_TESTER_FEEDBACK.md). Implemented changes are distinguished from unresolved reports; a passing compile alone is not proof that a reported visual or performance defect is gone.

## Follow-up checklist

| Request | Status | Change / evidence |
|---|---|---|
| Mancubus fireball trails | Implemented; runtime checked | Lower opacity, proportional fading and independent random roll/scale. |
| Cacodemon fireball trails | Implemented; runtime checked | Both regular and miniature trails receive the same treatment. |
| Hectebus fireball trails | Implemented; runtime checked | Center/ring trails are more transparent and varied; their existing animation phases remain. |
| SoulHarvester fullbright/self-light | Implemented | Removed fullbright from attack frames; nine attached lights use DontLightSelf. Existing selective SLHV brightmaps remain active. |
| Tortured Soul poison attack | Implemented; actual damage checked | Authoritative projectile collision replaces the cosmetic-only actor. Cloud damages a shootable target and the player, and expires. |
| Poison cloud appearance | Selected design 3 implemented | Eight transparent spore-cloud frames from the approved mockup direction; retained source artwork and reproducible extraction. |
| TNT01 stained glass | Implemented; scene checked | NEUESDI uses a selective 60% brightmap on warm glass, leaving dark leading/frame unlit. |
| TNT01 missing teleporter runes | Implemented | Reactivated the two dormant authored rune spawners (TIDs 151/152); both pads visually checked. |
| TNT01 broken-computer sparks | Implemented; repeated activation checked | Existing script 667 now runs at map opening, intermittently activating the authored emitters 61–63. |
| TNT01 machine destruction | Implemented; scene checked | Timed distortion, amber flashes, sparks and explosions with bounded lifetimes; native machine destruction/unlocking remains on its original schedule. |
| Unequal message padding | Implemented; scene checked | Subtitle background measures visible capital rows, matching top and bottom padding. |
| Animated fire windows and red grille fire | Implemented; renderer compiled | All FIRELAVA/FIREWALL variants crossfade source frames with rising distortion and restrained glow. |
| Archvile fire too small | Implemented; runtime checked | Native unit scale and original 30-frame sequence restored, plus sparse low-opacity smoke. Supersedes the earlier tiny-warning-flame treatment. |
| Keycard/skull voxel blinking | Implemented; runtime checked | Stable opaque A frame with continuous illumination pulse; native pickup behavior and voxel rotation remain. |
| TNT01 ceiling lamps after power-off | Implemented; 32 replacements checked | The switch replaces affected LITEF02 ceilings with a dark non-brightmapped ULITEOFF variant. |
| TNT02 sign closes on Use | Implemented; interaction/visual check passed | Fresh Use press starts the fade-out; the original held press is ignored. Reopening works, with separate player guards. |
| Ultimate Doom Builder load/parsing errors | Partly resolved | Removed duplicate GLDEFS/MODELDEF/TEXTURES includes and added regression protection. Local map resources now load the PK3 instead of recursively scanning the source/cache tree. Current official DLLs do not reproduce the supplied Esprima method error; full editor retest remains open. |
| Actors overlap TNT02 volumetric rays | Open | Native translucent sprite ordering remains. Segmented-ray experiment produced visible seams and was removed; no defective workaround is shipped. |
| Thunder frequency during heavy rain | Implemented; lifecycle/roof/save checks passed | Shorter storm intervals and more near/heavy thunder, preserving delayed rumble delivery and private serialized randomness. |
| Mario coin notice | Implemented; scene checked | Animated original coin, pixel panel, blue/gold border and arcade lettering, using existing localized strings. |
| TNT02 severe lag after nine minutes | Improved; exact report not fully reproduced | Reduced distant storm rain density and dynamic-light queries. Controlled peak-weather comparison improves frame time by about 22%; actor counts did not show unbounded growth. |
| Flamer/Pyrocannon deaths | Implemented; damage-source/resurrection checks passed | Native death animation gradually chars/desaturates, with partial amber coloration and sparse fading cinders for six seconds; resurrection restores the prior translation. |
| Floor seal and rusty metal border | Implemented; scene checked | Seal/runes scaled to 82%, framed with native METALF06 rusty steel, bevel and corner fasteners; rim does not emit light. |

## Runtime and rendering details

Trail alpha is 0.28 for Mancubus/Hectebus center smoke and 0.40 for Cacodemon/Hectebus ring trails. Fade increments are reduced with alpha to retain useful lifetime. Randomized roll and scale belong to individual trail actors. Projectile damage and targeting are unchanged.

TorturedSoulPoison must participate in authoritative collision: CLIENTSIDEONLY, THRUACTORS and NOBLOCKMAP cannot remain on a damaging projectile. The replacement retains its attack ownership, uses Poison damage, and has bounded fade/death states. The old cosmetic-contract catalog therefore excludes it. The selected spore artwork is a visual design, not a claimed engine screenshot; the shipped frames are derived by tools/build_tester_effect_artwork.py.

Archvile reference: UZDoom's packaged actors/doom/archvile.zs, original fire sequence (30 frames, two tics each), native scale 1.0 and targeting/crackle functions. Smoke is supplementary and small. This replaces the previous reduced flame implementation in the older checklist.

Fire-surface materials sample stable original frames so texture animation does not jump beneath the shader. SetupMaterial preserves the renderer contract. The seal uses its existing procedural material and original rune atlas; no replacement raster artwork is needed for the rusty border.

The effect origin is anchored to the visible upper central machine; the quake MapSpot is hidden behind its plinth and incorrectly failed the wall trace. The reactor's saved map clock schedules charging sparks, flashes, local explosions and a brief view distortion. Range, view direction, wall trace, shader/quality and reduced-effects options gate the view effect. Its former opaque white wash is reduced, with temporary warm sector haze. Machine kills still occur at tic 210; temporary sector fade is cleared at tic 315. Effect actors expire independently. No additional gameplay damage is introduced.

Fire deaths use 33 shared palette translations prepared on map loading. Native death/raise states and boss completion remain intact. Once settled, the behavior retains only a resurrection guard. Existing non-default translations are restored on resurrection, but the intermediate char palette derives from PLAYPAL rather than composing arbitrary third-party translations.

The ceiling-off variant is assigned by the actual map switch. An old save made after that switch was already consumed will not replay the new assignment automatically; replay from before the switch or start the map anew to see this correction.

## Performance investigation

The baseline run at TNT02 (2897, -93, -69) lasted 571 seconds. The registered effect sources stayed at 293 and client actor counts at approximately 1225–1236. Rain varied with the weather cycle, reaching over 12,000 particles in the strong phase. This supports a peak-weather load problem; it does not establish a memory/actor leak or reproduce every aspect of the tester's nine-minute hitch.

At the same forced weather peak, the baseline averaged 32.60 / 32.27 ms per frame in the two sample windows, versus 25.95 / 25.13 ms with the change. Rain count fell from about 12,114 to 9,697, while near rain remained dense. These are local controlled comparisons on this machine, not a universal performance guarantee. Distant precipitation keeps sector lighting but skips per-particle dynamic-light queries.

The optimized follow-up ran for 567 seconds without runtime errors. Across the nine-minute samples, registered sources stayed at 293 and client actors at 1230–1236; rain rose and fell with the weather rather than accumulating. The two strongest sampled windows averaged 25.69 / 25.48 ms, versus 32.75 / 31.11 ms in the baseline. The run included nine minutes of simulation at the reported location.

## Editor investigation

The installed Builder r4327 DLLs and config match the official r4327 archive byte for byte. An isolated .NET Framework probe successfully parses the first five supplied example scripts using those files; it does not reproduce Esprima.Scanner.ScanComments MissingMethodException. No speculative DLL replacement was performed.

UDB enumerates source-directory files recursively before applying ignored-directory names. Loading tutnt as a directory therefore also walks its large local .codex work/cache tree. The two local map settings now reference the integration PK3. Their original DBS files are backed up centrally and are not versioned. Duplicate native includes are removed while retaining the final occurrence/order. Intentional native lock overrides are not removed just to silence warnings.

## Validation

- UZDoom 5.0.1 compiles the candidate including both new shaders and map ACS.
- tools/test_tester_effects.py: 122 runtime assertions covering trail properties/variation, poison damage to target/player, cloud lifetime, native fire scale, stable key frames, weapon-specific burn death and resurrection restoration.
- tools/test_thunder_runtime.py: 15 assertions plus image checks for moving clouds, sky/world lightning, roof isolation and save/load.
- tools/test_weather_response.py (rain): 32 assertions for production rain/visor, shelter, freeze and save/load behavior.
- tools/test_definition_layout.py: ten tests, including duplicate-include rejection; definition tables check clean.
- tools/build_tester_effect_artwork.py --check: all 14 output images reproduce byte for byte.
- Reactor scene checks also confirm all three native monster kills and cleanup of the temporary light. The computer check confirms repeated activation of the placed sources in the normal actor list.
- Scene captures cover the selective glass, both rune emitters, French remaining-coin notice, rusty seal/runes, 32 switched ceiling textures, subtitle padding, coin panel and reactor sequence. The sign was captured visible, dismissed and reopened.

Local evidence uses tester-effects-, tester-weather-ab-, tester-sign- and tester-seal prefixes under tutnt/.codex/logs and tutnt/.codex/validation. Additional thunder/rain evidence is in tutnt/.codex/work/tester-effects/thunder-check. Work files and exploratory patches are excluded from the game package.

## Still open across the complete feedback set

- Original TNT01 one-second door hitch: precaching mitigation is implemented, exact hitch remains unconfirmed.
- TNT04CN black beam rectangles: not reproduced in either Source arena on Vulkan/OpenGL; no speculative fix claimed.
- TNT02 translucent actor/light-ray ordering: unresolved; rejected segmented experiment is not integrated.
- UDB Esprima exception and actual editor load time: source scanning/duplicate includes addressed, current exception not reproduced in the isolated parser.
- TNT02 reported severe nine-minute lag: measured peak-weather cost reduced; the exact severity/trigger on the tester's session is not fully reproduced.

## Integration package

Shared snapshot `72f61ed5b73f` passes the engine check and all 122 effect assertions and contains the current map scripts and reactor/seal sources. Size: 372,699,675 bytes. Existing unrelated TNT02 placement edits remain in the integration package but are excluded from this task commit. The work-layout audit reports eleven existing editor settings/autosave/backup files; none was created or moved by this batch.
