Title: Cheello's Voxel Doom
Version: 2.4
Release date: April 2024
Engine: GZDoom 4.11.3 or higher
https://twitter.com/DanielWienerson
https://www.youtube.com/channel/UC1WkHfzyqhCMTOLCeBznygA

//===========================================================================
//
// REQUIREMENTS AND TECHNICAL NOTES
//
//===========================================================================

- GZDoom requires up to 2.2 GB of video memory (VRAM) to fully load Voxel
  Doom. A graphics card with 4 GB of VRAM is recommended.
- The software render is not supported. GZDoom will most likely just crash.
- GZDoom, by default, only loads in voxel data when an object comes into
  view. This may cause stuttering as a monster appears in your view for the
  first time. You can enable voxel precaching in the Voxel Doom Options menu
  to force the mod to preload voxels for every existing object in the map.
  Do note that this comes with a small tradeoff - entering a map will be
  delayed slightly as a result, in addition to consuming a little more VRAM.

//===========================================================================
//
// INSTALLATION
//
//===========================================================================

Place the VoxelDoom.pk3 file in your GZDoom folder. Drag the file on to
gzdoom.exe and select a WAD file to run.

It is safe to have the mod autoloaded as the contents will be filtered
properly depending on whether Doom 1 or Doom 2 is played.

Enjoy!

//===========================================================================
//
// ABOUT VOXEL DOOM
//
//===========================================================================

Voxel Doom features:

- Full support for Doom 1, Ultimate Doom, Doom 2, TNT and Plutonia!
- Voxel Doom comes with its own Actor replacements. This was necessary for
  most of its core features and is unavoidable. Compatibility with other mods
  is therefore not guaranteed.
- Killed monsters will face the player that killed them.
- Smooth rotation for monsters (optional).
- Flying monsters will adjust their pitch to face their target (optional).
- Spinning item pickups (optional).
- Colorized blood for the Cacodemon, Baron of Hell and Hell Knight.
- Render styles for some Actors have been explicitly changed due to rendering
  glitches with GZDoom. Actors affected: Spectre, Mancubus fireball, player
  invisibility powerup.
- Incorporated GZSprFix's (which, in turn, is based off Revenant100's Sprite
  Fix Project) Actor fixes concerning wrongly-lit attacking frames. Affects
  the Zombieman, Cyberdemon, Spider Mastermind, Chaingunner and Arachnotron.
- Powerup spheres will always face the camera.
- Automatically rotate the eye decorations when the mod is played with SIGIL.
- Fully voxelized Icon of Sin!

//===========================================================================
//
// CREDITS
//
//===========================================================================

Cheello's Voxel Doom
© 2021 - 2024 Daniel Peterson

All voxel models and base VOXELDEF by Cheello
ZScript code by Nash Muhandes (GPL v3.0 licensed)

Special thanks:

Nash Muhandes for consultation, beta testing, and coding help
Agustin Alvarez for various feature ideas, beta testing and additional support

MODDERS:

You may use my voxels in your own projects, as long as you give me, "Cheello"
credit.
