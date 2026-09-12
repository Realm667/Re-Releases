# Original UTNT font artwork

DBIGFONT.fon2 is the original 20-pixel menu font, relocated unchanged from the
runtime root. PLAYPAL.pal holds the 256 RGB colors used to decode the original
Quake STCFN patches. The original patches remain in tutnt/graphics/fonts.

Run `python tools/build_localized_fonts.py` from the repository root to rebuild
all four complete Unicode definitions. UCRBIG uses the existing 1.8x palette
brightening; BigUpper shares the BigFont artwork. Legacy runtime FON2 files must
not be reintroduced: they take precedence over same-package Unicode folders.

The generator implements the engine's documented FON2 and Unicode-folder formats:
https://github.com/UZDoom/UZDoom/blob/master/src/common/fonts/singlelumpfont.cpp
https://github.com/UZDoom/UZDoom/blob/master/src/common/fonts/font.cpp
The supplied artwork is inherited from UTNT; no third-party replacement font was
introduced. See _docs/utnt/LOCALIZATION.md for the required translation workflow.
