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
 def test_duplicate_native_include_rejected(self):
  (self.mod/'GLDEFS.txt').write_text('#include "gldefs/GLDEFS.a"\n#include "gldefs/GLDEFS.a"')
  (self.mod/'gldefs/GLDEFS.a').write_text('// one module')
  with self.assertRaisesRegex(ValueError,'Duplicate native include'):generate(self.root)
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
 def test_runtime_aliases_follow_editor_stop_marker(self):
  runtime='textures/definitions/TEXTURES.environment-generated'
  authored='textures/definitions/TEXTURES.authored'
  sky='textures/definitions/TEXTURES.sky-edges'
  payload={'TEXTURES.txt':f'#include "{runtime}"\n#include "{authored}"\n#include "{sky}"\n'.encode(),
   sky:b'Texture SG000001,1,1 {}\n',runtime:b'Texture EV000001,1,1 {}\n',authored:b'Texture MAPWALL,1,1 {}\n'}
  original=payload.copy();out=package_textures(payload)['TEXTURES.txt'].decode()
  visible,hidden=out.split('//$GZDB_SKIP')
  self.assertIn('MAPWALL',visible);self.assertNotIn('EV000001',visible)
  self.assertIn('SG000001',hidden);self.assertNotIn('SG000001',visible)
  self.assertIn('EV000001',hidden);self.assertNotIn('MAPWALL',hidden)
  self.assertEqual(payload,original)
 def test_missing_texture_include_blocks_packaging(self):
  with self.assertRaisesRegex(ValueError,'Missing texture include'):
   package_textures({'TEXTURES.txt':b'#include "textures/definitions/missing"',
    'textures/definitions/unused':b''})
 def test_generated_texture_table_preserves_package_and_editor_materials(self):
  from build_definition_tables import TEXTURE_SOURCE, TEXTURE_HEADER
  base=self.mod/TEXTURE_SOURCE
  authored='textures/definitions/TEXTURES.cavern'
  runtime='textures/definitions/TEXTURES.environment-generated'
  base.write_text(f'#include "{runtime}"\nTexture ORIGINAL,1,1 {{}}\n#include "{authored}"\n')
  (self.mod/authored).write_text('Texture UCAVROCK,1,1 {}\nTexture UCAVFALL,1,1 {}\n')
  (self.mod/runtime).write_text('Texture EV000001,1,1 {}\n')
  generate(self.root);generate(self.root,True)
  payload={p.relative_to(self.mod).as_posix():p.read_bytes() for p in [base,self.mod/authored,self.mod/runtime,self.mod/'TEXTURES.txt']}
  text=payload['TEXTURES.txt'].decode();visible,hidden=text.split('//$GZDB_SKIP')
  self.assertIn('UCAVROCK',visible);self.assertIn('UCAVFALL',visible)
  self.assertIn('EV000001',hidden);self.assertNotIn('#include',visible)
  self.assertEqual(package_textures(payload)['TEXTURES.txt'],payload['TEXTURES.txt'])
  # Hand-editing a final table cannot silently diverge from its authoring modules.
  (self.mod/authored).write_text('Texture UCAVROCK,2,2 {}')
  with self.assertRaisesRegex(ValueError,'Stale definition'):generate(self.root,True)
  payload[authored]=(self.mod/authored).read_bytes()
  with self.assertRaisesRegex(ValueError,'Stale TEXTURES'):package_textures(payload)
 def test_generated_texture_entry_keeps_native_include_validation(self):
  from build_definition_tables import TEXTURE_SOURCE
  (self.mod/TEXTURE_SOURCE).write_text('#include "textures/definitions/missing"')
  with self.assertRaisesRegex(ValueError,'Missing texture include'):generate(self.root)
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
