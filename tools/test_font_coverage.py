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
    def test_authored_fonts_have_double_pixels_and_original_display_metrics(self):
        data=b.outputs()
        manifest=json.loads(data['tools/font-glyphs.json'])
        original,palette,_,_=b.read_fon2(b.ROOT/'tools/font-sources/DBIGFONT.fon2')
        big=b.extend(original,palette,False)
        raw=(b.ROOT/'tools/font-sources/PLAYPAL.pal').read_bytes()
        palette=[tuple(raw[i:i+3]) for i in range(0,768,3)]
        original={int(p.stem[5:]):b.read_patch(p) for p in (b.ROOT/'tutnt/graphics/fonts').glob('STCFN*.lmp')}
        small=b.extend(original,palette,True)
        for name,font in manifest['fonts'].items():
            self.assertEqual(font['scale'],2)
            self.assertIn(b'Scale 2\n',data[f'tutnt/fonts/{name}/font.inf'])
            for code,metrics in font['glyphs'].items():
                old=(small if name=='smallfont' else big)[int(code,16)]
                for key in ('width','height','left','top'):
                    self.assertEqual(metrics[key],2*getattr(old,key),(name,code,key))
    def test_accent_colors_exclude_translucent_edge_samples(self):
        palette=[(0,0,0,8),(64,64,64,255),(128,128,128,255),(224,224,224,255)]
        reference=b.Glyph(4,1,[0,1,2,3])
        mark=b.mask(['##','##'],palette,reference,scale=2,unit=2)
        self.assertTrue(all(palette[p][3]==255 for p in mark.pixels if p>=0))
    def test_remaster_uses_original_colors_and_retains_alpha(self):
        original={65:b.Glyph(4,1,[0,1,1,2])}
        oldpal=[(12,11,10),(85,56,34),(142,81,41)]
        source={65:b.Glyph(4,1,[0,1,1,2])}
        bright=[(10,10,30,255),(150,160,240,255),(255,255,255,128)]
        remapped=b.original_color_palette(source,bright,original,oldpal)
        self.assertEqual([c[:3] for c in remapped],oldpal)
        self.assertEqual([c[3] for c in remapped],[255,255,128])
if __name__=='__main__':unittest.main()
