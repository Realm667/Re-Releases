# UTNT second pass — campaign, coop and presentation

Follow-up to `UTNT_MODERNIZATION.md`, based on commit `179735e36`. Release test target remains **UZDoom 5.0.1**, ZScript language level 5.0.0, Windows, Doom II IWAD. The local UZDoom source and current wiki export are implementation references; the development branch is not the tested release binary.

## 1. Campaign progression and map corrections

- Original boss triggers and completion barriers are exercised in TNT01, TNT02 and TNT03B. TNT04C, TNT04CN and TNTLE must actually reach INTERMAP after the original completion scripts. These tests save and reload during the encounters; an engine exit code alone is insufficient.
- TNT03A1 now terminates its repeating rocket hazard in the current map (`ACS_Terminate(14, 0)`); the old map number 1 addressed the wrong map. The regression starts the original switch script and verifies the hazard can restart after termination. TNT03A2 and TNT04B progression switches are also exercised across save/load.
- TNT04CN no longer calls undefined legacy script 669. The common `IntroText` OPEN script already supplies the intro.
- TNT02's orphan light-niche edge is closed by appending one linedef and one sidedef. Existing vertices, sectors, things, lines and sides retain their indices and properties. Stale node caches are removed so UZDoom rebuilds them. The prior unconnected-edge warning disappears.
- The footsteps entry now references the actual flat `"DOPE2 R"`, removing the old unknown-flat warning.
- A static campaign inventory records scripts, checkpoint destinations, starts, keys and locks. Real-map key tests verify rejection without keys, acceptance with keys and preservation across save/load for all five maps with native locked-door specials. They do not establish that every key is reachable from every route.

All five common boss completion blocks remain unchanged. Map SCRIPTS lumps are authoritative and the three modified WADs have matching compiled code. Boss-completion tests deliberately force boss deaths, including shielded Source phases; they validate progression, not weapon balance or the experience of fighting every boss.

## 2. Combat and ambient effect budgets

Decorative emissions and combat feedback have independent client-side pools. Ambient limits are 32/64/128 and combat limits 24/48/96 emissions per game tic at low/medium/high quality. Quality zero disables new effects; the reduced profile caps both pools at low quality. Sparks use the available remainder instead of dropping the entire burst. One-shot impacts bypass ambient tic throttling, while distance culling remains active. Rocket flames can retain their flame when only one emission slot remains.

These are emission budgets, not total particle counts. Native particles also obey engine limits. Gameplay projectiles, damage and weapon timings are unchanged.

## 3. Subtitles and localization

Localized line breaks, line widths and maximum width are cached until the text, speaker setting or wrap width changes. The saved map handler queues overlapping voice/subtitle pairs and suppresses duplicate active or pending lines. Timing uses measured durations of the 35 shipped Ogg clips, verified from their granule positions, so disabling audio on one peer cannot change shared simulation timing. The longer of subtitle hold time and clip duration governs each entry. Voice playback retains the original ACS volume (127/127 = 1.0).

Options control subtitles, background, speaker labels and scale independently. German provides **103 entries** covering the remaster menu, episode headings, initial objectives, common labels and all 35 player voice subtitles. Other original narrative strings retain the English fallback and audio remains original. This is a German foundation, not a claim of complete campaign translation.

German menu and subtitle captures cover 960×540 and 1260×540 at maximum subtitle scale. Queue ordering and pending entries are tested across save/load. Tests run without sound; they do not certify subjective audio mixing or seamless resumption of an already playing clip after loading.

## 4. Local comfort settings

Heat distortion retains its existing CVar name but is now local. Ambient smoke has a separate local setting. Injury overlay and heartbeat volume are independent, including under the reduced visual-effects profile. The four-peer regression uses opposing heat/smoke/overlay settings and different heartbeat volumes, checks that they remain local, then checks simulation consistency after deaths and disconnect.

Atmosphere and weather remain shared world settings. The original intro/cutscene behavior and authored story timing remain.

## 5. Cooperative campaign behavior

Checkpoint respawns prefer authored destinations and use collision-checked nearby fallbacks when occupied. Checks reject walls, insufficient vertical clearance and solid actor volumes, including non-shootable blockers. They account for the engine's overlap-unblocking behavior; a rejected candidate leaves the pawn at its previous location. The common respawn script retries briefly when players respawn simultaneously and retains the engine spawn if no candidate is valid.

Four real local UZDoom peers, including all three classes, test simultaneous death/respawn, distinct TIDs, Behavior recreation, acquired keys/weapons/ammo, an occupied checkpoint and graceful departure of one peer. A separate four-peer run tests death during the original TNT04A cutscene, release of all players and joint arrival in TNT04B. The existing two-peer portal/checkpoint test remains available.

Test-only statistics screens simulate continue in singleplayer and send the engine's real ready message from each coop peer. They live under `tools/`, never in the game package. Runners clean up only their own child processes after completion markers; those cleanup exit codes are not crashes. This validates local four-peer sessions, not WAN latency/loss, arbitrary join-in-progress, or 8/64-player campaign support.

## 6. Repeatable performance work

`profile_combat.py` measures frame intervals in TNT02, TNTLE and TNT04CN with fixed RNG seed 667, scripted shotgun fire and nearby Imps. It records actor/client-visual counts and engine thinker snapshots. Frame data is accumulated during the measurement and printed afterwards. Warm-up ends at tic 140; measurement ends at tic 560. The scene runs at 960×540, without VSync or an FPS cap, and without other engine instances.

