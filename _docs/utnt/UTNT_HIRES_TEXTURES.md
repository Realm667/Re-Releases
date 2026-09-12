# UTNT high-resolution texture artwork

Updated: 12 September 2026.

## OCOMP

- Source: `tutnt/textures/ogro/OCOMP.lmp`, 128 x 64 pixels, decoded using the first palette of `tutnt/PLAYPAL.pal`.
- Replacement: `tutnt/hires/textures/OCOMP.png`, exactly 256 x 128 pixels, opaque 8-bit RGB PNG. The original lump remains unchanged. The hires resource retains the original logical texture dimensions.
- Artwork: a faithful dark industrial computer panel with a large recessed screen on the left, a smaller upper-right display and bronze/charcoal electronic controls. Finer bevels and worn surfaces retain the source composition and palette families.
- Production: built-in Imagegen edit of the palette-decoded source, followed by Lanczos3 downsampling. Colors are inspired by the current PLAYPAL reference and allow intermediate truecolor shades; they are not restricted to 256 entries and do not track later palette changes automatically.
- Validation: original/output dimension ratio, opaque RGB PNG encoding, successful decoding, packager inclusion and visual comparison. No in-game rendering test or shared integration-package rebuild was performed for this asset-only change.

The generation prompt, full-resolution intermediate and local validation record are stored in `tutnt/.codex/work/ocomp-hires/`.

## Texture remaster batch, 12 September 2026

Local artwork, awaiting commit. 86 of 98 additional requested replacements are saved and validated; twelve transparent replacements remain pending alpha correction. OCOMP is additional to this batch.

| Set | Names | Final pixel dimensions | Status |
|---|---|---|---|
| Tombstones | GR_BOUN, GR_CUTTY, GR_DUDE, GR_ENJAY, GR_ERIAN, GR_HIRO, GR_KEKS, GR_PHOB, GR_RAND, GR_SCUBA, GR_SOLAR, GR_TDA, GR_VADER, GR_ZAHL | 96 x 128 | Saved |
| Industrial lights | IKLIGHT1, IKLIGHT4; IKLIGHT3; IKLITE2, IKLITE3 | 256 x 256; 128 x 256; 128 x 128 | Saved |
| Gothic windows | NEUESDI, NEUESDI2 | 128 x 256 | Saved |
| Metal doors | OIDOOR2, OSNOW2, QDOOR1-5, QDOOR9 | 256 x 256 | Saved |
| Computers | Q2CMP085-090, Q2COMP8-13; Q2GCMP, Q2MCMP, Q2RCMP and Q2YCMP with suffixes 8, 9, 11, 12 | 256 x 128 | Saved |
| Square computers | Q2CMP091, Q2CMP092 | 128 x 128 | Saved |
| Stained glass | QWINDOW1-5 | 128 x 384 | Saved |
| Light fades | XLIGHT-B/G/O/R/W/X/Y, YLIGHT-B/G/O/R/W/X/Y, XYELLO | 128 x 128 | Saved |
| Particle fade | YYELLO | 128 x 128 | Alpha correction pending |
| Narrow lights | ADEL_N07-10, ADEL_N30; ADEL_N24 | 64 x 256; 64 x 192 | Saved |
| Open grilles | ADEL_N25; ADEL_N26 | 64 x 192; 128 x 256 | Alpha correction pending |
| Banners | HYPO_D01-09 | 256 x 256 | Alpha correction pending |
| Glowing ornament | OLITE4 | 64 x 128 | Saved |

All final assets retain their original names under tutnt/hires/textures/. Native lumps were decoded with the first palette in tutnt/PLAYPAL.pal; existing PNG color variants retain their authored color references. IKLITE2/3 originate in flats, NEUESDI/2 in patches. Source resources remain unchanged.

Built-in Imagegen produced the artwork from individual original references. Mechanical Lanczos3 downsampling sets exactly twice the source width and height, with truecolor RGB or RGBA PNG encoding. Palette families guide the new shading; the files are not quantized to 256 colors and do not respond automatically to later PLAYPAL changes. The revised tombstone set has fourteen distinct carved front frames and varied inscription styles, preserving every name and removing RIP. Opaque light fades preserve vertical direction and smoother falloff; XYELLO retains real alpha.

