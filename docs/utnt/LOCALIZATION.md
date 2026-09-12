# UTNT localization

UTNT ships complete English, German, Spanish and French text catalogs. Original
voice recordings, contributor names, the product title, and embedded artwork
are retained. Spanish is a shared Spanish translation; French is a shared French
translation. The engine's language setting selects the text (`en`, `de`, `es`,
`fr`; legacy `enu` and `deu` remain supported by UZDoom).

English source text lives in `tutnt/language/LANGUAGE.enu` and the English-only feature
files `language/LANGUAGE.*`. Every translated key has exactly one definition in each of
`language/LANGUAGE.deu`, `language/LANGUAGE.esp` and `language/LANGUAGE.fra`. These files declare both the
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
6. Run `python tools/build_definition_tables.py` to refresh the engine-readable
   root tables, then `python tools/check_localization.py` and
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
caches are refreshed on language changes. The remaster UI uses the mod's own complete Unicode bitmap fonts. `SmallFont`
retains the original Quake glyphs; `BigFont`/`BigUpper` retain the original menu
artwork and `UCRBIG` its brighter credit palette. Missing accents, umlauts, sharp S,
ligatures and punctuation are explicitly drawn in the same style. No alternate
font is selected for these four languages. SmallFont has an eleven-pixel line
height to leave space above its original seven-pixel caps for diacritics; credit
cards retain their original cap scaling and explicit line spacing.
Three old malformed subtitle escape prefixes
and the missing obituary victim marker are corrected. Two English obituaries use
equivalent pronoun-free wording so translated sentences do not depend on the
English possessive/object-pronoun substitution.

## Validation of the 2026-09-10 catalog

The initial translation expansion contained 878 entries per language. Its source
and packaged-catalog gates passed, as did 14 localization unit tests. UZDoom 5.0.1 completed 7,760 runtime
assertions across the four languages, including actual StringTable lookup, font
glyph coverage, class-card and chapter layout, and localized credit pages.
German, Spanish and French menu/card screenshots and dense French credits were
visually checked. This is targeted UI validation, not a full campaign playthrough.
Local evidence is under `tutnt/.codex/validation/localization-2026-09-10/`.

## Maintaining native glyph coverage

Every new character must exist in all four font definitions, including uppercase
variants used in headings. `check_localization.py` and `build_utnt.py` now also run
`check_font_coverage.py`; missing, blank or modified glyphs fail the gate. This
checks actual packaged PNGs as well as source files, including punctuation that
an engine CanPrint check alone can silently substitute.

The original menu font and small-font palette are retained in
`tools/font-sources/`. Original small glyphs remain in `tutnt/graphics/fonts/`.
Edit `tools/build_localized_fonts.py` to author additional native glyphs, run it,
review the output in game, and commit the generated `tutnt/fonts/` images and
`tools/font-glyphs.json` together. The generator uses no operating-system font or
external font family. `python tools/build_localized_fonts.py --check` proves the
checked-in output matches its sources; CI runs it and the glyph regression tests.
Do not introduce AlternativeSmallFont/AlternativeBigFont in player UI to conceal
missing artwork. Runtime tests compare every glyph's actual width, height and
offset and verify that the engine itself chooses the complete mod fonts in en,
de, es and fr. Local runtime evidence: `.codex/validation/font-glyphs-2026-09-10/`
under `tutnt/`.

The native-font update passed 10,552 engine assertions across all four languages,
39 credit/save/load/finale assertions, eight glyph regression tests and the
existing localization and build-snapshot test suites. Screenshots of the final
accents, quotes, class cards and dense credits were visually checked.
