# Borderless title artwork

Updated: 13 September 2026.

TITLE_1, TITLE_2, TITLE_3, TITLEPIC and TNTE4_1 use the approved
TITLE_3 variant 1 finish: detailed, original-faithful Doom/Quake matte painting,
crisp architecture, rough materials, restrained haze and readable dark surfaces.
All five images extend to every edge without decorative side frames.

The new Remaster screenshots supplied for each resource define its scene and
camera. The accepted TITLE_3 example defines the shared rendering style.
TITLE_1 retains its gray thunderstorm; TITLE_2 retains its red courtyard sky;
TITLE_3 depicts the lava fortress; TITLEPIC depicts the central beam and cloud
opening; TNTE4_1 depicts the amber seal in the Source chamber.

## Files and export

The five production files are in tutnt/hires/graphics/interms/, as opaque RGBA
PNGs at 1716 x 960 pixels, matching the preceding hires files. The logical
858 x 480 resources in tutnt/graphics/interms/ are unchanged.

Generated with the built-in Imagegen tool. The generated masters are resized
once with high-quality bicubic interpolation to the exact target dimensions,
without cropping. Prompts and masters are retained locally under
tutnt/.codex/work/interms-borderless/; previous hires files are backed up under
tutnt/.codex/backups/interms-borderless-20260913/.

This replaces the 8 September framed treatment only for the five named files.
Other chapter images and the separate TNTE4_2 illustration remain outside this
five-image update.

## Validation

Each exported file is decoded and checked for PNG format, RGBA mode, exact
dimensions and full opacity. The generated images were visually reviewed for
subject, style and absence of frames. Pixel data is checked against the packaged
resources after the standard integration build and engine load check.
Local results are stored in tutnt/.codex/validation/interms-borderless.json
and tutnt/.codex/logs/interms-borderless-build.log.

This is an artwork/resource check, not a full campaign playthrough.
