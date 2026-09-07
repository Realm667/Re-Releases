"""UTNT organic fire lifecycle, particle population, renderer and visual-color regression.
Run with configured UTNT_ENGINE/UTNT_IWAD. Writes only logs and isolated saves.
The fixture exercises default map replacements, explicit aliases and barrels.
"""
import argparse, json, os
from pathlib import Path
from check_engine import ROOT,run_case

def commands(label):
    s=['unbindall','wait 200','vid_setsize 1920 1080','wait 20','event firecheck 8']
    def shot(name): s.append(f'screenshot logs/{label}-{name}.png')
    shot('overview')
    for camera,name in [(1,'orange'),(3,'green'),(4,'blue'),(2,'barrels')]:
        s.extend([f'netevent firecamera {camera}','wait 50',f'event fireview {camera}']); shot(name)
        if camera==1:
            s.append('wait 13'); shot('motion')
            for frame in range(8):
                s.append('wait 4'); shot(f'flow-{frame:02d}')
    s.extend(['netevent firecamera 0','wait 20',f'save {label}','wait 5',
              'UTNT_fxquality 0','wait 50','event firecheck 0'])
    shot('disabled')
    s.extend(['UTNT_fxquality 1','wait 50','event firecheck 8'])
    shot('low')
    s.extend(['UTNT_fxquality 2','wait 50','event firecheck 8',
              'UTNT_fxquality 3','UTNT_reducedfx true','wait 50','event firecheck 8'])
    shot('reduced')
    s.extend(['UTNT_reducedfx false','UTNT_lod 10','wait 50','event firecheck 0',
              'UTNT_lod 2000','wait 50','event firecheck 8',
              'netevent fireremove','wait 30','event firecheck 7',
              f'load {label}','wait 60','event firecheck 8'])
    shot('restored')
    s.extend(['netevent firealiases','wait 60','event firecheck 14'])
    shot('aliases')
    s.extend(['netevent firestress','wait 100','event firecheck 54','profilecsthinkers -t 10'])
    shot('stress')
    s.extend(['UTNT_fxquality 2','wait 70','event firecheck 54','UTNT_fxquality 0','wait 50','event firecheck 0','UTNT_fxquality 1','wait 70','event firecheck 54',
              'echo UTNT_REGRESSION_COMPLETE','echo UTNT_TEST_END','wait 5','quit'])
    return '; '.join(s)+'\n'

def inspect_pixels(label):
    # Checks the rendered result, not only the shader registration flags.
    from PIL import Image,ImageChops
    results={}
    for color in ['orange','green','blue']:
        im=Image.open(ROOT/'logs'/f'{label}-{color}.png').convert('RGB')
        assert im.size==(1920,1080),im.size
        pixels=im.crop((870,150,1050,450)).getdata()
        if color=='green': n=sum(g>90 and g>r*1.6 and g>b*1.6 for r,g,b in pixels)
        elif color=='blue': n=sum(b>90 and b>r*1.6 and b>g*1.2 for r,g,b in pixels)
        else: n=sum(r>150 and r>g*1.3 and g>b*1.5 for r,g,b in pixels)
        results[color+'_pixels']=n
        assert n>300,(color,n)
    a=Image.open(ROOT/'logs'/f'{label}-orange.png').convert('RGB').crop((870,150,1050,450))
    b=Image.open(ROOT/'logs'/f'{label}-motion.png').convert('RGB').crop((870,150,1050,450))
    n=sum(max(rgb)>20 for rgb in ImageChops.difference(a,b).getdata())
    results['animated_pixels']=n
    assert n>200,n
    return results

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    p.add_argument('--mod',type=Path)
    p.add_argument('--label',default='fire-final')
    a=p.parse_args();results=[]
    for renderer in ['0','1'] if a.renderer=='both' else [a.renderer]:
        label=a.label+'-'+renderer
        r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mod=a.mod,
            mapname='UTNTFIRE',addon=ROOT/'tools/fire-tests',renderer=renderer,
            label=label,commands=commands(label),timeout=120,regression=True,
            settings=[('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),('screenblocks',12),('vid_maxfps',120),('gl_texture_filter',0),('gl_lights',True),
                      ('gl_bloom',True),('UTNT_fxquality',3),('UTNT_reducedfx',False),('UTNT_lod',2000),
                      ('crosshair',0),('r_drawplayersprites',False),('con_notifytime',0)])
        if r['ok']:
            try:r['pixels']=inspect_pixels(label)
            except Exception as e:r['ok']=False;r['errors'].append(str(e))
        results.append(r)
    (ROOT/'logs'/(a.label+'-results.json')).write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
    raise SystemExit(0 if all(r['ok'] for r in results) else 1)
if __name__=='__main__':main()
