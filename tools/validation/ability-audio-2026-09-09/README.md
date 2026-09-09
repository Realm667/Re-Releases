# Ability audio validation, 2026-09-09

UZDoom 5.0.1 with the actual OpenAL backend enabled: all three classes and two
real local cooperative peers passed 43 assertions. The two existing Ogg cues
decode to 0.788 seconds (activation) and 1.144 seconds (expiry).

The Marine run waits for both complete 15-second effects. Scout and Commando
use --fast to shorten the timer but still expire through the production Tick.
Each run verifies one cue per successful activation/expiry, no extra cues for
rejected input or cleanup/death, separate cooldown notification, save/load and
map travel. Two peers verify that player 0's cues are absent on player 1, then
that both peers receive exactly their own start/end pair. No WAN test is claimed.

Tests use the recorded committed baseline plus this contribution. Concurrent
work on the Cursed Peak renderer was excluded after its incomplete source
prevented the initial live-project run from compiling.

Run tools/test_ability_audio.py --class Marine (optionally --fast for quick
regression), then tools/test_ability_audio_coop.py. Set UTNT_ENGINE/UTNT_IWAD
or supply --engine/--iwad. Isolated test settings mute music, not sound effects.
