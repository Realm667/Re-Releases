# UTNT localization

UTNT ships complete English, German, Spanish and French text catalogs. Original
voice recordings, contributor names, the product title, and embedded artwork
are retained. Spanish is a shared Spanish translation; French is a shared French
translation. The engine's language setting selects the text (`en`, `de`, `es`,
`fr`; legacy `enu` and `deu` remain supported by UZDoom).

English source text lives in `tutnt/LANGUAGE.enu` and the English-only feature
files `LANGUAGE.*`. Every translated key has exactly one definition in each of
`LANGUAGE.deu`, `LANGUAGE.esp` and `LANGUAGE.fra`. These files declare both the
modern and legacy codes: `[deu de]`, `[esp es]`, `[fra fr]`. Use the engine's modern
`de`, `es`, `fr` settings so its own menus and font fallbacks are localized too.
File extensions do not select the language.

## Required workflow for every text change

1. Put new player-facing text in an English LANGUAGE entry. Use a stable key in
   ZScript, ACS, MENUDEF or MAPINFO instead of embedding the displayed sentence.
2. Add or update that key in **all three** translated catalogs in the same change.
   For changes to English meaning, review every translation even when the key
   remains the same. Remove retired keys from all four catalogs together.
3. Preserve substitution tokens (`%d`, `%%`, `%o`, `%k`, `{n}`), color escapes and
   explicit line/paragraph breaks. Obituary tokens can change order. Narrative
   fragments must read coherently when joined; preserve their trailing `\n`.
   Use UTF-8, including real accented characters and umlauts. Do not copy English
   sentences into other languages just to satisfy key coverage. Proper names and
   conventional weapon names can deliberately remain identical.
4. Review the translations and their in-game context. Check long text, narrow
   screens, class cards, chapters and subtitle line wrapping. Voice recordings
   remain original; translate the corresponding subtitle text.
5. Run `python tools/check_localization.py --accept-reviewed` **only after** that
   review. This records fingerprints of the English and translated values; it
   does not translate text, approve its meaning or fill missing keys.
6. Run `python tools/check_localization.py` and
   `python -m unittest discover -s tools -p test_localization.py`, then build with
   `tools/build_utnt.py`. For runtime validation, use
   `python tools/test_localization_runtime.py --mod tutnt.pk3` with `UTNT_ENGINE`
   and `UTNT_IWAD` set. Commit the catalogs and review manifest together.

The build validates its immutable source snapshot before compilation and
packaging. Missing, extra, duplicate, empty or malformed entries, changed
placeholders/colors/line breaks and unreviewed text changes fail the build.
The same gate runs in GitHub Actions on pushes and pull requests. Generated build
identifiers are deliberately identical in all four languages and are emitted in
four language sections by the packager. Use `--pk3 tutnt.pk3` to verify packaged
catalogs against the current source review manifest.

Automation proves structural coverage and detects unreviewed changes; linguistic
accuracy and tone still require reviewing the actual translations.

## Terminology

| English | German | Spanish | French |
| --- | --- | --- | --- |
| The Source | Die Quelle | La Fuente | La Source |
| Dark Portal | Dunkles Portal | Portal oscuro | Portail obscur |
| Tech Center | Technikzentrum | Centro técnico | Centre technique |
| Cursed Peak | Verfluchter Gipfel | Cumbre maldita | Sommet maudit |
| Edge of Chaos | Rand des Chaos | Borde del caos | Confins du chaos |
| Facility A/B | Anlage A/B | Instalación A/B | Installation A/B |
| Rage | Raserei | Furia | Rage |
| Weak Spot | Schwachstelle | Punto débil | Point faible |
| Cloak | Tarnung | Camuflaje | Camouflage |
| Overdrive | Überlastung | Sobrecarga | Surcharge |
| Bollwerk | Bollwerk | Baluarte | Bastion |

The 2026-09-10 expansion also localizes the previously literal main-menu,
episode-selection and skill names, automap statistics and authored credit headings,
contributions and navigation. Credit data stores LANGUAGE keys; each client resolves
them when drawing, so cooperative peers may use different languages. Credits layout
caches are refreshed on language changes. The remaster UI uses the engine's
`AlternativeSmallFont` for matching wrapping, measurement and drawing; this retains
the mod font where complete and uses the extended native font for accented text.
Three old malformed subtitle escape prefixes
and the missing obituary victim marker are corrected. Two English obituaries use
equivalent pronoun-free wording so translated sentences do not depend on the
English possessive/object-pronoun substitution.

## Validation of the 2026-09-10 catalog

All four languages contain 878 entries. The source and packaged-catalog gates
pass, as do 14 localization unit tests. UZDoom 5.0.1 completed 7,760 runtime
assertions across the four languages, including actual StringTable lookup, font
glyph coverage, class-card and chapter layout, and localized credit pages.
German, Spanish and French menu/card screenshots and dense French credits were
visually checked. This is targeted UI validation, not a full campaign playthrough.
Local evidence is under `tutnt/.codex/validation/localization-2026-09-10/`.
