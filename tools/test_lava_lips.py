"""Isolated lava spill geometry regression, with optional packaged input."""
from pathlib import Path
import sys,struct,json,re,shutil,argparse
HERE=ROOT=ENGINE=IWAD=MOD=None

def fixture():
    from build_lava_lips import generate
    project=ROOT/'tutnt/.codex/work/performance-multiplayer/lava-fixture-project';addon=project/'tutnt';(addon/'maps').mkdir(parents=True,exist_ok=True)
    # Clockwise high pool, two joined fall segments; low pool below it.
    vertices=[(-384,-384),(-384,0),(0,0),(384,96),(384,-384),(-384,512),(384,512)]
    lines=[(0,1,0,None),(1,2,0,1),(2,3,0,1),(3,4,0,None),(4,0,0,None),(1,5,1,None),(5,6,1,None),(6,3,1,None)]
    text='namespace="zdoom";\n';sides=[]
    for x,y in vertices:text+=f'vertex {{ x={x}; y={y}; }}\n'
    for a,b,hi,lo in lines:
        sf=len(sides);sides.append((hi,'BSTONE1','-'))
        sb=len(sides) if lo is not None else -1
        if lo is not None:sides.append((lo,'-','LAVA'))
        text+=f'linedef {{ v1={a}; v2={b}; sidefront={sf};'+(f' sideback={sb}; twosided=true;' if sb>=0 else ' blocking=true;')+' }\n'
    for sec,mid,bot in sides:text+=f'sidedef {{ sector={sec}; texturemiddle="{mid}"; texturebottom="{bot}"; }}\n'
    text+='sector { heightfloor=0; heightceiling=512; texturefloor="QLAVA"; textureceiling="CEIL5_2"; lightlevel=192; id=101; }\n'
    text+='sector { heightfloor=-192; heightceiling=512; texturefloor="RROCK05"; textureceiling="CEIL5_2"; lightlevel=192; }\n'
    text+='thing { x=0; y=-240; type=1; angle=90; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; dm=true; }\n'
    body=bytearray();dire=bytearray();lumps=[(b'LIPTEST',b''),(b'TEXTMAP',text.encode()),(b'ENDMAP',b'')]
    for n,d in lumps:dire+=struct.pack('<II8s',12+len(body),len(d),n);body+=d
    (addon/'maps/liptest.wad').write_bytes(struct.pack('<4sII',b'PWAD',len(lumps),12+len(body))+body+dire)
    (addon/'shaders').mkdir(exist_ok=True)
    for name in ('lava-surface.fp','lava-fall.fp'):
        text=(ROOT/'tutnt/shaders'/name).read_text();text=re.sub(r'\btimer\b','(3.75)',text)
        (addon/'shaders'/name).write_text(text)
    generate(project)
    generated=addon/'zscript/lava-lips-generated.zc'
    generated.write_text((ROOT/'tutnt/zscript/lava-lips-generated.zc').read_text()+generated.read_text())
    (addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTLipTest" }\nmap LIPTEST "Lava lip fixture" { NoIntermission }\n')
    (addon/'ZSCRIPT.test').write_text('''version "5.0.0"
class UTNTLipTest : EventHandler
{
    Actor Cam;
    int View;
    override void WorldTick()
    {
        if(level.time<5)return;
        if(!Cam)Cam=Actor.Spawn("MapSpot",(0,-190,100));
        Vector3 pos;double yaw,pitch;
        if(level.MapName~=="LIPTEST")
        {
            pos=View==0 ? (-140,-190,105) : View==1 ? (110,210,52) : (330,180,6);
            yaw=View==0?70:View==1?260:230;pitch=View==0?25:View==1?18:0;
        }
        else if(level.MapName~=="TNT02") { pos=(1600,-1020,-16);yaw=270;pitch=20; }
        else { pos=(4360,-1460,40);yaw=342;pitch=25; }
        Cam.SetOrigin(pos,false);Cam.Angle=yaw;Cam.Pitch=pitch;players[0].camera=Cam;
    }
    override void NetworkProcess(ConsoleEvent e)
    {
        if(e.Name=="lipview")View=e.Args[0];
        if(e.Name=="lipmode")
        {
            let it=ThinkerIterator.Create("UTNTLavaLip",Thinker.MAX_STATNUM+1,true);UTNTLavaLip lip;
            while(lip=UTNTLavaLip(it.Next()))lip.A_SetRenderStyle(1.0,e.Args[0]==0?STYLE_None:STYLE_Translucent);
        }
        if(e.Name=="lipassert")
        {
            int count=0;let it=ThinkerIterator.Create("UTNTLavaLip",Thinker.MAX_STATNUM+1,true);UTNTLavaLip lip;
            while(lip=UTNTLavaLip(it.Next()))
            {
                count++;
                bool equalized=(level.MapName~=="TNT02") && lip.High && lip.High.Index()==109
                    && abs(lip.High.floorplane.ZatPoint(lip.Center)-lip.Low.floorplane.ZatPoint(lip.Center))<0.01;
                if(lip.bSolid || !lip.bNoInteraction || lip.High==null || lip.bInvisible!=equalized)Console.Printf("UTNT_ASSERT FAIL lip collision/visibility");
                else Console.Printf("UTNT_ASSERT PASS lip nonblocking");
            }
            int expected=(level.MapName~=="LIPTEST")?2:(level.MapName~=="TNTLE")?118:9;
            Console.Printf("UTNT_ASSERT %s lip count %d expected %d",count==expected?"PASS":"FAIL",count,expected);
        }
        if(e.Name=="lipmove")level.Sectors[0].MoveFloor(128,level.Sectors[0].floorplane.PointToDist((0,0),e.Args[0]),-1,e.Args[0]>0?1:-1,false,true);
        if(e.Name=="liptexture")level.Sectors[0].SetTexture(Sector.floor,TexMan.CheckForTexture(e.Args[0]==0?"QLAVA":e.Args[0]==2?"QLAVA2":e.Args[0]==3?"QLAVASB":"QWATER1"));
        if(e.Name=="lipwall")
        {
            let it=ThinkerIterator.Create("UTNTLavaLip",Thinker.MAX_STATNUM+1,true);UTNTLavaLip lip;
            while(lip=UTNTLavaLip(it.Next()))lip.FallSide.SetTexture(Side.bottom,TexMan.CheckForTexture(e.Args[0]==0?"LAVA":"LAVAHR"));
        }
        if(e.Name=="lipstate")
        {
            int count=0;bool ok=true;let it=ThinkerIterator.Create("UTNTLavaLip",Thinker.MAX_STATNUM+1,true);UTNTLavaLip lip;
            while(lip=UTNTLavaLip(it.Next()))
            {
                count++;
                if(e.Args[0]==0)ok=ok && lip.bInvisible;
                else ok=ok && !lip.bInvisible && abs(lip.Pos.Z-e.Args[1])<0.01;
            }
            Console.Printf("UTNT_ASSERT %s dynamic lip state %d height %d",ok && count==2?"PASS":"FAIL",e.Args[0],e.Args[1]);
        }
    }
}
''')
    return addon

def run(renderer='1',mapname='LIPTEST'):
    from check_engine import run_case
    addon=fixture()
    if mapname!='LIPTEST':
        # Real-map run uses the project's generated registration/model assets.
        scene=ROOT/'tutnt/.codex/work/performance-multiplayer/lava-scene';scene.mkdir(exist_ok=True)
        for n in ('MAPINFO','ZSCRIPT.test'):shutil.copyfile(addon/n,scene/n)
        (scene/'shaders').mkdir(exist_ok=True)
        if MOD is None:
            for name in ('lava-surface.fp','lava-fall.fp','lava-lips.fp'):shutil.copyfile((HERE/'fixture-project/tutnt/shaders')/name,scene/'shaders'/name)
        addon=scene
    commands=['unbindall','god','notarget','wait 500','vid_setsize 1280 720','wait 20','netevent lavalips','netevent lipassert']
    for view in range(3 if mapname=='LIPTEST' else 1):
        commands += [f'netevent lipview {view}','netevent lipmode 0','wait 10',f'screenshot logs/lip-{mapname}-{renderer}-{view}-before.png','netevent lipmode 1','wait 10',f'screenshot logs/lip-{mapname}-{renderer}-{view}-after.png']
    if mapname=='LIPTEST':
        commands+=['netevent lipmove 16','wait 10','netevent lipstate 1 16','netevent liptexture 1','wait 10','netevent lipstate 0','netevent liptexture 0','netevent lipmove 0','wait 10','netevent lipstate 1 0']
        for variant in [2,3]:
            commands += [f'netevent liptexture {variant}','netevent lipwall 1','wait 10','netevent lipstate 1 0']
        commands += ['netevent lipview 1','wait 10',f'screenshot logs/lip-LIPTEST-{renderer}-variants.png','netevent liptexture 0','netevent lipwall 0','wait 10','netevent lipstate 1 0']
    commands+=['save lip-save','wait 5','load lip-save','wait 20','netevent lipassert','netevent lavalips','wait 5','echo UTNT_TEST_END','wait 5','quit']
    result=run_case(ENGINE,IWAD,root=HERE,mod=MOD or ROOT/'tutnt',addon=addon,mapname=mapname,renderer=renderer,label=f'lip-{mapname}-{renderer}',commands='; '.join(commands)+'\n',timeout=60,settings=[('vid_maxfps',60),('gl_texture_filter',0),('gl_bloom',False),('screenblocks',12),('crosshair',0),('r_drawplayersprites',False),('con_notifytime',0),('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),('vid_activeinbackground',True)])
    log=Path(result['log']).read_text()
    if any(x in log for x in ['Unable to load shader','Failed to compile','Shader compilation failed']):result['ok']=False
    (HERE/f'result-{mapname}-{renderer}.json').write_text(json.dumps(result,indent=2))
    if not result['ok']:print(log[-7000:]);raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser(description="Render lava lip before/after views and verify rule, movement and save/load.")
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parent.parent)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--engine',required=True);p.add_argument('--iwad',required=True)
    p.add_argument('--mod',type=Path);p.add_argument('--renderer',choices=['0','1'],default='1')
    p.add_argument('--map',choices=['LIPTEST','TNTLE','TNT02'],default='LIPTEST')
    a=p.parse_args();ROOT=a.project.resolve();HERE=a.out.resolve();HERE.mkdir(parents=True,exist_ok=True)
    ENGINE=a.engine;IWAD=a.iwad;MOD=a.mod
    sys.path.insert(0,str(ROOT/'tools'));run(a.renderer,a.map)
