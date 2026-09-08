# Sector lighting check — 2026-09-09

The dedicated Steam fixture switches the same 125 frozen wisps from sector
light 224 to 32 and back to 224. Vulkan: eight assertions passed, all three
directions present. Captures visually confirm darkening and reillumination.
The C++ engine implementation in p_effect.cpp DVisualThinker::GetLightLevel
uses rendersector->GetSpriteLight() with AddLightLevel=false, LightLevel=-1.
The existing native Tick keeps the wisp render sector current.

Reproduce using tools/check_engine.py, this fixture, map UTNTSTM, renderer 1,
the checked package and the included console CFG. Set UTNT_fxquality=3,
UTNT_lod=2000 and UTNT_reducedfx=false. Frozen simulation keeps the same wisps
alive across lighting changes. Screenshots still animate the material shader.

OpenGL also passed all eight assertions.
