"""Regressions for editable cavern geometry, model placement and source preservation."""
import collections,re,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def lumps(data):
    _,count,offset=struct.unpack_from('<4sII',data);result={}
    for i in range(count):
        start,size,name=struct.unpack_from('<II8s',data,offset+i*16);result[name.rstrip(b'\0').decode()]=data[start:start+size]
    return result
def blocks(text,kind):
    text=re.sub(r'//[^\n]*|/\*.*?\*/','',text,flags=re.S)
    return [dict(re.findall(r'(\w+)\s*=\s*([^;]+);',body)) for body in re.findall(r'\b'+kind+r'\s*\{([^}]*)\}',text)]
class AuthoredCavernTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.map=(ROOT/'tutnt/maps/tnt03a2.wad').read_bytes();text=lumps(cls.map)['TEXTMAP'].decode()
        cls.b={k:blocks(text,k) for k in ('linedef','sidedef','sector','thing')}
        cls.windows=[l for l in cls.b['linedef'] if cls.b['sidedef'][int(l['sidefront'])].get('texturemiddle')=='"UCAVFOG"']
    def test_three_blocked_translucent_windows_with_stone_sills(self):
        self.assertEqual(len(self.windows),3)
        for line in self.windows:
            self.assertEqual(line['blocking'],'true');self.assertEqual(line['twosided'],'true')
            self.assertEqual(float(line['alpha']),.5);self.assertEqual(line['wrapmidtex'],'true')
            side=self.b['sidedef'][int(line['sideback'])];pocket=self.b['sector'][int(side['sector'])]
            self.assertEqual(pocket['texturefloor'],'"UCAVROCK"');self.assertEqual(pocket['textureceiling'],'"UCAVROCK"')
    def test_three_native_portals_and_authored_cameras(self):
        self.assertEqual(sum(l.get('special')=='57' and l.get('arg1')=='5' for l in self.b['linedef']),3)
        cameras=[t for t in self.b['thing'] if t.get('type')=='25110']
        self.assertEqual(len(cameras),3);self.assertEqual({int(t['id']) for t in cameras},{65200,65201,65202})
    def test_authored_hall_and_pocket_fog(self):
        halls=[s for s in self.b['sector'] if 65300<=int(s.get('id',0))<=65302];self.assertEqual(len(halls),3)
        for s in halls:
            self.assertEqual(int(s['fadecolor']),0x1b1814);self.assertEqual(int(s['fogdensity']),24);self.assertEqual(int(s['lightlevel']),96)
        for line in self.windows:
            s=self.b['sector'][int(self.b['sidedef'][int(line['sideback'])]['sector'])]
            self.assertEqual(int(s['fadecolor']),0x363029);self.assertEqual(int(s['fogdensity']),44);self.assertEqual(int(s['lightlevel']),160)
    def test_models_are_real_editor_things_with_modeldefs(self):
        defs=(ROOT/'tutnt/mapinfo/MAPINFO.cavern').read_text();models=(ROOT/'tutnt/modeldef/MODELDEF.cavern').read_text()
        numbers={int(n):c for n,c in re.findall(r'(\d+)\s*=\s*(UTNTCavern\w+)',defs)}
        things=[t for t in self.b['thing'] if 25000<=int(t.get('type',0))<25110];self.assertEqual(len(things),102)
        for t in things:self.assertIn('Model '+numbers[int(t['type'])]+'\n',models)
        self.assertEqual(sum(t.get('type')=='25111' for t in self.b['thing']),3)
    def test_lavafall_and_rock_shells_are_closed(self):
        for name in ('lavafall','fall_cheek_a','fall_cheek_b','fall_lip'):
            text=(ROOT/f'tutnt/models/cavern/{name}.obj').read_text()
            faces=[tuple(int(v.split('/')[0]) for v in line.split()[1:]) for line in text.splitlines() if line.startswith('f ')]
            edges=collections.Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]))
            self.assertEqual(set(edges.values()),{2},name)
    def test_normal_cavern_build_preserves_authored_bytes(self):
        from build_cavern import generate
        paths=[ROOT/'tutnt/maps/tnt03a2.wad',*sorted((ROOT/'tutnt/models/cavern').glob('*.obj'))]
        before={p:p.read_bytes() for p in paths};generate(ROOT,False);generate(ROOT,True)
        self.assertEqual(before,{p:p.read_bytes() for p in paths})
if __name__=='__main__':unittest.main()
