# Voiceover audio

Updated: 13 September 2026.

## Original voice option

UTNT settings > Sound and subtitles > Legacy voice acting selects the original
43 OGG recordings for dialogue and chapter narration. It defaults to off, is
saved as the per-player `UTNT_legacyvoices` preference, and applies when the
next recording starts. An already playing line finishes with its current voice.
The menu label and help are translated into all four supported languages.

Original recordings live in `tutnt/sounds/voices/legacy/LGVOC001.ogg` through
`LGVOC043.ogg`, with matching SNDINFO names. Renaming preserves their bytes.
The current MP3 files retain the `VOC001` through `VOC043` names.
Both dialogue playback and chapter transitions use `UTNTVoiceAudio.Resolve`.
Subtitles remain localized independently of the selected English audio.

Dialogue queue duration covers the longer of the two actual recordings and
the existing minimum subtitle duration, preventing early interruption. This
timing is identical across cooperative peers even when their voice preferences
differ. Existing chapter progression and explicit intro skipping stay intact.


All 43 recordings in `tutnt/sounds/voices/` receive an input amplitude gain
of 1.6 (+4.0824 dB). Dialogue and chapter narration retain their names,
sample rates, channel counts and exact decoded sample counts, preserving
playback timing and subtitle synchronization.

## Legacy option validation (13 September 2026)

- All 43 renamed OGG files match their original SHA-256 hashes byte for byte.
- The rebuilt shared package contains all 86 recordings with matching source hashes
  and passes the ACS, engine, localization and font gates.
- `tools/test_legacy_voices.py` passes 511 engine assertions: both sets decode,
  default/legacy/restored selection works, duplicate triggers stay deduplicated,
  and dialogue timing covers both recordings. All 86 sounds were observed on
  active audio channels through the actual dialogue and chapter playback paths.
  Audio output was muted; this was not a subjective listening test.
- `tools/test_options_menu.py` passes 924 assertions across English, German,
  Spanish and French. The German voice-options menu was also visually checked.
- Definition-table checks, native-font generation checks and all 14 localization
  unit tests pass. A complete campaign or multiplayer playthrough was not run.

Local evidence: `tutnt/.codex/validation/legacy-voices/`; audio and menu logs:
`tutnt/.codex/logs/legacy-voices/`. The work-layout checker reports eight
pre-existing TNT01/TNT02 editor backup/autosave files dated 10–12 September;
none were created or moved by this change.

## Processing

The current local MP3 recordings were the source for this change. Their
amplified MP3 replacements supersede the former tracked OGG resources;
ship only one resource per VOC001â€“VOC043 name. The SNDINFO bindings remain
unchanged and resolve the existing extension-independent logical names.

FFmpeg 6.1.1 applies `volume=1.6:precision=double`, then encodes with
`libmp3lame -q:a 0` and gapless Xing information. Metadata is cleared to
avoid carrying obsolete gain tags. This is a lossy re-encode; the exact
unmodified MP3 inputs are retained in the local backup.

Most dialogue recordings would clip with unrestricted gain. Where the
oversampled input peak plus gain exceeds -1 dBFS, processing uses 4x
oversampling and a look-ahead limiter: 2 ms attack, 10 ms release, disabled
auto-level and enabled latency compensation, followed by resampling to
the original rate. The limiter ceiling starts at -1 dBFS and is lowered
only if the encoded output would exceed the -0.3 dBTP validation ceiling.
36 files pass through this protection; the remaining seven need no limiter.

This applies the requested gain while containing loud peaks; it is not a
promise of a uniform 60% increase in perceived loudness. Measured RMS gains
range from +2.846 to +4.089 dB, with chapter narration at approximately
+4.08 dB. No dynamic normalization or changes to music/effect levels are used.

## Why the gain is in the audio files

The voice playback paths already request volume 1.0. UZDoom caps
`volume * sfx->Volume` at 1.0 in `SoundEngine::StartSound`, so an SNDINFO
`$volume` above 1.0 cannot amplify these recordings beyond their current
playback level. Raising the signal in the assets avoids that ceiling.

## Validation and local originals

All 43 outputs decode successfully. Original and output sample counts,
sample rates and channel counts match exactly. No decoded sample reaches
full scale; the highest measured 4x oversampled output peak is -0.430 dBTP.
These are automated signal checks, not a subjective listening assessment.

The shared `tutnt.pk3` was rebuilt with `tools/build_utnt.py` and passed
the engine, ACS, localization and font checks. All 43 packaged voice hashes
match the validated outputs. A separate UZDoom run loaded every voice from
the package and confirmed all 43 on active sound channels with the output
volume muted. The run reached its completion marker and exited normally.

- Original inputs and SHA-256 manifest: `tutnt/.codex/backups/voice-gain-20260912/`.
- Engine playback and package evidence: `tutnt/.codex/validation/voice-gain-20260912/engine-audio.json`.
- Per-file processing, hashes and measurements: `tutnt/.codex/validation/voice-gain-20260912/audio-validation.json`.
- Reproduction script and checked candidates: `tutnt/.codex/work/voice-gain-20260912/`.

Always reprocess from the saved originals, never from the amplified files.
