"""Compare actual cap joins over black/white backgrounds, opaque and fading.
Set UTNT_ENGINE / UTNT_IWAD. Requires Pillow and numpy for screenshot reads.
"""
from pathlib import Path
import argparse,json,os
import numpy as np
from PIL import Image
from check_engine import run_case

R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mod',type=Path,default=R/'tutnt')
p.add_argument('--renderer',choices=['0','1'],default='1')
p.add_argument('--label',default='objectives-seams')
a=p.parse_args();label=a.label+'-'+a.renderer
scales=[0.84,1.05,1.37,1.61];heights=[292,310.4,368,403.2]
commands=['wait 10']
for preset in range(4):
    for half in range(2):
        for background in range(2):
            commands += [f'event objseam {preset} {background} {half}','wait 3',
                f'screenshot logs/{label}-{preset}-{half}-{background}.png','wait 3']
commands += ['echo UTNT_TEST_END','wait 2','quit']
r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=R,mod=a.mod,
    addon=R/'tools/objective-seam-tests',mapname='TNT01',renderer=a.renderer,label=label,
    commands='; '.join(commands)+'\n',timeout=60,settings=[('win_w',1298),('win_h',767),
    ('con_notifytime',0),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False)])
checks=[]
if r['ok']:
    for preset,(scale,height) in enumerate(zip(scales,heights)):
        for half in range(2):
            images=[np.asarray(Image.open(R/'logs'/f'{label}-{preset}-{half}-{b}.png').convert('RGB'),dtype=np.int16) for b in range(2)]
            delta=images[1]-images[0]
            assert np.all(delta[0,0]==255),'Contrast backgrounds not captured'
            left=round(51.37+12*scale);right=round(51.37+508*scale)
            for edge in [60,height-16]:
                y=round(23.21+edge*scale)
                band=delta[y-2:y+3,left:right,:]
                expected=128 if half else 0
                worst=int(np.abs(band-expected).max())
                checks.append({'preset':preset,'half_opacity':bool(half),'edge':edge,'max_error':worst,'ok':worst<=2})
    r['ok']=all(c['ok'] for c in checks)
    if not r['ok']:r['errors'].append('cap join has a gap or double alpha blending')
r['pixel_checks']=checks
(R/'logs'/f'{label}-results.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'ok':r['ok'],'pixel_checks':len(checks),'failed':[c for c in checks if not c['ok']]}))
raise SystemExit(0 if r['ok'] else 1)
