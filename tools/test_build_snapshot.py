"""Build safety tests using temporary fixture sources, never the live project package."""
import json,pathlib,subprocess,sys,tempfile,unittest,zipfile
from unittest.mock import patch
import build_utnt as b

class SnapshotTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='utnt-build-test-');self.addCleanup(self.temp.cleanup)
  self.root=pathlib.Path(self.temp.name);self.output=self.root/'game.pk3'
  for name,data in {'zscript.zc':b'version "5.0.0"','MAPINFO.txt':b'gameinfo {}','acs/tutnt.o':b'ACS\0',
                    'source/tutnt.acs':b'// source','graphics/example.png':b'example','tools/no.txt':b'no'}.items():
   p=self.root/'tutnt'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 def test_determinism_and_manifest(self):
  result=b.package(self.root,self.output);first=self.output.read_bytes()
  self.assertEqual(first,(b.package(self.root,self.output),self.output.read_bytes())[1])
  with zipfile.ZipFile(self.output) as z:
   info=json.loads(z.read('UTNTBLD'));self.assertEqual(info['build_id'],result['build_id'])
   self.assertNotIn('source/tutnt.acs',z.namelist());self.assertNotIn('tools/no.txt',z.namelist())
   self.assertIn(result['build_id'].encode(),z.read('LANGUAGE.zzbuild'))
   for name,digest in info['files'].items():self.assertEqual(b.hashlib.sha256(z.read(name)).hexdigest(),digest)
 def test_mutation_preserves_old_package(self):
  self.output.write_bytes(b'old package')
  with b.snapshot(self.root) as (source,hashes,metadata):
   (self.root/'tutnt/zscript.zc').write_text('changed')
   self.assertEqual((source/'tutnt/zscript.zc').read_bytes(),b'version "5.0.0"')
   with self.assertRaisesRegex(RuntimeError,'changed during build'):
    b.publish_snapshot(source,self.root,self.output,hashes,metadata)
  self.assertEqual(self.output.read_bytes(),b'old package')
 def test_added_source_is_detected(self):
  with b.snapshot(self.root) as (source,hashes,metadata):
   (self.root/'tutnt/new.txt').write_text('new asset')
   with self.assertRaisesRegex(RuntimeError,'changed during build'):
    b.publish_snapshot(source,self.root,self.output,hashes,metadata)
  self.assertFalse(self.output.exists())
 def test_engine_failure_preserves_old_package(self):
  self.output.write_bytes(b'old package')
  with patch('check_engine.run_case',return_value={'ok':False,'log':'fixture.log'}):
   with self.assertRaisesRegex(RuntimeError,'Engine rejected'):
    b.package(self.root,self.output,'fixture.exe','fixture.wad')
  self.assertEqual(self.output.read_bytes(),b'old package')
 def test_os_lock_across_processes(self):
  script='from build_utnt import BuildLock;import pathlib,sys\nwith BuildLock(pathlib.Path(sys.argv[1])): print("acquired")'
  with b.BuildLock(self.output):
   child=subprocess.run([sys.executable,'-c',script,str(self.output)],cwd=pathlib.Path(b.__file__).parent,capture_output=True)
   self.assertNotEqual(child.returncode,0);self.assertIn(b'Another build owns',child.stderr)
  child=subprocess.run([sys.executable,'-c',script,str(self.output)],cwd=pathlib.Path(b.__file__).parent,capture_output=True)
  self.assertEqual(child.returncode,0,child.stderr)
 def test_reserved_metadata_cannot_be_overridden(self):
  (self.root/'tutnt/UTNTBLD').write_text('foreign manifest')
  with self.assertRaisesRegex(RuntimeError,'reserved'):b.package(self.root,self.output)
 def test_compiler_writes_only_snapshot(self):
  before=b.source_hashes(self.root)
  with b.snapshot(self.root) as (source,hashes,metadata):
   (source/'tutnt/acs/tutnt.o').write_bytes(b'compiled')
   b.publish_snapshot(source,self.root,self.output,hashes,metadata)
  self.assertEqual(before,b.source_hashes(self.root))
  with zipfile.ZipFile(self.output) as z:self.assertEqual(z.read('acs/tutnt.o'),b'compiled')

if __name__=='__main__': unittest.main(verbosity=2)
