# Approved TNT04CN dark zenith, revision 2

The user approved `tnt04cn-dark-zenith-v2.png` and explicitly clarified that the Source beam is existing level geometry. The mockup's illustrative beam is only an alignment reference and was **not** extracted into a production texture.

`reference-preferred.png` is the user-supplied palette reference. `prompt.txt` records the mockup prompt. `production-prompts.json` contains the exact Imagegen prompts for the two final cloud-only images:

- `tutnt/graphics/rift/zenith.png`: generated `exec-5d35bc9b-781a-4d47-8dfe-afc199fbe5ba.png`.
- `tutnt/graphics/rift/dark-clouds.png`: generated `exec-8498bdb9-cc8b-4abd-bb62-2e5168f36f8e.png`.

Both were generated from the approved v2 reference with the built-in Imagegen tool and visually inspected. They contain no beam, rocks, comets, foreground, weapon or HUD. The original outputs are copied without repainting. The existing separate keyed rocks and shared animated comets are composed by the runtime material. NumPy/Pillow only perform deterministic projection to static cube faces.

Palette: dark grey, dark brown, near-black, subdued red reflections; bright light orange confined to the overhead opening. Projection, portal alignment and validation are documented in `UTNT_RIFT_SKY.md`.
