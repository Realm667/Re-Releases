# UTNT usability refinements

## Player-facing changes

- Actual health, armor and five ammunition gains appear near their HUD values for 1.5 seconds. Consecutive pickups aggregate; capped or rejected quantities do not inflate the displayed amount. New weapons, keys and powerups get a small original-sprite card above the status bar. Starting equipment and script grants do not notify. Native pickup sounds, bonus flashes and message history remain intact. The feature can be disabled under Speech and HUD.
- Three class cards show the original player and starting-weapon sprites, actual maximum health and movement multiplier, and short English/German descriptions. Native class, random class, episode and difficulty selection remain authoritative. Arrow/controller navigation and mouse selection are supported.
- UTNT options are grouped into Display, Atmosphere, Combat feedback, and Speech and HUD. Original feel, Atmospheric and Reduced effects are actions applying local visual presets; every setting remains individually adjustable. Shared weather/atmosphere switches and subtitle preferences are not overwritten by presets. Motion blur is off in all three presets.
- Trying a locked door/switch records its required key or skull on the native automap. Either-key locks use the existing combined card/skull icon. Repeated attempts reuse the marker; successful activation removes it, and externally raised closed doors clear their marker. Markers survive save/load and represent shared cooperative discovery. Untried locks are never scanned into markers. Automap rotation/zoom remain native. Key sprites follow PLAYPAL, including the established blue #00759F.
- Seventeen verified access notifications trigger a warm, three-second light and a quiet positional switch sound at the affected opening. Adjacent bars share one signal; distant openings are bounded to four lights per notice. Repeat notices within four seconds do not repeat the signal. The cues change no door, switch, enemy, objective or progression logic.

## Access bindings

The complete notice-to-sector audit is in `tools/validation/usability-2026-09-09/access-bindings.json`.

| Map | Notice → sector tag |
| --- | --- |
| TNT01 | 198 → polyobject 2, original start spot (1224, 1568) |
| TNT02 | 211 → 38; 216 → 24; 224 → 29; 229 → 68; 238 → 3; 245 → 37 |
| TNT03A1 | 247 → 6; 252 → 10; 260 → 48 |
| TNT03B | 283 → 8 |
| TNT04B | 294 → 28; 302 → 38 |
| TNT04C | 308 → 9; 312 → 18; 315 → 19 |
| TNTLE | 358 → 9 |

TNT03A2 contains old script text referring to absent gate tags; TNT04CN does not call the corresponding access notices. Neither receives speculative bindings. Other maps still use the global pickup, class, options and discovered-lock features. Sector cues use actual open neighboring geometry, while TNT01's sliding polyobject uses its verified map anchor. Dynamic-light rendering follows the engine renderer settings; the positional sound is independent of dynamic lights.

## Implementation

`UTNT_PickupFeedback.zc` observes successful native inventory touches through the Marine base class. UI events never grant inventory. `UTNT_ChoiceUI.zc` renders the existing populated ListMenu and applies menu-authorized CVar changes. `UTNT_AccessFeedback.zc` uses saved MapMarker actors and the successful WorldLineActivated callback. The existing BeginNotice entry point also dispatches the bounded world cue. Separate MENUDEF, CVARINFO, LANGUAGE and MAPINFO lumps keep the additions scoped.

Engine contracts were checked against the local UZDoom source: Inventory.Touch/CallTryPickup, PlayerPawn, ListMenu, menu item activation, MapMarker/automap DrawMarker, DynamicLight and WorldLineActivated. UI cards reuse the remaster's frame, font, palette and user scale.

## Validation

UZDoom 5.0.1, Vulkan, isolated configuration files: **77 runtime assertions passed** across Marine (1920×1080, English), Scout (1280×720, German), Commando (1024×768, English), and the actual TNT01 script 244 opening sequence. Checks cover gain aggregation and caps, failed pickups, compact key cards, marker deduplication/removal/save-load, either-key icons, native keyboard/mouse class-menu routes, all three presets and light expiration. Selected runtime screenshots and machine-readable results are stored beside the binding audit.

Run `python tools/test_usability.py --engine PATH --iwad PATH`. Add `--class Scout --language deu --width 1280 --height 720`, or `--class Commando --width 1024 --height 768`; `--dungeon` runs the native TNT01 sequence. `--mod PATH` accepts a built PK3. Tests use the real mod, with no overridden production resources. All test cheats are confined to `tools/usability-tests`, which is excluded from the game package.

The cooperative marker behavior follows saved world actors but has not been checked with two connected clients in this change. The fixture runs without audio output, so sound routing was checked in code; volume has not been listening-tested. This is not a full playthrough of every mapped gate.
