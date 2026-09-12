"""Structural and in-engine regression for generated sky cornices.
All transient products are stored under tutnt/.codex.
"""
from pathlib import Path
import argparse, collections, json, math, sys, unittest
from build_sky_edges import detect, mesh, generate, mapping, resolve_slopes, plane, ROOT
from build_lava_lips import parse

class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.variants={name:dict(family=name,logical=[128,128]) for name in ['QROCK3','ICEY','SNOW3','QBRICK6']}
    def fixture(self,texture='QROCK3',sky=True,back=None):
        b=dict(vertex=[dict(x='0',y='0'),dict(x='256',y='0'),dict(x='448',y='96')],
               sector=[dict(heightfloor='0',heightceiling='256',textureceiling='"F_SKY1"' if sky else '"CEIL5_2"')],
               sidedef=[dict(sector='0',texturemiddle='"'+texture+'"') for _ in range(2)],
               linedef=[dict(v1='0',v2='1',sidefront='0'),dict(v1='1',v2='2',sidefront='1')])
        if back is not None:
            b['sector'].append(dict(heightfloor=str(back),heightceiling='256',textureceiling='"F_SKY1"'))
            b['sidedef'].append(dict(sector='1'));b['linedef'][0]['sideback']='2'
            b['sidedef'][0]['texturebottom']='"'+texture+'"'
        return b
    def test_material_and_actual_sky_boundary(self):
        self.assertEqual(len(detect(self.fixture(),self.variants)),2)
        self.assertFalse(detect(self.fixture(sky=False),self.variants))
        self.assertFalse(detect(self.fixture('QBRICK6'),self.variants))
        self.assertEqual(len(detect(self.fixture(back=128),self.variants)),1)
        self.assertEqual(len(detect(self.fixture(back=256),self.variants)),2)
        self.assertEqual({e['kind'] for e in detect(self.fixture('ICEY'),self.variants)},{'snow'})
    def test_upper_sky_wall_and_pegging(self):
        b=self.fixture('ICEY',back=0)
        b['sector'][1].update(heightceiling='232',textureceiling='"SNOW3"')
        b['sidedef'][0]['texturetop']='"ICEY"'
        edge=next(e for e in detect(b,self.variants) if e['line']==0)
        self.assertEqual(edge['part'],0);self.assertEqual(edge['top_id'],0)
        self.assertEqual(edge['uv']['ref'],360)
        _,_,_,_,vertices=mesh(edge)
        self.assertGreaterEqual(min(v[1] for v in vertices),-24)
        b['linedef'][0]['dontpegtop']='true'
        self.assertEqual(detect(b,self.variants)[0]['uv']['ref'],256)
        b['sector'][1]['textureceiling']='"F_SKY1"'
        self.assertFalse(any(e['part']==0 for e in detect(b,self.variants)))
        b['sector'][1].update(textureceiling='"SNOW3"',heightceiling='252')
        self.assertFalse(any(e['part']==0 for e in detect(b,self.variants)))

    def test_rock_crest_is_taller_than_snow(self):
        rock=mesh(detect(self.fixture('QROCK3'),self.variants)[0])
        snow=mesh(detect(self.fixture('ICEY'),self.variants)[0])
        self.assertGreater(max(v[1] for v in rock[-1]),max(v[1] for v in snow[-1])*1.2)

    def test_authored_slope_alignment(self):
        b=self.fixture(back=256)
        b['linedef'][0].update(special='181',arg1='1')
        b['sector'][1]['heightceiling']='128'
        resolve_slopes(b)
        self.assertAlmostEqual(plane(b['sector'][0],(0,0)),128)
        self.assertAlmostEqual(plane(b['sector'][0],(448,96)),256)

    def test_vulkan_include_identifiers(self):
        # UZDoom's Vulkan include guard replaces slashes and dots, but not
        # hyphens. OpenGL accepts the same paths, hiding this portability bug.
        import re
        for shader in (ROOT/'tutnt/shaders/sky-edges').glob('*.fp'):
            for include in re.findall(r'#include "([^"]+)"',shader.read_text()):
                guard=re.sub(r'[/\\.]','_',include)
                self.assertRegex(guard,r'^[A-Za-z_][A-Za-z_0-9]*$')
                self.assertTrue((ROOT/'tutnt'/include).is_file())

    def test_reversed_linedef(self):
        a=detect(self.fixture(),self.variants)[0];b=self.fixture();l=b['linedef'][0]
        l['v1'],l['v2']=l['v2'],l['v1'];l['sideback']=l.pop('sidefront')
        e=detect(b,self.variants)[0]
        self.assertEqual(a['a'],e['a']);self.assertEqual(a['normal'],e['normal'])
    def test_joined_mesh_seams_and_outward_silhouette(self):
        for texture in ['QROCK3','ICEY']:
            a,b=detect(self.fixture(texture),self.variants)
            ma,ca,ha,_,va=mesh(a);mb,cb,hb,_,vb=mesh(b)
            count=28 if texture=='ICEY' else 10
            def world(v,c,h):return(v[0]+c[0],-v[2]+c[1],v[1]+h)
            for v,w in zip(va[-count:],vb[:count]):
                self.assertLess(math.dist(world(v,ca,ha),world(w,cb,hb)),1e-5)
            self.assertGreater(max(v[1] for v in va),2)
            self.assertTrue(all(math.isfinite(n) for v in va for n in v))
            self.assertGreater(max(-world(v,ca,ha)[1] for v in va),5)
    def test_horizon_and_short_wall_excluded(self):
        b=self.fixture();b['linedef'][0]['special']='9'
        self.assertEqual(len(detect(b,self.variants)),1)
        b=self.fixture();b['sector'][0]['heightfloor']='240'
        self.assertFalse(detect(b,self.variants))

