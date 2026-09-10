"""Regression tests for authored native glyphs and missing-character build failures."""
from pathlib import Path
import hashlib,json,shutil,tempfile,unittest
from unittest.mock import patch
import build_localized_fonts as b
import check_font_coverage as c
class FontTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='utnt-font-tests-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'tools').mkdir()
        shutil.copytree(b.ROOT/'tutnt/fonts',self.root/'tutnt/fonts')
        shutil.copyfile(b.ROOT/'tools/font-glyphs.json',self.root/'tools/font-glyphs.json')
        self.catalog=patch.object(c,'catalogs',return_value={'de':{'sample':'Ärger, Größe!'}})
        self.catalog.start();self.addCleanup(self.catalog.stop)
    def test_complete_native_fonts(self):
        self.assertEqual(set(c.validate(self.root)['fonts']),set(c.FONTS))
    def test_missing_punctuation_is_rejected(self):
        (self.root/'tutnt/fonts/smallfont/0021.png').unlink()
        with self.assertRaisesRegex(ValueError,'0021'):c.validate(self.root)
    def test_new_translated_character_requires_artwork(self):
        c.catalogs.return_value={'fr':{'new':'test Ω'}}
        with self.assertRaisesRegex(ValueError,r'U\+03A9'):c.validate(self.root)
    def test_modified_glyph_is_rejected(self):
        (self.root/'tutnt/fonts/ucrbig/00D6.png').write_bytes(b'wrong image')
        with self.assertRaisesRegex(ValueError,'00D6'):c.validate(self.root)
    def test_blank_glyph_cannot_satisfy_coverage(self):
        manifest=json.loads((self.root/'tools/font-glyphs.json').read_text());entry=manifest['fonts']['smallfont']['glyphs']['00C4']
        data=b.png(b.Glyph(entry['width'],entry['height'],[-1]*(entry['width']*entry['height'])),[(0,0,0)])
        entry['sha256']=hashlib.sha256(data).hexdigest()
        (self.root/'tools/font-glyphs.json').write_text(json.dumps(manifest))
        (self.root/'tutnt/fonts/smallfont/00C4.png').write_bytes(data)
        with self.assertRaisesRegex(ValueError,'blank glyph'):c.validate(self.root)
    def test_alternate_font_is_rejected(self):
        path=self.root/'tutnt/fonts/smallfont/font.inf';path.write_text(path.read_text()+'\nAltfont "fallback"\n')
        with self.assertRaisesRegex(ValueError,'forbidden fallback'):c.validate(self.root)
    def test_original_letters_and_metrics_are_preserved(self):
        original,palette,height,kern=b.read_fon2(b.ROOT/'tools/font-sources/DBIGFONT.fon2')
        extended=b.extend(original,palette,False)
        for code in range(33,91):self.assertEqual(extended[code],original[code])
        raw=(b.ROOT/'tools/font-sources/PLAYPAL.pal').read_bytes();palette=[tuple(raw[i:i+3]) for i in range(0,768,3)]
        small={int(p.stem[5:]):b.read_patch(p) for p in (b.ROOT/'tutnt/graphics/fonts').glob('STCFN*.lmp')}
        extended=b.extend(small,palette,True)
        for code in range(33,91):self.assertEqual(extended[code],small[code])
        self.assertNotEqual(extended[ord('Ä')],extended[ord('A')])
        self.assertEqual(extended[ord('Ä')].width,extended[ord('A')].width)
    def test_quotes_stay_at_correct_vertical_positions(self):
        original,palette,_,_=b.read_fon2(b.ROOT/'tools/font-sources/DBIGFONT.fon2');g=b.extend(original,palette,False)
        self.assertLess(b.bounds(g[ord('“')])[1],b.bounds(g[ord('„')])[1])
        self.assertEqual(g[ord('“')].top,g[ord('„')].top)
if __name__=='__main__':unittest.main()
