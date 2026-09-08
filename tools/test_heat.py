"""Regression for sector-wide HeatEffectGiver, including a solid 3D floor.

Set UTNT_ENGINE / UTNT_IWAD or pass --engine / --iwad. Test addons and logs
are generated under --output; no campaign maps or user settings are changed.
"""
from pathlib import Path
import argparse, json, os, struct
from PIL import Image, ImageChops, ImageStat
from check_engine import run_case


def fixture(out):
    addon = out / 'fixture'
    (addon / 'maps').mkdir(parents=True, exist_ok=True)
    text = 'namespace="ZDoom";\n'
    for x, y in [(-512,-512),(-512,512),(512,512),(512,-512),
                 (1024,0),(1024,64),(1088,64),(1088,0)]:
        text += f'vertex {{ x={x}.0; y={y}.0; }}\n'
    for i in range(8):
        sector = i // 4
        text += f'sidedef {{ sector={sector}; texturemiddle="STARTAN3"; }}\n'
        special = 'special=160; arg0=1; arg1=1; arg4=255;' if i == 4 else ''
        text += f'linedef {{ v1={i}; v2={sector*4+(i+1)%4}; sidefront={i}; blocking=true; {special} }}\n'
    for floor, ceiling, tag in [(0,192,1),(32,64,0)]:
        text += f'sector {{ heightfloor={floor}; heightceiling={ceiling}; id={tag}; texturefloor="FLAT5_4"; textureceiling="CEIL1_1"; lightlevel=192; }}\n'
    for typ, x, tid in [(1,0,0),(32029,32,32029)]:
        text += f'thing {{ x={x}.0; y=0.0; type={typ}; id={tid}; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; }}\n'
    body, directory = bytearray(), bytearray()
    for name, data in [(b'HEATEST',b''),(b'TEXTMAP',text.encode()),(b'ENDMAP',b'')]:
        directory += struct.pack('<II8s',12+len(body),len(data),name)
        body += data
    (addon/'maps/heatest.wad').write_bytes(struct.pack('<4sII',b'PWAD',3,12+len(body))+body+directory)
    (addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTHeatRegression" }\nmap HEATEST "Heat regression" { levelnum=91 }\n')
    (addon/'ZSCRIPT').write_text('''version "5.0.0"
class UTNTHeatRegression : EventHandler
{
    HeatEffectGiver Source;
    void Check(bool ok, String message)
    { Console.Printf("UTNT_ASSERT %s: %s",ok ? "PASS" : "FAIL",message); }
    override void WorldTick()
    {
        if(level.time==2)
        {
            Source=HeatEffectGiver(ActorIterator.Create(32029).Next());
            let p=players[0].mo;
            p.bNoGravity=true; p.bNoClip=true; p.bNoInteraction=true; p.bInvulnerable=true;
            p.SetOrigin((0,0,64),false); p.Angle=0; p.Pitch=0;
        }
        if(level.time==35)
        {
            Check(Source!=null,"editor number 32029 spawns heat source");
            Check(Source.CeilingZ==32 && players[0].mo.Pos.Z==64,"fixture separates player from cached collision ceiling");
            let b=UTNTPlayerEffects(players[0].mo.FindBehavior('UTNTPlayerEffects'));
            Check(b && abs(b.Heat-0.75)<0.001,"heat crosses 3D floor within base sector");
        }
    }
    override void NetworkProcess(ConsoleEvent e)
    {
        let p=players[0].mo;
        if(e.Name=="heatmove") { p.SetOrigin((32+e.Args[0],0,e.Args[1]),false); p.Vel=(0,0,0); }
        if(e.Name=="heatcheck")
        {
            let b=UTNTPlayerEffects(p.FindBehavior('UTNTPlayerEffects'));
            Check(b && abs(b.Heat-e.Args[0]/1000.0)<0.001,String.Format("heat expected %d/1000, actual %.3f",e.Args[0],b ? b.Heat : -1));
        }
        if(e.Name=="heatact")
        {
            if(e.Args[0]==0) Source.Deactivate(p);
            if(e.Args[0]==1) Source.Activate(p);
            if(e.Args[0]==2) Source.Scale=(2,2);
            if(e.Args[0]==3) Source.Destroy();
            if(e.Args[0]==4) Source=HeatEffectGiver(Actor.Spawn('HeatEffectGiver',(32,0,0)));
        }
    }
}
''')
    return addon


def main():
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mod',type=Path,default=root/'tutnt.pk3')
    p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE'))
    p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD'))
    p.add_argument('--output',type=Path,default=root/'logs/heat-tests')
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    a=p.parse_args()
    if not a.engine or not a.iwad: p.error('set UTNT_ENGINE/UTNT_IWAD or pass --engine/--iwad')
    out=a.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    addon=fixture(out); results=[]
    for renderer in (['0','1'] if a.renderer=='both' else [a.renderer]):
        label='heat-'+renderer
        commands=f'''unbindall; wait 160; listuniforms heatshader; screenshot logs/{label}-on.png;
UTNT_shaderoverlayswitch false; wait 10; screenshot logs/{label}-off.png;
UTNT_shaderoverlayswitch true; UTNT_heatstrength 0; wait 10; screenshot logs/{label}-zero.png;
UTNT_heatstrength 1; UTNT_reducedfx true; wait 10; screenshot logs/{label}-reduced.png;
UTNT_reducedfx false; wait 10; save {label}; wait 10;
netevent heatmove 64 64; wait 40; netevent heatcheck 500;
netevent heatmove 128 64; wait 40; netevent heatcheck 0;
netevent heatmove 0 64; wait 10; netevent heatcheck 1000;
netevent heatact 0; wait 40; netevent heatcheck 0;
netevent heatact 1; wait 10; netevent heatcheck 1000;
netevent heatmove 64 64; netevent heatact 2; wait 40; netevent heatcheck 750;
netevent heatmove 64 200; wait 40; netevent heatcheck 0;
netevent heatmove 64 -100; wait 40; netevent heatcheck 0;
netevent heatmove 64 0; wait 40; netevent heatcheck 750;
netevent heatact 3; wait 40; netevent heatcheck 0;
netevent heatact 4; wait 10; netevent heatcheck 500; wait 5;
load {label}; wait 40; netevent heatcheck 750; screenshot logs/{label}-restored.png;
wait 10; echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit
'''
        result=run_case(a.engine,a.iwad,root=out,mod=a.mod,addon=addon,
            mapname='HEATEST',renderer=renderer,label=label,timeout=60,
            commands=commands.replace(chr(10),' '),regression=True,settings=[('use_mouse',False),
            ('use_joystick',False),('i_pauseinbackground',False),('UTNT_reducedfx',False),
            ('UTNT_shaderoverlayswitch',True),('UTNT_heatstrength',1),
            ('motionblur',False),('r_drawplayersprites',False)])
        log=Path(result['log']).read_text()
        result['uniform_ok']='  amount : 51.750000' in log and '  Amount :' not in log
        def frame(mode):
            # Static ceiling detail, away from the HUD and console notices.
            return Image.open(out/f'logs/{label}-{mode}.png').convert('RGB').crop((100,50,800,160))
        off=frame('off')
        def difference(mode):
            return sum(ImageStat.Stat(ImageChops.difference(frame(mode),off)).mean)/3
        result['pixel_differences']={m:difference(m) for m in ['on','zero','reduced']}
        result['render_ok']=(result['pixel_differences']['on']>1
            and result['pixel_differences']['zero']<0.1
            and result['pixel_differences']['reduced']<0.1)
        results.append(result)
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    assert all(r['ok'] and r['assertions']==15 and r['uniform_ok'] and r['render_ok'] for r in results),results


if __name__=='__main__': main()