def runtime(root,engine,iwad,mod,mapname,renderer,packaged=False,label_suffix="",line=None):
    from check_engine import run_case
    manifest=json.loads((root/'tools/sky-edges-manifest.json').read_text())['edges']
    selected=[e for e in manifest if e['map']==mapname]
    # Long edge keeps the reference camera far from a junction. TNT02 line 4
    # is a known outdoor rock wall; other maps use their longest actual rim.
    selected.sort(key=lambda e:math.dist(e['a'],e['b']),reverse=True)
    e=next((x for x in selected if mapname=='TNT02' and x['line']==4),selected[0])
    if line is not None:e=next(x for x in selected if x['line']==line)
    ax,ay=e['a'];bx,by=e['b'];length=math.hypot(bx-ax,by-ay)
    nx,ny=(by-ay)/length,-(bx-ax)/length;mx,my=(ax+bx)*.5,(ay+by)*.5
    z=(e['h0']+e['h1'])*.5;yaw=math.degrees(math.atan2(-ny,-nx))
    addon=root/('tutnt/.codex/work/sky-edges/runtime-packaged' if packaged else 'tutnt/.codex/work/sky-edges/runtime');addon.mkdir(parents=True,exist_ok=True)
    if not packaged:
        import shutil
        for rel in json.loads((root/'tools/sky-edges-outputs.json').read_text()):
            if rel.startswith('tutnt/') and not rel.startswith('tutnt/textures/definitions/'):
                target=addon/rel.removeprefix('tutnt/');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,target)
        (addon/'shaders/skyedges').mkdir(parents=True,exist_ok=True)
        (addon/'shaders/skyedges/ceiling_glow.glsl').write_bytes((root/'tutnt/shaders/skyedges/ceiling_glow.glsl').read_bytes())
        (addon/'ANIMDEFS').write_text('canvastexture USKYGLOW 256 256\n')
        (addon/'GLDEFS.txt').write_text('#include "gldefs/GLDEFS.sky-edges"\n')
        (addon/'TEXTURES.txt').write_bytes((root/'tutnt/textures/definitions/TEXTURES.sky-edges').read_bytes())
        (addon/'MODELDEF.txt').write_text('#include "modeldef/MODELDEF.sky-edges"\n')
        (addon/'zscript').mkdir(exist_ok=True)
        (addon/'zscript/UTNT_SkyEdges.zc').write_bytes((root/'tutnt/zscript/UTNT_SkyEdges.zc').read_bytes())
    (addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTSkyEdgeTest" }\n')
    (addon/'ZSCRIPT.test').write_text('''version "5.0.0"
class UTNTSkyEdgeTest : EventHandler
{
    Actor Cam;
    int View;
    Array<Color> GlowColors;Array<double> GlowHeights;
    override void WorldTick()
    {
        if(level.time<10)return;
        if(!Cam)Cam=Actor.Spawn("MapSpot",(0,0,0));
        double distance=View==0?180:View==1?90:320;
        double along=View==2?-200:0;
        if(View==2)distance=180;
        Cam.SetOrigin((MX+NX*distance-NY*along,MY+NY*distance+NX*along,TOP-(View==1?48:100)),false);
        Cam.Angle=YAW-(View==2?48:0);Cam.Pitch=View==1?-14:-12;players[0].camera=Cam;
    }
    override void NetworkProcess(ConsoleEvent e)
    {
        if(e.Name=="skyedgeview")View=e.Args[0];
        if(e.Name=="skyedgeglow")
        {
            bool restored=true;
            for(int i=0;i<level.Sectors.Size();i++)
            {
                let s=level.Sectors[i];
                if(e.Args[0]==1) { GlowColors.Push(s.GetGlowColor(Sector.ceiling));GlowHeights.Push(s.GetGlowHeight(Sector.ceiling)); }
                s.SetGlowColor(Sector.ceiling,e.Args[0]==1?Color(255,64,16):e.Args[0]==2?Color(-1):GlowColors[i]);
                s.SetGlowHeight(Sector.ceiling,e.Args[0]==0?GlowHeights[i]:192);
                if(e.Args[0]==0)restored=restored && s.GetGlowColor(Sector.ceiling)==GlowColors[i] && s.GetGlowHeight(Sector.ceiling)==GlowHeights[i];
            }
            if(e.Args[0]==0)Console.Printf("UTNT_ASSERT %s live ceiling glow restoration",restored?"PASS":"FAIL");
        }
        if(e.Name=="skyedgeassert")
        {
            let it=ThinkerIterator.Create("UTNTSkyEdge");UTNTSkyEdge edge;int total=0,visible=0;bool safe=true;
            while(edge=UTNTSkyEdge(it.Next()))
            {
                total++;if(!edge.bInvisible)visible++;
                safe=safe && !edge.bSolid && edge.bNoInteraction && edge.bNoBlockmap;
            }
            Console.Printf("UTNT_ASSERT %s sky edge count %d expected COUNT",total==COUNT?"PASS":"FAIL",total);
            Console.Printf("UTNT_ASSERT %s sky edge collision flags",safe?"PASS":"FAIL");
            Console.Printf("UTNT_ASSERT %s sky edge visibility %d",visible==COUNT?"PASS":"FAIL",visible);
        }
        if(e.Name=="skyedgeinvalid")
        {
            let it=ThinkerIterator.Create("UTNTSkyEdge");UTNTSkyEdge edge;bool safe=true;int total=0;
            while(edge=UTNTSkyEdge(it.Next()))
            {
                let old=edge.Wall.GetTexture(edge.Part);
                edge.Wall.SetTexture(edge.Part,TexMan.CheckForTexture("STARTAN3"));edge.UpdateEdge();
                safe=safe && edge.bInvisible;edge.Wall.SetTexture(edge.Part,old);edge.UpdateEdge();total++;
            }
            Console.Printf("UTNT_ASSERT %s changed material fallback",safe && total>0?"PASS":"FAIL");
        }
        if(e.Name=="skyedgedetail")
        {
            let it=ThinkerIterator.Create("UTNTSkyEdge");UTNTSkyEdge edge;int hidden=0;
            while(edge=UTNTSkyEdge(it.Next()))if(edge.bInvisible && hidden++<6)
                Console.Printf("SKYEDGE_HIDDEN|%s|skin=%s/%s|uv=%f,%f/%f,%f|height=%f/%f",edge.GetClassName(),TexMan.GetName(edge.Wall.GetTexture(edge.Part)),edge.SkinName,edge.Wall.GetTextureXOffset(edge.Part),edge.Wall.GetTextureYOffset(edge.Part),edge.XOffset,edge.YOffset,edge.TopAt(edge.EdgeA),edge.InitialHeight);
        }
    }
}
'''.replace('MX','('+str(mx)+')').replace('MY','('+str(my)+')').replace('NX','('+str(nx)+')').replace('NY','('+str(ny)+')').replace('TOP','('+str(z)+')').replace('YAW','('+str(yaw)+')').replace('COUNT',str(len(selected))))
    prefix=f'sky-edges-{mapname}-{renderer}'+('-packaged' if packaged else '')+label_suffix
    commands=['unbindall','god','notarget','wait 180','vid_setsize 1280 720','wait 20','netevent skyedges','netevent skyedgeassert','netevent skyedgedetail']
    for view in range(3):
        commands += [f'netevent skyedgeview {view}','netevent skyedges_mode 0','wait 10',f'screenshot logs/{prefix}-{view}-before.png','netevent skyedges_mode 1','wait 10',f'screenshot logs/{prefix}-{view}-after.png']
    commands+=['netevent skyedgeview 0','netevent skyedgeglow 1','wait 20',f'screenshot logs/{prefix}-glow-on.png','netevent skyedgeglow 2','wait 20',f'screenshot logs/{prefix}-glow-off.png','netevent skyedgeglow 0','wait 10']
    commands+=['netevent skyedgeinvalid','save sky-edge-regression','wait 10','load sky-edge-regression','wait 70','netevent skyedgeassert','netevent skyedges','wait 20','echo UTNT_TEST_END','wait 10','quit']
    result=run_case(engine,iwad,root=root/'tutnt/.codex',mod=mod,addon=addon,mapname=mapname,renderer=renderer,label=prefix,commands='; '.join(commands)+'\n',timeout=90,settings=[('UTNT_subtitles',False),('vid_maxfps',60),('gl_texture_filter',0),('gl_bloom',False),('screenblocks',12),('crosshair',0),('r_drawplayersprites',False),('con_notifytime',0),('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),('vid_activeinbackground',True)])
    log=Path(result['log']).read_text()
    if result['assertions']!=8:
        result['ok']=False;result['errors'].append('missing runtime assertions (including post-load checks)')
    if any(s in log for s in ['Unable to load shader','Shader compilation failed','Failed to compile']):result['ok']=False
    out=root/'tutnt/.codex/validation/sky-edges';out.mkdir(parents=True,exist_ok=True)
    (out/(prefix+'.json')).write_text(json.dumps(result|dict(camera_edge=e),indent=2))
    if not result['ok']:print(log[-6000:]);raise SystemExit(1)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--runtime',action='store_true');ap.add_argument('--packaged',action='store_true');ap.add_argument('--map',default='TNT02');ap.add_argument('--renderer',default='1',choices=['0','1']);ap.add_argument('--engine',type=Path);ap.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'));ap.add_argument('--mod',type=Path,default=ROOT/'tutnt/.codex/builds/tutnt-sky-edges.pk3');ap.add_argument('--label-suffix',default='');ap.add_argument('--line',type=int);args=ap.parse_args()
    if args.runtime:runtime(ROOT,args.engine,args.iwad,args.mod,args.map.upper(),args.renderer,args.packaged,args.label_suffix,args.line)
    else:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(GeometryTests)
        if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():sys.exit(1)
        print(json.dumps(generate(ROOT,check=True),indent=2))