The initial 24 cases cover two backends, gore limits 0/1024 and two repetitions. Six final cases repeat gore 1024 after cleanup changes. These are controlled workloads inside real maps, not full-map traversal or every large boss arena. Client visual counts exclude native particles; zero visuals in a starting view does not mean the engine drew no effects.

Profiling did not justify a broad NashGore Behavior rewrite. Its cleanup instead receives a bounded scan and a clamp for negative limits. Unsupported members of the gore stat cannot prevent eligible gore from being removed or cause an unbounded cleanup loop. A regression places such a member ahead of a gib and uses a negative limit.

| Map | Backend | Initial mean range (ms, two runs) | Final mean / p95 (ms, one run) |
|---|---|---:|---:|
| TNT02 | OpenGL | 3.26–3.27 | 3.09 / 4.12 |
| TNTLE | OpenGL | 7.43–7.44 | 7.05 / 11.33 |
| TNT04CN | OpenGL | 7.30–7.49 | 7.38 / 9.31 |
| TNT02 | Vulkan | 2.95–3.12 | 3.13 / 4.36 |
| TNTLE | Vulkan | 5.61–5.67 | 5.72 / 9.85 |
| TNT04CN | Vulkan | 6.08–6.50 | 7.00 / 9.17 |


Frame intervals include renderer/driver/OS scheduling; they are not isolated GPU times. The small repetition count and different final sample count do not support a general FPS improvement claim. In particular, the final TNT04CN Vulkan run is slower than the initial two runs (7.00 ms mean versus 6.08–6.50 ms); its actor count also differs slightly (2,790 versus 2,783). These samples do not isolate the cause. Individual thinker samples remain diagnostic, not averaged timing guarantees.

## 7. Per-map atmosphere

TNT03A1, TNT03A2 and TNTLE have distinct sky-mist scale, distant-fog distance/density and subtle outdoor tints. Only sky sectors with no existing fade receive a tint. Disabling the option restores the recorded fades; a newer change by a map script takes precedence and is preserved. Saved ownership data survives load. Existing colored lava fog and the peak's animated day/night fades remain authored effects.

Paired OpenGL/Vulkan screenshots and six state regressions cover enabling, save/load, disabling and preservation of a subsequent map-script fade. The option remains off by default. The preserved orange fog in TNTLE is already dense in the baseline; these captures do not imply a campaign-wide readability redesign.

## Validation and reproduction

| Check | Result |
|---|---|
| `runtime-matrix.json` | 32/32 passed; 132 runtime assertions |
| `campaign-results.json` | 18/18 passed; 46 runtime assertions |
| `key-results.json` | 5/5 passed; 15 runtime assertions |
| `four-player-results.json` | 4/4 passed; 325 runtime assertions |
| `coop-campaign-results.json` | 4/4 passed; 68 runtime assertions |
| `coop-results.json` | 2/2 passed; 62 runtime assertions |
| `visual-review-results.json` | 6/6 passed; 24 runtime assertions |
| `subtitle-results.json` | 2/2 passed; 6 runtime assertions |
| `combat-profile-results.json` | 24/24 passed; 0 runtime assertions |
| `combat-final-profile-results.json` | 6/6 passed; 0 runtime assertions |
| Structural invariants | 776 passed; 8779 source files hashed |
| Build / bytecode / deterministic package | 14 ACS modules; engine validation and matching repeated PK3 hashes |
| Final package runtime | TNT04CN completion marker reached |

Final PK3: 8,778 entries, 82,327,310 bytes, SHA-256 `e99c9e921d3bebb3b43367dd1fc1afbc6b8ccc7d0a4225c3f14bd46eed88701c`. Generated package remains local.


Evidence, raw passing logs, captures, source hashes and build manifests are in `tools/validation/second-pass-2026-09-06/`. Failed development trials stay in ignored local logs. Historical first-pass evidence is unchanged. Source hashes describe the exact bytes of the tested Windows working tree; Git line-ending conversion can change text-file hashes on another platform. The recorded raw vertex-boundary inventory is a diagnostic, not a list of proven broken sectors: coincident vertex indices and map tricks require interpretation.

From the repository root, configure the ignored `tools/utnt-env.cmd` as described in the first report, then run:

```bat
tutnt_build.bat
call tools\utnt-env.cmd
"%UTNT_PYTHON%" tools\test_second_pass_structure.py
"%UTNT_PYTHON%" tools\audit_campaign.py
"%UTNT_PYTHON%" tools\test_matrix.py
"%UTNT_PYTHON%" tools\test_campaign.py
"%UTNT_PYTHON%" tools\test_keys.py
"%UTNT_PYTHON%" tools\test_four_player.py
"%UTNT_PYTHON%" tools\test_coop_campaign.py
"%UTNT_PYTHON%" tools\test_coop.py
"%UTNT_PYTHON%" tools\test_visual_review.py
"%UTNT_PYTHON%" tools\test_subtitles.py
"%UTNT_PYTHON%" tools\check_engine.py --map UTNTTEST --addon tools/runtime-tests --exec tools/save-load.cfg --regression
"%UTNT_PYTHON%" tools\profile_combat.py
```

Run GPU workloads sequentially. The structure check requires Git and the baseline commit. Test runners rebuild the imported ACS fixture when needed. No engine, IWAD, PK3, local configuration, reference checkout or AGENTS.md is committed.

This is a tested implementation of the seven packages with bounded automated acceptance. It is not a guarantee of zero defects, a complete manual campaign playthrough, compatibility with pre-migration saves, arbitrary third-party mods, or older GZDoom versions. The remaining authored portal-alignment conversion notices are not silently removed by changing campaign geometry.
