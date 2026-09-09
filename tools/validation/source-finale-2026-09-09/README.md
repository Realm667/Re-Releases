# Source finale - runtime evidence

Direct UZDoom 5.0.1 captures from the isolated tested package. Both OpenGL and
Vulkan exercise the living encounter, save/load, all defeat stages, the empty
centre, and the actual BOSSHP-driven level exit after two seconds of stillness.
Two local cooperative peers use opposing effect settings and share the same
defeat clock. Static comparison preserves map geometry, living monster states,
damage, guardian spawning and attack scheduling. These automated runs do not
replace a full manual campaign playthrough or subjective listening review.

The five phases occupy tics 1-34, 35-104, 105-157, 158-192 and 193-244.
Tic 245 leaves the centre empty and completes the objective; tic 315 permits
the original destination transition. Lightning is decorative and consumes no
gameplay RNG. The dedicated seven-second sound is generated deterministically
by tools/build_source_audio.py and seeks to the saved phase after load.
