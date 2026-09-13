"""Geometry contracts for material-aware outdoor terrain edges."""
import math,unittest
from build_terrain_edges import detect_terrain,terrain_mesh,floor_uv,floor_coord,HeightSampler
from build_sky_edges import plane

class TerrainTests(unittest.TestCase):
    def setUp(self):
        self.variants={n:dict(family=n,logical=[64,64],profile=p,depth=4,stem='unused') for n,p in [('QROCK3','rock'),('QGRASS','grass'),('SNOW3','snow'),('GROUND2','soil'),('GRAVE01','gravel'),('QBRICK6','brick')]}
    def fixture(self,upper='QGRASS',lower='QROCK3',wall='QROCK3'):
        b=dict(vertex=[dict(x=str(x),y=str(y)) for x,y in [(0,0),(256,0),(256,-256),(0,-256),(256,256),(0,256)]],
               sector=[dict(heightfloor=str(h),heightceiling='256',textureceiling='"F_SKY1"',texturefloor='"'+t+'"') for h,t in [(0,lower),(64,upper)]],
               sidedef=[dict(sector='0',texturebottom='"'+wall+'"'),dict(sector='1')],linedef=[dict(v1='0',v2='1',sidefront='0',sideback='1')])
        for sec,a,c in [(0,1,2),(0,2,3),(0,3,0),(1,0,5),(1,5,4),(1,4,1)]:
            si=len(b['sidedef']);b['sidedef'].append(dict(sector=str(sec),texturemiddle='"'+wall+'"'));b['linedef'].append(dict(v1=str(a),v2=str(c),sidefront=str(si)))
        return b
    def edge(self,b):return [e for e in detect_terrain(b,self.variants) if e['line']==0 and e['mode']==1]
    def test_floor_and_wall_materials_are_separate(self):
        body,cap=self.edge(self.fixture());self.assertEqual(body['uv']['skin'],'QROCK3');self.assertEqual(cap['uv']['skin'],'QGRASS')
        self.assertEqual(cap['kind'],'grass');self.assertEqual(body['kind'],'rock')
        _,snow=self.edge(self.fixture('SNOW3'));self.assertEqual(snow['kind'],'snow')
    def test_material_and_boundary_exclusions(self):
        self.assertFalse(self.edge(self.fixture(wall='QBRICK6')))
        self.assertFalse(self.edge(self.fixture(upper='QBRICK6')))
        for mutate in [lambda b:b['sector'][1].update(heightfloor='256'),lambda b:b['sector'][1].update(heightfloor='2'),lambda b:b['sector'][0].update(textureceiling='"CEIL5_2"'),lambda b:b['linedef'][0].update(special='156')]:
            b=self.fixture();mutate(b);self.assertFalse(self.edge(b))
    def test_low_grass_step_and_non_sky_wall_pegging(self):
        b=self.fixture();b['sector'][1]['heightfloor']='4'
        self.assertEqual(len(self.edge(b)),2)
        from build_sky_edges import wall_uv
        b=self.fixture();b['sector'][1].update(textureceiling='"CEIL5_2"',heightceiling='128')
        b['linedef'][0]['dontpegbottom']='true'
        e=dict(side=b['sidedef'][0],linedef=b['linedef'][0],front=b['sector'][0],back=b['sector'][1],part=2,texture='QROCK3',line=0,face=0)
        self.assertEqual(wall_uv(e,self.variants,{})['ref'],320)

    def test_scrolling_floors_do_not_receive_static_caps(self):
        b=self.fixture();b['sector'][1]['special']='209';self.assertFalse(self.edge(b))
        b=self.fixture();b['sector'][0]['scroll_floor_x']='.5'
        self.assertFalse(any(e['mode']==2 and e['front_id']==0 for e in detect_terrain(b,self.variants)))

    def test_layers_share_exact_seam(self):
        for surface in ['QGRASS','SNOW3','QROCK3','GROUND2','GRAVE01']:
            body,cap=self.edge(self.fixture(surface));mb=terrain_mesh(body);mc=terrain_mesh(cap)
            for a,b in zip(mb[-1][::5],mc[-1][5::6]):self.assertLess(math.dist((a[0]+mb[1][0],a[1]+mb[2],-a[2]+mb[1][1]),(b[0]+mc[1][0],b[1]+mc[2],-b[2]+mc[1][1])),1e-7)
            self.assertEqual(len(mb[-1])//5,len(mc[-1])//6)
    def test_walkable_cap_and_foot_heights_are_bounded(self):
        for e in detect_terrain(self.fixture('SNOW3'),self.variants):
            if e['layer']!=1:continue
            _,center,h,_,verts=terrain_mesh(e)
            for x,z,y in verts:
                above=z+h-plane(e['top'],(x+center[0],-y+center[1]),'floor')
                self.assertLessEqual(above,2.3 if e['mode']==2 else .66)
    def test_slope_continuity_and_finite_normals(self):
        b=self.fixture();b['sector'][1].update(floorplane_a='-.05',floorplane_b='-.02',floorplane_c='1',floorplane_d='-64')
        body,cap=self.edge(b);obj,center,h,_,verts=terrain_mesh(cap)
        for x,z,y in verts[::6]:self.assertAlmostEqual(z+h-plane(cap['top'],(x+center[0],-y+center[1]),'floor'),.045,places=6)
        for line in obj.splitlines():
            if line.startswith('vn '):self.assertAlmostEqual(math.sqrt(sum(float(x)**2 for x in line.split()[1:])),1,places=5)
    def test_floor_rotation_scaling_and_area_binding(self):
        sec=self.fixture()['sector'][1];sec.update(xpanningfloor='3',ypanningfloor='7',xscalefloor='2',yscalefloor='.5',rotationfloor='90')
        c=floor_uv(sec,1,self.variants,{})
        u,v=floor_coord(c,(16,32));self.assertAlmostEqual(u,(-32+3)*2/64);self.assertAlmostEqual(v,(-16+7)*.5/64)
        c=floor_uv(sec,1,self.variants,{1:['F','1','0','QGRASS','QGRASS','11','13','3','7']});self.assertEqual((c['ox'],c['oy']),(11,13))
    def test_heightmap_decoding_and_wrapping(self):
        from PIL import Image
        s=HeightSampler('.',self.variants);s.cache['QGRASS']=Image.new('L',(4,4),127)
        self.assertEqual(s.sample('QGRASS',(-.25,1.5)),0)
        s.cache['QGRASS'].putpixel((3,2),0)
        self.assertEqual(s.sample('QGRASS',(-.25,1.5)),s.sample('QGRASS',(.75,.5)))
        self.assertLess(s.sample('QGRASS',(.75,.5)),0)
    def test_body_heightmap_deformation_preserves_material_seam(self):
        class Sampler:
            def sample(self,skin,uv):return math.sin(uv[0]*3+uv[1]*2)
        body,cap=self.edge(self.fixture());plain=terrain_mesh(body);deformed=terrain_mesh(body,Sampler());upper=terrain_mesh(cap,Sampler())
        self.assertNotEqual(plain[-1],deformed[-1])
        for a,b in zip(deformed[-1][::5],upper[-1][5::6]):self.assertLess(math.dist((a[0]+deformed[1][0],a[1]+deformed[2],-a[2]+deformed[1][1]),(b[0]+upper[1][0],b[1]+upper[2],-b[2]+upper[1][1])),1e-7)

if __name__=='__main__':unittest.main(verbosity=2)
