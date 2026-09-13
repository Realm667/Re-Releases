# Basalt fortress border artwork

Updated: 13 September 2026.

The approved second design replaces the high-resolution S_BORDER and S_BORDET
frames with fractured basalt masonry, weathered bronze trim and amber runes.
S_BORDER uses the selected export unchanged. S_BORDET uses the same geometry
with RGB values multiplied by 1.5 and clipped to 255, retaining the brighter
presentation of the previous pair without transferring its old skull imagery.

Both files are 1716x960 RGBA PNGs. Their alpha channels are pixel-identical to
the previous assets, including the transparent central opening and feathered
inner edges. The original low-resolution resources and logical dimensions are
unchanged.

Validation confirmed the selected S_BORDER export byte-for-byte, both dimensions,
all original alpha values, and the S_BORDET brightness transform. The images were
visually reviewed. Local backups and validation evidence are stored in the
central UTNT workspace.

The shared tutnt.pk3 build passed its engine check, and both packaged PNGs were
verified byte-for-byte against the source files. This is a resource/build check,
not a complete playthrough of every transition.
