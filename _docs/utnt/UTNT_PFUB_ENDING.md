# Cyberdemon ambush ending artwork

Updated: 13 September 2026.

PFUB2 (LEFT) and PFUB1 (RIGHT) form one continuous volcanic cliff panorama.
The left half shows a rear three-quarter view of the classic Cyberdemon firing
toward the Marine; its cannon replaces the forearm and hand. The single flying
rocket is entirely within the left half. The right half shows the green-armored
Marine from behind at the cliff edge, holding a lowered, smoking plasma rifle,
with fallen brown aliens on the rocks behind him.

The supplied PLAYC4C6 and CYBRF6 images define the Marine and Cyberdemon.
DGRDQ0.lmp and QUEEQ0.lmp from the game are decoded with its PLAYPAL to supply
the two corpse references. The existing plasma pickup guides the rifle design.
The commissioned scene has no caption or decorative frame.

## Export contract

Both production PNGs in tutnt/hires/graphics/interms/ are opaque RGBA at
1280 x 960, retaining the preceding hires dimensions. The original logical
resources remain unchanged. Generate one full panorama, resize it once to
2560 x 960, then split at x=1280. PFUB2 contains columns 0..1279; PFUB1 contains
1280..2559. Never independently generate or resample the two halves.

The built-in Imagegen prompts, intermediate corrections and complete exported
panorama are retained locally in tutnt/.codex/work/pfub-ending/.
Previous hires files are backed up in tutnt/.codex/backups/pfub-ending-20260913/.

## Verification

The panorama was visually checked for character orientation, integrated cannon,
rocket placement, lowered smoking plasma gun and reference alien corpses.
Concatenating PFUB2 then PFUB1 reconstructs the complete export pixel for pixel:
no missing or repeated columns and no gap or seam adjustment.
Local evidence: tutnt/.codex/validation/pfub-ending.json.

No gameplay, ending timing or scroll code is changed.
