"""Geometry/rule tests; run without the engine or graphics dependencies."""
import copy,math,struct,tempfile,unittest
from pathlib import Path
from build_lava_lips import detect,mesh,profile,parse,generate

def fixture():
    return {'vertex':[dict(x=-64,y=0),dict(x=64,y=0)],
        'sector':[dict(heightfloor=0,texturefloor='"QLAVA"'),dict(heightfloor=-128,texturefloor='"RROCK05"')],
        'sidedef':[dict(sector=0),dict(sector=1,texturebottom='"LAVA"')],
        'linedef':[dict(v1=0,v2=1,sidefront=0,sideback=1)]}

class LavaLips(unittest.TestCase):
    def test_qualified_lower_wall(self):
        b=fixture();e=detect(b);self.assertEqual(len(e),1)
        self.assertEqual(e[0]['face'],1);self.assertEqual(e[0]['high'],0)
        self.assertEqual(e[0]['normal'],(0,1))
    def test_no_false_matches(self):
        for change in ['floor','fall','upper','height','onesided']:
            b=fixture()
            if change=='floor':b['sector'][0]['texturefloor']='QWATER1'
            if change=='fall':b['sidedef'][1]['texturebottom']='BSTONE1'
            if change=='upper':b['sidedef'][1]['texturetop']='LAVA';del b['sidedef'][1]['texturebottom']
            if change=='height':b['sector'][1]['heightfloor']=64
            if change=='onesided':del b['linedef'][0]['sideback']
            self.assertEqual(detect(b),[],change)
    def test_all_material_variants(self):
        for floor in ['QLAVA','QLAVA2','QLAVASB']:
            for fall in ['LAVA','LAVAHR']:
                b=fixture();b['sector'][0]['texturefloor']=floor;b['sidedef'][1]['texturebottom']=fall
                self.assertEqual(len(detect(b)),1)
    def test_reversed_linedef(self):
        b=fixture();before=detect(b)[0]
        b['linedef'][0].update(v1=1,v2=0,sidefront=1,sideback=0)
        after=detect(b)[0]
        for key in ['a','b','normal','high','low']:self.assertEqual(before[key],after[key])
    def test_shallow_drop_scales_radius(self):
        b=fixture();b['sector'][1]['heightfloor']=-16
        self.assertEqual(detect(b)[0]['radius'],1)
    def test_round_surface_encloses_old_corner(self):
        points=profile(4)
        # At the old sharp x=0 corner the cap is above z=0, so the old
        # silhouette cannot poke through the replacement render surface.
        for a,b in zip(points,points[1:]):
            if a[0]<=0<=b[0]:
                z=a[1]+(b[1]-a[1])*(-a[0])/(b[0]-a[0])
                self.assertGreater(z,2.5)
        self.assertAlmostEqual(points[0][1],0.035)
        self.assertAlmostEqual(points[-1][0],0.035)
        self.assertTrue(all(b[2]>a[2] for a,b in zip(points,points[1:])))
    def test_miter_connects_diagonal_segments(self):
        b=fixture();b['vertex'].append(dict(x=128,y=64))
        b['linedef'].append(dict(v1=1,v2=2,sidefront=0,sideback=1))
        edges=detect(b);a,c=edges
        self.assertEqual(a['ma'],c['mb'])
        for d,_,_ in profile(4):
            pa=tuple(a['a'][i]+a['ma'][i]*d for i in range(2))
            pc=tuple(c['b'][i]+c['mb'][i]*d for i in range(2))
            self.assertEqual(pa,pc)
    def test_render_mesh_finite_and_no_source_mutation(self):
        b=fixture();original=copy.deepcopy(b);e=detect(b)[0]
        data,center,h,triangles=mesh(e)
        self.assertGreater(triangles,20);self.assertNotIn('nan',data);self.assertEqual(b,original)
    def test_sloped_drop_uses_both_endpoints(self):
        b=fixture();b['sector'][0].update(floorplane_a=1,floorplane_b=0,floorplane_c=1,floorplane_d=0)
        e=detect(b)[0];self.assertNotEqual(e['h0'],e['h1'])
        b['sector'][1]['heightfloor']=-32
        self.assertEqual(detect(b),[])
    def test_rebuild_removes_only_owned_obsolete_geometry(self):
        with tempfile.TemporaryDirectory(prefix='lava-lip-test-') as temp:
            root=Path(temp);(root/'tutnt/maps').mkdir(parents=True);(root/'tutnt/shaders').mkdir()
            for name in ['lava-surface.fp','lava-fall.fp']:
                (root/'tutnt/shaders'/name).write_text('float LavaFarVisibility;\nvoid SetupMaterial(inout Material mat) {}\n')
            def write_map(floor):
                b=fixture();b['sector'][0]['texturefloor']='"'+floor+'"'
                text='namespace="zdoom";\n'
                for kind,items in b.items():
                    for item in items:text+=kind+' { '+' '.join(f'{k}={v};' for k,v in item.items())+' }\n'
                data=text.encode();body=struct.pack('<4sII',b'PWAD',3,12+len(data))+data
                (root/'tutnt/maps/test.wad').write_bytes(body+struct.pack('<II8s',12,0,b'TEST')+struct.pack('<II8s',12,len(data),b'TEXTMAP')+struct.pack('<II8s',12+len(data),0,b'ENDMAP'))
            write_map('QLAVA');self.assertEqual(generate(root)['edges'],1)
            manual=root/'tutnt/models/lava-lips/manual.obj';manual.write_text('unrelated user file')
            self.assertEqual(generate(root,check=True)['updated'],0)
            write_map('QWATER1')
            with self.assertRaises(RuntimeError):generate(root,check=True)
            self.assertEqual(generate(root)['edges'],0)
            self.assertFalse((root/'tutnt/lavalips/test.txt').exists())
            self.assertEqual(list((root/'tutnt/models/lava-lips').glob('*.obj')),[manual])
            self.assertEqual(manual.read_text(),'unrelated user file')

if __name__=='__main__':unittest.main()
