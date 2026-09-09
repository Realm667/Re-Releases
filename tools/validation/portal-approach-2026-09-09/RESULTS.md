# Portal direct-approach regression — 2026-09-09

The reported TNT03B route (map switch, noclip and fly) is reproduced without
executing an activation command. The previous test explicitly ran ACS 176 and
missed this path. The baseline log's PASS means that the absence was reproduced:
Dormant=1, PortalActive=0, emitters=0, motes=0, suction=0.

After the fix, the ordinary first-person player camera is placed 64 map units
in front of the mapped portal. Before any activation call, one emitter produces
motes and the actual postprocess intensity is 0.5. The supplied before/after
images use that view. Screenshots are static evidence; motion is checked through
the active emitter/mote counts and shader state, not inferred from the image.

The approach regression has ten assertions per run: direct arrival; both legacy
ACS visibility hints; explicit shutdown; a legacy hint preserving shutdown;
save/load while off; explicit activation; quality 0; restoring quality 3; and
save/load while active. It passes on OpenGL and Vulkan with runtime overlays,
then on Vulkan using the rebuilt normal package and only the two-file test handler.

The rebuilt package also passes the existing Vulkan 128/192 fixture, distance
gates at 240/128/96/64/24 units, postprocess settings, occlusion, manual switching,
save/load, and campaign activation in TNT03B, TNT04A and TNT04B.
There are 8 passing runs and 378
logged assertions in results.json; the baseline and older-save probe are separate.
No new multiplayer test was performed in this follow-up.

## Save compatibility

The older-save probe is NOT a passing migration test. UZDoom rejects the save
because the common TUTNT ACS module size changed (7284 versus 7216 saved bytes).
Restart the engine and start TNT03B freshly for this build. Save/load within the
new version passes; old saves were not forced past the engine compatibility check.

## Package and reproduction

Engine: UZDoom 5.0.1, user's installed engine. Build ID: 0e5b9e0503fd.
Normal tutnt.pk3 SHA-256: 0d7bcb5164ccc6a286c26cd039fd39432d79b97ac0e1622285fe182268380216
The full package includes the shared working tree, including other tasks' local
changes. Only this fix's files are committed. Runtime identity between the package
and the portal ZScript/ACS bytecode was checked byte-for-byte. ACS source is
excluded from the distributable and is recorded separately in runtime-sha256.json.

Run tools/test_portal_approach.py with --mod, --engine, --iwad and --renderer 1.
Run tools/test_portal_suction.py with the same inputs and --renderer 1 --campaign.
Use --out to select an isolated test output directory. These fixtures do not ship
in the game package and do not require a user save.
