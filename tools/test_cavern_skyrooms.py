"""Verify that package-only cavern skyboxes preserve unrelated map data."""
import json,re,struct,unittest
from pathlib import Path
from cavern_skyrooms import apply,MARKER
ROOT=Path(__file__).resolve().parents[1]

def lumps(data):
    _,count,offset=struct.unpack_from('<4sII',data)
    result={}
    for i in range(count):
        start,size,name=struct.unpack_from('<II8s',data,offset+i*16)
        result[name.rstrip(b'\0').decode()]=data[start:start+size]
    return result

def blocks(text,kind):
    text=re.sub(r'//[^\n]*|/\*.*?\*/','',text,flags=re.S)
    return [dict(re.findall(r'(\w+)\s*=\s*([^;]+);',body)) for body in re.findall(r'\b'+kind+r'\s*\{([^}]*)\}',text)]

class SkyroomMapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/'tutnt/maps/tnt03a2.wad').read_bytes()
        cls.spec=json.loads((ROOT/'tutnt/cavern/skyrooms.json').read_text())
        cls.patched=apply(cls.source,cls.spec)
        cls.before=lumps(cls.source);cls.after=lumps(cls.patched)

    def test_scripts_and_other_lumps_preserved(self):
        for name,data in self.before.items():
            if name not in ('TEXTMAP','ZNODES','BLOCKMAP','REJECT'):self.assertEqual(self.after[name],data,name)
        self.assertNotIn('ZNODES',self.after)

    def test_original_geometry_and_things_preserved_except_three_openings(self):
        for kind in ('vertex','sector','thing','sidedef','linedef'):
            original=blocks(self.before['TEXTMAP'].decode(),kind)
            patched=blocks(self.after['TEXTMAP'].decode(),kind)
            for i,entry in enumerate(original):
                expected=entry|self.spec['changes'].get(kind,{}).get(str(i),{})
                self.assertEqual(patched[i],expected,(kind,i))
        self.assertEqual(len(self.spec['changes']['linedef']),3)
        self.assertEqual(len(self.spec['changes']['sidedef']),3)

    def test_native_portals_and_blocked_entrances(self):
        lines=blocks(self.after['TEXTMAP'].decode(),'linedef')
        things=blocks(self.after['TEXTMAP'].decode(),'thing')
        for window in self.spec['windows']:
            entrance=lines[window['line']];portal=lines[window['portal_line']]
            self.assertEqual(entrance['blocking'],'true')
            self.assertEqual(entrance['twosided'],'true')
            self.assertEqual((portal['special'],portal['arg1']),('57','5'))
            self.assertGreater(window['top']-window['bottom'],300)
        cameras=[t for t in things if t.get('type')=='9083' and 65200<=int(t.get('id',0))<=65202]
        self.assertEqual(len(cameras),3)
        self.assertEqual(len({t['id'] for t in cameras}),3)

    def test_stale_patch_rejected_without_topology_change(self):
        changed=self.source.replace(b'1920.0',b'1921.0',1)
        self.assertNotEqual(changed,self.source)
        with self.assertRaises(AssertionError):apply(changed,self.spec)

    def test_double_application_rejected(self):
        with self.assertRaises(AssertionError):apply(self.patched,self.spec)

    def test_changed_source_topology_rejected(self):
        spec=dict(self.spec,counts=dict(self.spec['counts'],vertex=1))
        with self.assertRaises(AssertionError):apply(self.source,spec)

if __name__=='__main__':unittest.main()
