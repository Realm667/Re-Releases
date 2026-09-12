"""Definition layout gates: detect silently lost modules and stale runtime tables."""
import json,tempfile,unittest
from pathlib import Path
from build_definition_tables import DIRECTORIES,generate,package_textures
class DefinitionLayoutTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name);self.mod=self.root/'tutnt';self.mod.mkdir();(self.root/'tools').mkdir()
  self.manifest={}
  for group,folder in DIRECTORIES.items():
   (self.mod/folder).mkdir(parents=True)
   (self.mod/(group+'.txt')).write_text('// entrypoint\n')
   if group in ('CVARINFO','KEYCONF','LANGUAGE','MENUDEF'):
    name=folder+'/'+group+'.base';(self.mod/name).write_text('// source\n')
    self.manifest[group+'.txt']=[name]
  (self.root/'tools/definition-layout.json').write_text(json.dumps(self.manifest))
 def test_stale_tables_are_rejected_without_overwrite(self):
  generate(self.root);p=self.mod/'language/LANGUAGE.base';p.write_text('[en]\nTEST="New";\n')
  previous=(self.mod/'LANGUAGE.txt').read_bytes()
  with self.assertRaisesRegex(ValueError,'Stale definition'):generate(self.root,True)
  self.assertEqual(previous,(self.mod/'LANGUAGE.txt').read_bytes())
  generate(self.root);self.assertIn(b'TEST="New";', (self.mod/'LANGUAGE.txt').read_bytes());generate(self.root,True)
 def test_unlisted_module_rejected(self):
  (self.mod/'language/LANGUAGE.extra').write_text('// lost text')
  with self.assertRaisesRegex(ValueError,'manifest does not match'):generate(self.root)
 def test_missing_include_rejected(self):
  (self.mod/'GLDEFS.txt').write_text('#include "gldefs/missing"')
  with self.assertRaisesRegex(ValueError,'Missing or unsafe include'):generate(self.root)
 def test_cycle_rejected(self):
  (self.mod/'GLDEFS.txt').write_text('#include "gldefs/GLDEFS.loop"')
  (self.mod/'gldefs/GLDEFS.loop').write_text('#include "GLDEFS.txt"')
  with self.assertRaisesRegex(ValueError,'Cyclic include'):generate(self.root)
 def test_unreferenced_native_module_rejected(self):
  (self.mod/'gldefs/GLDEFS.lost').write_text('// lost effect')
  with self.assertRaisesRegex(ValueError,'Unreferenced'):generate(self.root)
 def test_old_root_fragment_rejected(self):
  (self.mod/'LANGUAGE.old').write_text('// old location')
  with self.assertRaisesRegex(ValueError,'modules in root'):generate(self.root)
 def test_texture_sources_are_flattened_only_in_package(self):
  payload={'TEXTURES.txt':b'#include "textures/definitions/TEXTURES.a"\n',
   'textures/definitions/TEXTURES.a':b'Texture TEST,1,1 {}\n', 'textures/image.png':b'image'}
  result=package_textures(payload)
  self.assertEqual(result['TEXTURES.txt'],b'Texture TEST,1,1 {}\n\n')
  self.assertNotIn('textures/definitions/TEXTURES.a',result)
  self.assertIn('textures/definitions/TEXTURES.a',payload)
  self.assertEqual(result['textures/image.png'],b'image')
 def test_missing_texture_include_blocks_packaging(self):
  with self.assertRaisesRegex(ValueError,'Missing texture include'):
   package_textures({'TEXTURES.txt':b'#include "textures/definitions/missing"',
    'textures/definitions/unused':b''})
 def test_material_scan_ignores_matching_directories(self):
  import build_environment_fx as environment
  from unittest.mock import patch
  (self.mod/'GLDEFS.cache').mkdir()
  (self.mod/'TEXTURES.cache').mkdir()
  (self.mod/'GLDEFS.txt').write_text('Material Texture BASE { Shader "base" }')
  (self.mod/'gldefs/GLDEFS.test').write_text('Material Texture MOVED { Shader "moved" }')
  (self.mod/'textures/definitions/TEXTURES.test').write_text('Texture MOVED, 16, 32 { Patch "PATCH", 0, 0 }')
  with patch.object(environment,'MOD',self.mod):
   materials,textures,terrain,files=environment.material_library()
  self.assertEqual(set(materials),{'BASE','MOVED'})
  self.assertEqual(textures['MOVED'][:2],(16,32))
if __name__=='__main__':unittest.main()
