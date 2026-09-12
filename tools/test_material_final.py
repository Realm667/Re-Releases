"""Render the user-reported relief materials on walls and floors in RELTEST."""
from pathlib import Path
import argparse,json,zipfile
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent
C=ROOT/'tutnt/.codex'
NAMES='ADEL_W39 CITYF01 XA22TEX XB22TEX IKTCR05B IKWALL28 METALF12 PANBOOK OTECH6 QMET10 QTECH30 QTECH31 QTECH32 SNOW3 XA16TEX XB16TEX TECHG QMET33'.split()

def capture(renderer='1',live=False,batch=0,names=None,suite='final'):
    names=NAMES if names is None else names
    assert suite in ('final','next','panel')
    rooms={r['name']:r for r in json.loads((C/'work/relief-gallery/rooms.json').read_text(encoding='utf8'))}
    selected=names[batch*6:batch*6+6];assert selected
    label=f'material-{suite}-{"live" if live else "package"}-r{renderer}-b{batch}'
    target=C/'builds'/f'{label}.pk3'
    cases=[]
    for i,n in enumerate(names):
        r=rooms[n];x,y=r['x'],r['y']
        cases.append(f'case {i}: Current={r["number"]-1};x={x};y={y};break;')
    injected='''  if(e.Name=="finalpose"){
   let p=players[0].mo;if(!p)return;
   double x,y;switch(e.Args[0]){CASES default:return;}
   if(e.Args[1]==0){p.SetOrigin((x,y-60,0),false);p.Angle=90;p.Pitch=5;}
   else if(e.Args[1]==1){p.SetOrigin((x-90,y,0),false);p.Angle=0;p.Pitch=48;}
   else{p.SetOrigin((x+90,y,0),false);p.Angle=180;p.Pitch=48;}
   p.Vel=(0,0,0);
   Console.Printf("FINAL_RELIEF|%s|%d|%s",NameAt(Current),e.Args[1],TexMan.GetName(p.CurSector.GetTexture(Sector.floor)));return;
  }
  int target=-1;'''.replace('CASES',''.join(cases))
    with zipfile.ZipFile(C/'builds/tutnt-relief-gallery.pk3') as src,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as dst:
        for e in src.infolist():
            data=src.read(e.filename)
            if e.filename=='ZSCRIPT':
                assert data.count(b'  int target=-1;')==1
                data=data.replace(b'  int target=-1;',injected.encode())
            dst.writestr(e,data)
        if live:
            g=json.loads((ROOT/'tools/organic-materials/generated.json').read_text(encoding='utf8'))
            for p in g['outputs']:
                data=(ROOT/p).read_bytes();dst.writestr(p.removeprefix('tutnt/'),data)
                # Old shared integration packages used the root include path.
                if p=='tutnt/gldefs/GLDEFS.organic':dst.writestr('GLDEFS.organic',data)
            dst.writestr('shaders/organic/relief.glsl',(ROOT/'tutnt/shaders/organic/relief.glsl').read_bytes())
    cmd='wait 240;screenblocks 12;'
    captures=[]
    for name in selected:
        for pose in range(3):
            rel=f'logs/{label}-{name}-{pose}.png';captures.append(rel)
            cmd+=f'netevent finalpose {names.index(name)} {pose};wait 8;netevent finalpose {names.index(name)} {pose};wait 25;screenshot "{rel}";wait 3;'
    cmd+='echo UTNT_TEST_END;wait 3;quit\n'
    settings=[('cl_capfps',True),('vid_scalemode',5),('vid_scale_customwidth',1280),('vid_scale_customheight',720),('i_pauseinbackground',False),('vid_activeinbackground',True),('use_mouse',False),('use_joystick',False),('con_notifytime',0),('r_drawplayersprites',False),('gl_texture_filter',0)]
    r=run_case(Path('F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe'),Path('F:/DoomDev/DOOM2.WAD'),root=C,mod=ROOT/'tutnt.pk3',addon=target,mapname='RELTEST',renderer=renderer,label=label,timeout=100,commands=cmd,settings=settings,quiet=True)
    assert r['ok'],r
    log=Path(r['log']).read_text(encoding='utf8')
    assert not any(s in log for s in ('Failed to compile','Unknown texture','Missing texture'))
    for name in selected:
        for pose in range(3):assert f'FINAL_RELIEF|{name}|{pose}|{name}' in log,(name,pose)
    assert all((C/p).is_file() for p in captures)
    r.update(materials=selected,captures=captures,renderer=renderer,live=live)
    out=C/'validation'/f'material-{suite}-pass';out.mkdir(exist_ok=True)
    (out/f'{label}.json').write_text(json.dumps(r,indent=2),encoding='utf8')
    print(json.dumps(r),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--renderer',default='1');p.add_argument('--live',action='store_true');p.add_argument('--batch',type=int,default=0);p.add_argument('--names',nargs='+');p.add_argument('--suite',choices=['final','next','panel'],default='final');a=p.parse_args();capture(a.renderer,a.live,a.batch,a.names,a.suite)
