"""Native regression for signed/repeated material UVs and side-on floor relief."""
from pathlib import Path
import argparse,json,zipfile
import numpy as np
from PIL import Image
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent
C=ROOT/'tutnt/.codex'

ORACLE='''
float ReliefUVError(sampler2D dataMap,vec2 uv,vec2 gx,vec2 gy)
{
    vec2 base=fract(uv);
    vec4 reference=RockRawData(dataMap,base,gx,gy);
    vec2 offsets[6]=vec2[6](vec2(-3,-7),vec2(-3,7),vec2(3,-7),vec2(3,7),vec2(-64,0),vec2(0,-64));
    float error=0.0;
    for(int i=0;i<6;i++){
        vec4 d=abs(reference-RockRawData(dataMap,base+offsets[i],gx,gy));
        error=max(error,max(max(d.x,d.y),max(d.z,d.w)));
    }
    return error;
}
'''

def addon(shader,mode,label):
    if mode=='oracle':
        shader=shader.replace('void SetupOrganicMaterial(inout Material mat)',ORACLE+'\nvoid SetupOrganicMaterial(inout Material mat)')
        needle='    if(abs(determinantUV)<1e-12)return;'
        shader=shader.replace(needle,'''    float error=max(ReliefUVError(organicHeight,uv,gx,gy),ReliefUVError(normaltexture,uv,gx,gy));
    float fail=step(0.002,error);
    mat.Base=vec4(fail,1.0-fail,0.0,1.0);mat.Normal=n;mat.Specular=vec3(0);mat.SpecularLevel=0;return;
'''+needle)
    target=C/'builds'/('relief-uv-'+label+'.pk3')
    with zipfile.ZipFile(C/'builds/tutnt-relief-gallery.pk3') as src,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as dst:
        for entry in src.infolist():
            data=src.read(entry.filename)
            if entry.filename=='ZSCRIPT':
                data=data.replace(b'  int target=-1;',b'''  if(e.Name=="reliefpose"){
   let p=players[0].mo;if(p){
    if(e.Args[0]==0){p.SetOrigin((3904,320,0),false);p.Angle=0;}
    else if(e.Args[0]==1){p.SetOrigin((4128,320,0),false);p.Angle=180;}
    else{p.SetOrigin((4032,260,0),false);p.Angle=90;}
    p.Pitch=35;p.Vel=(0,0,0);
   }return;
  }
  int target=-1;''')
            dst.writestr(entry,data)
        if shader is not None:dst.writestr('shaders/organic/relief.glsl',shader)
    return target


def capture(engine,iwad,shader,renderer,mode,label):
    target=addon(shader,mode,label)
    poses=[0] if mode=='oracle' else [0,1,2]
    cmd='wait 240;screenblocks 12;'
    for pose in poses:
        cmd+=f'netevent reliefpose {pose};wait 8;netevent reliefpose {pose};wait 30;screenshot "logs/relief-uv-{label}-{pose}.png";wait 3;'
    cmd+='echo UTNT_TEST_END;wait 3;quit\n'
    settings=[('cl_capfps',True),('vid_scalemode',5),('vid_scale_customwidth',1280),('vid_scale_customheight',720),('i_pauseinbackground',False),('vid_activeinbackground',True),('use_mouse',False),('use_joystick',False),('con_notifytime',0),('r_drawplayersprites',False),('gl_texture_filter',0)]
    r=run_case(engine,iwad,root=C,mod=ROOT/'tutnt.pk3',addon=target,mapname='RELTEST',renderer=renderer,label='relief-uv-'+label,timeout=55,commands=cmd,settings=settings,quiet=True)
    assert r['ok'],r
    log=Path(r['log']).read_text(encoding='utf-8')
    assert not any(s in log for s in ['Failed to compile','Unknown texture','Missing texture'])
    if mode=='oracle':
        # Central floor region excludes HUD, signs and neighboring materials.
        rgb=np.asarray(Image.open(C/'logs'/f'relief-uv-{label}-0.png').convert('RGB'),dtype=np.int16)[200:580,320:960]
        failed=(rgb[:,:,0]>2*rgb[:,:,1])&(rgb[:,:,0]>20)
        green=(rgb[:,:,1]>2*rgb[:,:,0])&(rgb[:,:,1]>20)
        r.update(failed_pixels=int(failed.sum()),passed_pixels=int(green.sum()),sample_pixels=int(failed.size))
        assert r['passed_pixels']+r['failed_pixels']>failed.size*.95,'Oracle image was obscured'
    r.update(mode=mode,renderer=renderer,poses=poses);print(json.dumps(r),flush=True);return r


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',type=Path,default=Path('F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe'))
    p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'))
    p.add_argument('--before',type=Path,help='Optional pre-fix shader for a native comparison')
    a=p.parse_args();shader=(ROOT/'tutnt/shaders/organic/relief.glsl').read_text(encoding='utf-8')
    with zipfile.ZipFile(ROOT/'tutnt.pk3') as z:
        packaged=z.read('shaders/organic/relief.glsl').decode().replace('\r\n','\n')
        assert packaged==shader,'Build tutnt.pk3 before the native package test'
    results=[]
    if a.before:results.append(capture(a.engine,a.iwad,a.before.read_text(encoding='utf-8'),'1','oracle','before-oracle'))
    for renderer in ['1','0']:
        r=capture(a.engine,a.iwad,shader,renderer,'oracle','fixed-oracle-r'+renderer);results.append(r)
        assert r['failed_pixels']==0,('Whole-tile UV translation changed relief samples',r)
        results.append(capture(a.engine,a.iwad,None,renderer,'visual','fixed-r'+renderer))
    dest=C/'validation/relief-uv-offset';dest.mkdir(exist_ok=True)
    (dest/'native.json').write_text(json.dumps(results,indent=2),encoding='utf-8')

if __name__=='__main__':main()
