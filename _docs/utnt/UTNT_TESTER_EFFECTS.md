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
| TNT02 northern teleporter runes | Implemented; runtime and scene checked | Enabled existing dormant TeleportSparkle_R, TID 1003, at (5472, 6240), near the reported view (5494, 6101, 248); no extra emitter or gameplay changes. |
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

## Previous batch integration package

Shared snapshot `72f61ed5b73f` passes the engine check and all 122 effect assertions and contains the current map scripts and reactor/seal sources. Size: 372,699,675 bytes. Existing unrelated TNT02 placement edits remain in the integration package but are excluded from this task commit. The work-layout audit reports eleven existing editor settings/autosave/backup files; none was created or moved by this batch.

## Follow-up corrections (15 September 2026)

| Request | Implementation / evidence |
| --- | --- |
| BlueCard and other keys | All six pulsing cards/skulls store canonical native inventory classes; old saved pulse-key inventory converts silently on its next tick. 54 runtime assertions cover real pickups, native lock checks, duplicate pickups and migration. |
| HellWarrior | Red blood and a synchronized random defensive hold of 30–46 tics instead of fixed 42, the whole-tic interval within 70–110 percent. All 32 measured activations stay in range and retain shield protection. |
| Bruiser smoke | Dedicated flight/impact/explosion subclasses use 30 percent opacity with proportional fade rates, preserving lifetime and other enemies' shared smoke. Combined combat fixture: 101 assertions. |
| Sparks | Ricochet lifetime 150 percent; generator lifetime 175 percent, rounded to tics. Emission counts, collision retirement and budgets remain unchanged. |
| Snow seam | Expanded SNOW3 tile/band enable existing matched diffuse, height and normal edge blending. |
| Snow veils | Ground/air mist uses 45 percent alpha and cubic 35-tic fades. Flakes and rain veils are unchanged. |
| TNT03A2 cave | Six ordinary cave trees/stumps use dry wood, including saved winter substitutions; eleven explicit exterior ice props retain snow. Five runtime assertions cover mapping and actor properties; an in-game capture confirms the dry stump at the reported cave position. |
| TNT02 runes | Authored TID 1003 at (5472,6240) is active. Three assertions find one emitter and its emitted glow. |
| UDB | Skip internal EV/SG aliases; correct two invalid sprite names. See definition layout for actual parser evidence. |
| Floor mirrors | At most two nearby horizontal reflection heights, with hysteresis; other floors retain wet shading without another scene render. |
| CRT mirrors | Probe captures every four game tics, or immediately on a change of selected probe, instead of requesting two camera renders each video frame. |
| TNT03B brood | After the last living TNTSpider dies, all TNTMiniSpider actors die; delayed hatchlings are also cleaned up through normal deaths. Other maps are unchanged; 13 runtime assertions cover TNT03B, saved completion and a TNT02 negative control. |
| Rear portal runes | Automatic sources stay one unit from the portal face; intake particles require an unobstructed path to their portal, preventing emissions beyond a recess's solid rear wall. Both-side captures and two runtime assertions confirm an empty rear side and continued front emission. |

Rain VisualThinkers do not expose the Actor-only INVISIBLEINMIRRORS flag in the
installed engine. The reflection budget reduces repeated rain rendering but does
not remove rain from mirrors. r_portal_recursions affects additional engine
portals, so it is evaluated separately, not treated as a mirror-only control.

The first scene comparison at (3908,3739,-138) reduced rendered sprites from
18,753 to 7,719 and portal draws from 14 to 5. This confirms reduced duplicated
scene work; individual frame timings include substantial presentation jitter and
must not be presented as a reliable FPS forecast for the tester's machine.

The tester confirmed the second reflection hotspot is **TNT03A1**, at
(2692,-6005,-472). At that location a non-capture frame after throttling draws
11,866 sprites and three portals versus 48,265 sprites and thirteen portals
beforehand. Capture frames can still be costly; this is a reduction in capture
frequency, not a guarantee against every frame-time spike. The production code
does not override the shared engine portal-recursion setting.

The snow boundary and softer storm veils were captured at the reported TNT03A1
position. The change blends color and relief together and leaves the underlying
artwork intact. The full editor's opening time and the tester's worst FPS still
need confirmation in their normal play/editor session.

Final follow-up validation: `tools/test_tester_followup.py` passes 170 assertions
on the full integration candidate, including canonical key pickups/locks,
HellWarrior protection and timing, Bruiser smoke defaults, persisted brood
completion after save/load, delayed hatchlings and both portal sides.
The complete package's UDB table parses without errors: 1,280 authored entries,
zero EV aliases, 611 ms in the installed r4327 parser.

Shared integration package `a269d2a43a3f` was built with the normal snapshot builder and accepted by
UZDoom 5.0.1. It includes concurrent local cavern work and loses no resources from
the previous shared package; that work remains outside this task's commit.
The shared `tutnt.pk3` has exactly the tested candidate's runtime resource hashes.
The current layout audit reports 15 unrelated editor settings/autosave/backup
files in maps (11 pre-existing, plus four from subsequent TNT03A1/A2 editing).
No files in that list were created, moved or deleted by this follow-up.

The existing 122-assertion effect suite also passes on this shared package.
The broader snow-weather suite passes 27 checks (including frost, shelter,
freeze and save/load), but fails two sky-particle allocation/population checks.
The same two checks fail on the unchanged previous package with identical zero
sky-particle counts. This pre-existing discrepancy remains open; the entire
snow suite is not claimed to pass. Evidence is retained under
`.codex/validation/weather-before-followup` and `.codex/logs/response-snow-1.log`.