The six Q2COMP8-13 originals have identical decoded pixels to Q2CMP085-090 respectively. Each pair therefore shares the same remaster bytes under both required names. Q2G colors remain gold, Q2M panel layouts retain mirrored placement with readable new labels, Q2R remains blue/cyan and Q2Y remains purple/magenta.

Local production records are in tutnt/.codex/work/texture-hires-batch/manifest.json, including exact prompts and generation paths. Per-set folders hold palette-decoded originals, generated artwork and review sheets. validation.json checks original hashes, exact doubled dimensions, truecolor encoding, transparent pixels where required and inclusion by the existing packager. Saved artwork has been visually reviewed. No in-engine rendering test or shared tutnt.pk3 rebuild was performed.


## Revised artwork, 12 September 2026

51 replacements were revised locally, retaining their existing filenames and exactly twice their original pixel dimensions:

- All fourteen GR tombstones now have individually designed sculpted front frames, distinct inscription typography and smaller subordinate skull reliefs. Every original name is retained; RIP is removed.
- IKLIGHT1 and IKLIGHT3 have uninterrupted warm ivory fluorescent tubes. Their housings, ventilation slots and separate lamp modules remain.
- NEUESDI and NEUESDI2 reinterpret their amber and amber/crimson stained glass using the existing QRUNT63 rune alphabet, with clearer leadwork and glass shading.
- QWINDOW1 through QWINDOW5 depict HECTA1, MNTRA1, BRUSA1, HWARD1 and STYRB1 respectively, translated from the supplied UTNT sprites into dark medieval glass mosaics.
- Twenty-eight rectangular Q2 computer resources have newly authored portal arrays, slipgate synchronization, OGROS steelworks, containment experiments, plasma reactors and Source research diagrams. The six Q2COMP8-13 aliases share their corresponding Q2CMP085-090 artwork. Q2CMP091 and Q2CMP092 are excluded from this revision. No LCD grid or CRT scanlines are baked into the new images. The existing runtime CRT shader is explicitly retained at the user's request.

Built-in Imagegen produced 45 unique edited images; mechanical Lanczos3 downsampling exports the final RGB PNGs. Prompts and full-resolution outputs are preserved in tutnt/.codex/work/texture-revisions/, with manifest.json recording the sprite mapping, aliases and output hashes. Previous replacements are backed up in tutnt/.codex/backups/texture-revisions-20260912/.

The scoped validation.json passes all 51 files: exact doubled width and height, truecolor RGB encoding, unchanged original hashes, identical alias bytes and packager inclusion. Artwork was visually checked at generated and final scales. No engine rendering test or shared package rebuild was performed.

A broader historical batch check encountered the unrelated ADEL_N07 replacement at 48 x 256 instead of its previous 64 x 256. The user confirmed subsequent manual ADEL edits. This revision did not modify those files; the scoped 51-file check passes. The older twelve alpha-correction tasks are separate from these revisions. Commit/push remains pending after the previously reported automatic approval rejection.


## TNT2SCHL warning sign alternatives

Four 400 x 700 RGBA designs are preserved in tutnt/.codex/work/tnt2schl-sign/: A retains the original engraved character, B uses a riveted steel/stencil layout, C uses a cast plaque with raised lettering, and D uses worn enamel with hazard stripes. Each replaces the screenshot with an OGROS STEEL ARMORY GROUNDS / NO ENTRY / TRESPASSING PROHIBITED sign.

The user selected variant B, now installed locally as tutnt/hires/graphics/interms/TNT2SCHL.png. Its riveted dark steel, worn stencil lettering and red warning panel replace the screenshot with a clear forbidden-entry sign. The 400 x 700 fully opaque RGBA PNG is byte-identical to the selected variant and included by the packager. The low-resolution original remains unchanged. No shared package rebuild or new engine rendering test was performed. The existing replacement is backed up under tutnt/.codex/backups/tnt2schl-sign-20260912/. Built-in Imagegen prompts, full-resolution images, the comparison sheet and PNG validation are recorded in the work folder's manifest.json and validation.json.
