"""Render a diverse before/after PNG gallery with the real engine and compare pixels."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
from check_engine import ROOT, run_case


def run(report,package,engine,iwad):
    report=json.loads(Path(report).read_text(encoding='utf-8'))
    changed=[r for r in report['files'] if 'candidate' in r]
    chosen={r['path']:r for r in sorted(changed,key=lambda r:r['before'],reverse=True)[:96]}
    # Sample every changed subfolder, plus repaired CRCs and alpha conversions.
    groups={}
    for row in changed:
        key=str(Path(row['path']).parent)
        groups.setdefault(key,[]).append(row)
    for group in groups.values():
        for row in sorted(group,key=lambda r:r['before'],reverse=True)[:3]:chosen[row['path']]=row
    for category in ('crc_errors','stages'):
        rows=[r for r in changed if r[category] and (category=='crc_errors' or 'opaque-alpha' in r['stages'])]
        for row in (rows[:20] if category=='crc_errors' else rows):chosen[row['path']]=row
    rows=list(chosen.values())
    if len(rows)>800:raise ValueError('Gallery capacity exceeded')
    work=ROOT/'tutnt/.codex/work/png-optimization';results=[];screens=[]
    script='''version "5.0.0"
class UTNTPngGallery : StaticEventHandler {
 ui bool Reported;
 ui void Tile(String name,int i) {
  let tex=TexMan.CheckForTexture(name,TexMan.Type_Any);
  if(!Reported) Console.Printf("UTNT_ASSERT %s: PNG %s",tex.isValid()?"PASS":"FAIL",name);
  if(!tex.isValid()) return;
  Screen.DrawTexture(tex,true,4+(i%40)*38,4+(i/40)*38,DTA_DestWidth,34,DTA_DestHeight,34,DTA_LeftOffset,0,DTA_TopOffset,0);
 }
 override void RenderOverlay(RenderEvent e) {
  Screen.Dim(0x804020,1,0,0,Screen.GetWidth(),Screen.GetHeight());
'''
    script+=''.join(f'  Tile("PG{i:06d}",{i});\n' for i in range(len(rows)))
    script+='  if(!Reported) Console.Printf("UTNT_REGRESSION_COMPLETE"); Reported=true;\n }\n}\n'
    with ZipFile(report['backup']) as archive:
        for stage in ('before','after'):
            addon=work/('gallery-'+stage);(addon/'png-test').mkdir(parents=True,exist_ok=True)
            definitions=[]
            for i,row in enumerate(rows):
                data=archive.read(row['path']) if stage=='before' else (ROOT/row['path']).read_bytes()
                (addon/f'png-test/{i}.png').write_bytes(data)
                w,h=row['size'];definitions.append(f'Graphic "PG{i:06d}", {w}, {h} {{ Patch "png-test/{i}.png",0,0 }}')
            (addon/'TEXTURES').write_text('\n'.join(definitions))
            (addon/'MAPINFO').write_text('GameInfo { AddEventHandlers = "UTNTPngGallery" }\n')
            (addon/'ZSCRIPT').write_text(script)
            for filtering in (0,4):
                label=f'png-gallery-{stage}-{filtering}'
                result=run_case(engine,iwad,root=ROOT/'tutnt/.codex',mod=package,addon=addon,mapname='INTERMAP',
                    label=label,timeout=90,regression=True,settings=[('con_notifytime',0),('screenblocks',12),('vid_maxfps',60),('gl_texture_filter',filtering)],
                    commands=f'vid_setsize 1600 800; wait 180; screenshot logs/{label}.png; echo UTNT_TEST_END; wait 5; quit\n')
                results.append(result)
                if not result['ok'] or result['assertions']!=len(rows):raise RuntimeError(result)
                screens.append(ROOT/f'tutnt/.codex/logs/{label}.png')
    differences=[]
    for i in range(2):
        a,b=[Image.open(screens[j]).convert('RGB') for j in (i,i+2)]
        if a.size!=b.size or a.size!=(1600,800):raise ValueError('Gallery resolution mismatch')
        av,bv=a.tobytes(),b.tobytes();differences.append(sum(av[j:j+3]!=bv[j:j+3] for j in range(0,len(av),3)))
    evidence={'resources':[r['path'] for r in rows],'count':len(rows),'changed_pixels_nearest_linear':differences,'runtime':results}
    (ROOT/'tutnt/.codex/validation/png-optimization-runtime.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({'resources':len(rows),'changed_pixels':differences}))
    if any(differences):raise ValueError('PNG appearance changed')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report',type=Path,required=True);p.add_argument('--package',type=Path,required=True)
    p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'))
    run(**vars(p.parse_args()))
