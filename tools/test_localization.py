"""Regression tests for the build's localization gate; no engine required."""
import json
from pathlib import Path
import tempfile
import unittest
from check_localization import parse, validate

class LocalizationGateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'tutnt').mkdir();(self.root/'tools').mkdir()
        for language in ('enu default','deu','es','fr'):
            (self.root/'tutnt'/('LANGUAGE.'+language[:2])).write_text(
                '['+language+']\nKEY = "\\c[Red]Value %d {n}\\n";\n',encoding='utf-8')
        validate(self.root,accept_reviewed=True)
    def change(self,language,text):
        path=self.root/'tutnt'/('LANGUAGE.'+language)
        path.write_text(text,encoding='utf-8')
    def test_complete(self): self.assertEqual(validate(self.root)['languages']['fr'],1)
    def test_missing_translation(self):
        self.change('fr','[fr]\n')
        with self.assertRaisesRegex(ValueError,'missing keys'):validate(self.root)
    def test_empty_translation(self):
        self.change('es','[es]\nKEY="";')
        with self.assertRaisesRegex(ValueError,'empty value'):validate(self.root)
    def test_placeholder_loss(self):
        self.change('es','[es]\nKEY="\\c[Red]Texto {n}\\n";')
        with self.assertRaisesRegex(ValueError,'placeholder mismatch'):validate(self.root)
    def test_color_loss(self):
        self.change('es','[es]\nKEY="Texto %d {n}\\n";')
        with self.assertRaisesRegex(ValueError,'color-code mismatch'):validate(self.root)
    def test_stale_translation_review(self):
        self.change('en','[enu default]\nKEY="\\c[Red]Changed %d {n}\\n";')
        with self.assertRaisesRegex(ValueError,'review required'):validate(self.root)
    def test_duplicate_across_files(self):
        self.change('extra','[fr]\nKEY="duplicate";')
        with self.assertRaisesRegex(ValueError,'duplicate'):validate(self.root)
    def test_concatenated_strings_and_comments(self):
        self.assertEqual(parse('[enu default] /* hi */ KEY="a"\n"b"; // end')['en']['KEY'],'ab')
    def test_malformed_syntax(self):
        with self.assertRaises(ValueError):parse('[fr] KEY="missing semicolon"')
    def test_orphan(self):
        self.change('extra','[fr]\nORPHAN="Texte";')
        with self.assertRaisesRegex(ValueError,'orphan keys'):validate(self.root)
    def test_unknown_escape(self):
        self.change('fr','[fr]\nKEY="\\q %d {n}\\n";')
        with self.assertRaisesRegex(ValueError,'unknown escape'):validate(self.root)
    def test_missing_referenced_key(self):
        (self.root/'tutnt/MENUDEF.txt').write_text('Title "$UTNT_MISSING";')
        with self.assertRaisesRegex(ValueError,'undefined localization key'):validate(self.root)
    def test_credit_literal_rejected(self):
        (self.root/'tutnt/credits').mkdir()
        (self.root/'tutnt/credits/original.txt').write_text('P|opening|1|10|Untranslated title\n')
        with self.assertRaisesRegex(ValueError,'credit text must reference'):validate(self.root)

    def test_ignored_work_tree(self):
        hidden=self.root/'tutnt/.codex/work/credits'
        hidden.mkdir(parents=True)
        (hidden/'original.txt').write_text('P|opening|1|10|Historical untranslated title')
        self.assertTrue(validate(self.root)['reviewed'])

if __name__=='__main__':unittest.main()
