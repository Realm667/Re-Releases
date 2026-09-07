# Objective fades — 2026-09-08

Both live PK3 cases passed: 149 assertions on TNTLE, German/Vulkan and
English/OpenGL. Checks cover intermediate opacity, endpoints after seven UI
tics (0.2 seconds), mid-fade reversal, hold/release, loading/menu cancellation,
firing and automatic-summary expiry. The runner also rejects duplicate ACS
objective messages in engine output. Screenshots show fade-in and fade-out.

All 14 ACS modules compile. Only the shared library bytecode changes; map
bytecode remains unchanged. The final PK3 passed engine validation and its
relevant contents match the current sources/bytecode. Hashes are in results.json.
Tests use isolated configs/saves and a test-only invulnerability addon.
Independent checkout work in the live PK3 is excluded from this commit.
