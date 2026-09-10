# Source implosion audio sources

Klerrp: implosion_near.WAV (121942) and implosion_far.WAV (121941), Freesound,
CC0 1.0. See sources.json for original pages, exact public download URLs and
SHA-256 hashes. The high-quality public MP3 previews were decoded to PCM16 WAV;
these are not the login-gated original 32-bit WAV downloads. No substitute SFX.

Near supplies the high-frequency break; Far supplies the low-frequency body.
The runtime file is a deterministic seven-second edit with reverse build-up,
100 ms near-silence, the combined forward impact at tic 158, and a fading tail.
Rebuild it with python -B tools/build_source_audio.py (requires NumPy).
Source WAVs are retained here to rebuild without external decoding libraries.
