# Cursed Peak sunset and distant snow — 2026-09-09

UZDoom 5.0.1, OpenGL and Vulkan: each renderer passed 20 new runtime assertions,
the rendered-pixel checks, and all 44 established Cursed Peak assertions.
The runtime snapshot contains committed project sources plus this change.

- Direct south gaze enables glare. East/north/west, roof, solid actor,
  reduced effects, day and night disable it. A2 uses a traced open-sky position.
- The rendered solar disc is within 3 pixels of the expected screen centre.
- Snow changes both cloud and mountain crops. Freeze holds both crops exactly;
  releasing freeze resumes movement. The foreground wall shows no flake leakage.
- Once the mountain hides the sun, enabling glare produces zero pixel change
  in the fixed sky crop. Storms attenuate the visible sun and its lighting.
- Both maps retain exact sector/sky fade agreement, tagged covered-sector
  lighting and clear-weather fog density, including A2 entered with weather off.
- The existing motion test retains zero mountain motion with moving clouds.

Images are unmodified Vulkan engine captures. `snow-on.png` isolates the
sky snow from foreground particles; `weather-*.png` show the combined effect.
For reproduction, run tools/test_sunset.py with --work, --engine, --iwad and
--renderer 0 or 1, then tools/check_sunset_images.py on the log prefix.
Run tools/test_cursed_sky.py and tools/check_cursed_motion.py for regression.
