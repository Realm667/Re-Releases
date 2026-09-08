# TNT02 distance and atmosphere correction

UZDoom 5.0.1, Vulkan: 28 assertions including distance distribution, exact thunder deadlines, exactly one dispatch, save/load with pending distant thunder, roof gating and pulse baseline. OpenGL: 10 assertions plus the same image checks. Both pass.

Screenshots are real game frames. Far/mid/near images hold each peak for inspection; natural near flashes remain brief. The measured reference sky is approximately 63% darker than the previous implementation. Both renderers show distinct increasing sky/world brightness, almost neutral sky color, animated clouds, and zero sampled interior difference between dark and near-flash states.

The scripted 1000-event sample yields 595 distant, 337 medium and 68 close events, with at least three intervening events between close flashes. The saved distant event dispatches once at its retained deadline. These automated runs disable audio; they verify sound gain/pitch values and dispatch timing rather than subjective loudness. Structure checks preserve all gameplay geometry, interior sectors and remaining ACS. Full live-project compiler check also passes. The tested snapshot contains the same runtime implementation; the final source only rewords one code comment. No complete multiplayer campaign is claimed.
