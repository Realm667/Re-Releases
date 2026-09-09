"""Verify map panning against equivalent world-camera shifts with frozen shader time."""
from pathlib import Path
import argparse,json,re,shutil
import numpy as np
from PIL import Image
from test_liquids import fixture
from check_engine import run_case

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parent.parent)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--mod',type=Path)
    p.add_argument('--engine',required=True);p.add_argument('--iwad',required=True)
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    addon=fixture(out,True)
    (addon/'MAPINFO').write_text((addon/'MAPINFO').read_text().replace('AddEventHandlers="UTNTLiquidTest"','AddEventHandlers="UTNTLiquidTest", "UTNTMapFlowTest"'))
    with (addon/'ZSCRIPT').open('a') as f:f.write('''
class UTNTMapFlowTest : EventHandler
{
    Actor Cam;
    override void NetworkProcess(ConsoleEvent e)
    {
        if(e.Name!="mapflowview")return;
        int mode=e.Args[0];int rotation=e.Args[1];
        for(int i=0;i<level.Sectors.Size();i++)
        {
            let sec=level.Sectors[i];
            sec.SetXScale(sector.floor,1.7);sec.SetYScale(sector.floor,1.3);
            sec.SetAngle(sector.floor,rotation);
            sec.SetXOffset(sector.floor,mode==1?32.0:0.0);
            sec.SetYOffset(sector.floor,mode==3?32.0:0.0);
        }
        Vector3 position=(0,-100,56);
        if(mode==2)position+=rotation==90?(0,-32,0):(32,0,0);
        if(mode==4)position+=rotation==90?(-32,0,0):(0,-32,0);
        if(!Cam)Cam=Actor.Spawn("MapSpot",position);
        Cam.SetOrigin(position,false);Cam.Angle=90;Cam.Pitch=25;
        players[0].camera=Cam;
        Console.Printf("UTNT_ASSERT PASS mapflow mode %d rotation %d",mode,rotation);
    }
}
''')
    definitions=(a.project/'tutnt/GLDEFS.liquids').read_text()
    for family in ['water','slime','blood']:
        source=(a.project/f'tutnt/shaders/liquids/{family}.fp').read_text()
        source=re.sub(r'\btimer\b','(375.000000)',source)
        (addon/(family+'.fp')).write_text(source)
        definitions=definitions.replace(f'shaders/liquids/{family}.fp',family+'.fp')
    (addon/'GLDEFS').write_text(definitions)
    results=[];metrics={}
    for backend in (['0','1'] if a.renderer=='both' else [a.renderer]):
        label='mapflow-'+backend;commands=['wait 180','vid_setsize 1280 720','wait 30']
        cases=[(0,'QWATER1',0),(5,'QSLIME1',0),(10,'QWATERT6',0),(0,'QWATER1',90)]
        for index,name,rotation in cases:
            commands += [f'netevent liquidselect {index}']
            for mode in range(5):commands += [f'netevent mapflowview {mode} {rotation}','wait 12',f'screenshot logs/{label}-{name}-{rotation}-{mode}.png']
        commands+=['echo UTNT_TEST_END','wait 4','quit']
        r=run_case(a.engine,a.iwad,root=out,mod=a.mod or a.project/'tutnt',addon=addon,mapname='LIQTEST',renderer=backend,label=label,commands='; '.join(commands)+'\n',timeout=120,
            settings=[('vid_maxfps',60),('gl_texture_filter',0),('gl_bloom',False),('gl_lights',True),('screenblocks',12),('crosshair',0),('r_drawplayersprites',False),('con_notifytime',0)])
        results.append(r)
        if not r['ok']:raise RuntimeError(Path(r['log']).read_text()[-6000:])
        for _,name,rotation in cases:
            def frame(mode):return np.asarray(Image.open(out/f'logs/{label}-{name}-{rotation}-{mode}.png').convert('RGB'),dtype=float)[220:660,100:1180]
            base=frame(0)
            for actual,expected,axis in [(1,2,'X'),(3,4,'Y')]:
                pan=frame(actual);reference=frame(expected)
                error=float(abs(pan-reference).mean());movement=float(abs(pan-base).mean())
                assert movement>0.3,(backend,name,rotation,axis,'map scroll ignored',movement)
                assert error<0.5,(backend,name,rotation,axis,'wrong direction or speed',error)
                metrics[f'{backend}-{name}-{rotation}-{axis}']={'camera_equivalence_error':error,'pan_delta':movement}
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
